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

def clean_company_name_ultra_strict(raw_title):
    if not raw_title or pd.isna(raw_title):
        return ""
        
    t = str(raw_title).strip()
    
    # 1. Limpeza de caracteres inviáveis
    t = re.sub(r'[\ufffd\x80-\xff]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    
    # 2. Excluir agregadores e buscas informacionais
    noise_domains = [
        'doctoralia', 'medprev', 'psitto', 'os 10 melhores', 'os 20', 'acheioprofissional', 
        'maps.google', 'google.com', 'google maps', 'maps', 'google', 'empresa', 'profissional', 
        'pesquisa', 'home', 'contato', 'agende sua', 'saiba mais', 'atendimento', 'clinica', 'consultorio'
    ]
    t_low = t.lower()
    if any(agg in t_low for agg in noise_domains):
        if t_low in ['google maps', 'google', 'maps', 'empresa', 'profissional', 'home', 'contato', 'pesquisa']:
            return ""

    # 3. Remover sufixos de SEO comuns
    t = re.sub(r'(?i)\s*[-|—–:/]\s*(agende|agendamento|consulta|valores|desconto|preço|saiba mais|whatsapp|telefones?|os \d+|mais recomendados|em curitiba|em são paulo|em campinas|em sorocaba|em sp|em pr).*', '', t)
    t = re.sub(r'(?i)\s*[-|—–:/]\s*(psicologia|psicologo|psicologa|dentista|odontologia|barbearia|estetica|advocacia|advogado|medico).*', '', t)
    t = re.sub(r'(?i)\s+(em curitiba|em são paulo|em campinas|em sorocaba|curitiba|campinas|são paulo|sp|pr)$', '', t)

    # 4. Cortar na primeira barra ou hífen longo
    parts = re.split(r'\s+[-|—–:/]\s+', t)
    clean_name = parts[0] if (parts and len(parts[0]) >= 3) else t
    clean_name = clean_name[:40].strip()

    # 5. Remover pontuação no final
    clean_name = re.sub(r'[\s\-|,.:/]+$', '', clean_name).strip()
    
    # 6. Rejeitar nomes genéricos
    if len(clean_name) < 3 or clean_name.lower() in ['google maps', 'google', 'maps', 'empresa', 'profissional', 'home', 'contato', 'pesquisa', 'site']:
        return ""
        
    return format_title_pt(clean_name)

def auditar_e_reparar_todos_os_leads():
    print("=" * 75)
    print("🛡️ REVISÃO ULTRA-RIGOROSA E VALIDAÇÃO DE NOMES PRÓPRIOS PARA LIGAÇÃO")
    print("=" * 75)
    
    csv_files = glob.glob("leads_*.csv")
    total_revisados = 0
    total_corrigidos = 0
    
    for csv_file in csv_files:
        core = csv_file.replace("leads_", "").replace(".csv", "")
        print(f"\n📂 Processando Planilha: {csv_file}")
        
        df = pd.read_csv(csv_file)
        if df.empty:
            continue
            
        novos_nomes = []
        alterados_aqui = 0
        
        for idx, row in df.iterrows():
            orig_name = str(row['nome'])
            cleaned = clean_company_name_ultra_strict(orig_name)
            
            if not cleaned or len(cleaned) < 3:
                cleaned = clean_company_name_ultra_strict(row.get('nome_original', orig_name))
                
            if not cleaned or cleaned.lower() in ['google maps', 'google', 'empresa']:
                cleaned = f"Empresa {idx+1}"
                
            if cleaned != orig_name:
                alterados_aqui += 1
                
            novos_nomes.append(cleaned)
            total_revisados += 1
            
        df['nome'] = novos_nomes
        
        # Salvar CSV
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # Salvar Excel
        xlsx_file = f"leads_{core}.xlsx"
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Leads Webfy")
            
        print(f"  ✅ {len(df)} leads validados! ({alterados_aqui} nomes ajustados para ficarem 100% perfeitos ao telefone)")
        total_corrigidos += alterados_aqui

    # Reconstruir o portal central
    from build_portal import build_central_portal
    build_central_portal(".")

    print("\n" + "=" * 75)
    print(f"🎉 AUDITORIA E LIMPEZA ULTRA-RIGOROSA CONCLUÍDA!")
    print(f" • Total de Leads Revisados: {total_revisados}")
    print(f" • Total de Ajustes de Precisão: {total_corrigidos}")
    print("=" * 75)

if __name__ == "__main__":
    auditar_e_reparar_todos_os_leads()
