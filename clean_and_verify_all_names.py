import os
import glob
import re
import sys
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PREPOSITIONS = {'de', 'da', 'do', 'dos', 'das', 'e', 'em', 'para', 'com', 'por', 'a', 'o', 'as', 'os'}

def format_title_pt(text):
    if not text:
        return ""
    words = text.split()
    formatted = []
    for i, w in enumerate(words):
        w_lower = w.lower()
        if i > 0 and w_lower in PREPOSITIONS:
            formatted.append(w_lower)
        else:
            formatted.append(w.capitalize())
    return " ".join(formatted)

def clean_company_name_strict(raw_title, nicho="", cidade=""):
    if not raw_title or pd.isna(raw_title):
        return ""
        
    t = str(raw_title).strip()
    
    # Remover caracteres estranhos ou desformatados
    t = re.sub(r'[\ufffd\x80-\xff]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    
    # Excluir agregadores de busca e nomes genéricos
    noise_domains = [
        'doctoralia', 'medprev', 'psitto', 'os 10 melhores', 'os 20', 'acheioprofissional', 
        'maps.google', 'google.com', 'google maps', 'maps', 'google', 'empresa', 'profissional', 
        'pesquisa', 'home', 'contato', 'agende sua', 'saiba mais', 'atendimento', 'clinica', 'consultorio'
    ]
    if any(agg in t.lower() for agg in noise_domains):
        # Se contiver apenas o nome agregador sem o nome próprio
        if t.lower() in ['google maps', 'google', 'maps', 'empresa', 'profissional', 'home', 'contato', 'pesquisa']:
            return ""

    # Remover sufixos de SEO comuns no Google e Google Maps
    t = re.sub(r'(?i)\s*[-|—–:/]\s*(agende|agendamento|consulta|valores|desconto|preço|saiba mais|whatsapp|telefones?|os \d+|mais recomendados|em curitiba|em são paulo|em campinas|em sorocaba|em sp|em pr).*', '', t)
    t = re.sub(r'(?i)\s*[-|—–:/]\s*(psicologia|psicologo|psicologa|dentista|odontologia|barbearia|estetica|advocacia|advogado|medico).*', '', t)
    t = re.sub(r'(?i)\s+(em curitiba|em são paulo|em campinas|em sorocaba|curitiba|campinas|são paulo|sp|pr)$', '', t)

    # Pegar apenas a primeira parte relevante antes de barras ou hífens longos
    parts = re.split(r'\s+[-|—–:/]\s+', t)
    clean_name = parts[0] if (parts and len(parts[0]) >= 3) else t
    clean_name = clean_name[:40].strip()

    # Limpar caracteres de pontuação sobrantes no final
    clean_name = re.sub(r'[\s\-|,.:/]+$', '', clean_name).strip()
    
    # Se o nome ficou muito curto ou virou uma palavra genérica, descartar
    if len(clean_name) < 3 or clean_name.lower() in ['google maps', 'google', 'maps', 'empresa', 'profissional', 'home', 'contato', 'pesquisa', 'site']:
        return ""
        
    return format_title_pt(clean_name)

def revisar_e_corrigir_todas_as_planilhas():
    print("=" * 70)
    print("🧹 REVISÃO PROFUNDA E REPARO DE NOMES PRÓPRIOS EM TODAS AS PLANILHAS")
    print("=" * 70)
    
    csv_files = glob.glob("leads_*.csv")
    reparos_totais = 0
    
    for csv_file in csv_files:
        core = csv_file.replace("leads_", "").replace(".csv", "")
        print(f"\n📋 Revisando nomes na planilha: {csv_file}")
        
        df = pd.read_csv(csv_file)
        if df.empty:
            continue
            
        novos_nomes = []
        alterados = 0
        
        for idx, row in df.iterrows():
            orig_name = str(row['nome'])
            cleaned = clean_company_name_strict(orig_name)
            
            if not cleaned or len(cleaned) < 3:
                cleaned = clean_company_name_strict(row.get('nome_original', orig_name))
                
            if not cleaned:
                cleaned = f"Empresa {idx+1}"
                
            if cleaned != orig_name:
                alterados += 1
                
            novos_nomes.append(cleaned)
            
        df['nome'] = novos_nomes
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # Recriar Excel
        xlsx_file = f"leads_{core}.xlsx"
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Leads Webfy")
            
        print(f"  ✅ {len(df)} nomes validados com sucesso ({alterados} nomes ajustados para perfeição gramatical)!")
        reparos_totais += alterados
        
    print("\n" + "=" * 70)
    print(f"✅ REVISÃO GERAL CONCLUÍDA! Total de {reparos_totais} nomes corrigidos.")
    print("=" * 70)

if __name__ == "__main__":
    revisar_e_corrigir_todas_as_planilhas()
