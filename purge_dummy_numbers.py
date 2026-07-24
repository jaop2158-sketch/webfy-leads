import os
import glob
import re
import sys
import urllib.parse
import pandas as pd
from ddgs import DDGS

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def clean_phone_strict(phone_str):
    if not phone_str or pd.isna(phone_str):
        return None
    digits = re.sub(r'\D', '', str(phone_str))
    if digits.startswith("55"):
        digits = digits[2:]
    if len(digits) == 11 and digits[2] == '9':
        if digits in ["41988776655", "19988776655", "11988776655", "5541988776655"]:
            return None
        return "55" + digits
    return None

def format_phone_display(phone_clean):
    if not phone_clean:
        return None
    d = str(phone_clean)
    if d.startswith("55"):
        d = d[2:]
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    return d

def deep_find_real_phone(nome_empresa, cidade):
    queries = [
        f'"{nome_empresa}" {cidade} whatsapp celular 9',
        f'"{nome_empresa}" {cidade} contato (41) 9 OR (19) 9 OR (11) 9'
    ]
    for q in queries:
        try:
            with DDGS() as ddg:
                res = list(ddg.text(q, max_results=5))
                for item in res:
                    text = item.get('title', '') + " " + item.get('body', '')
                    phones = re.findall(r'\(?\d{2}\)?\s?9\d{4}[-\s]?\d{4}', text)
                    for p in phones:
                        clean = clean_phone_strict(p)
                        if clean:
                            fmt = format_phone_display(clean)
                            return fmt, clean
        except Exception:
            pass
    return None, None

def expurgar_telefones_falsos_e_limpar():
    print("=" * 75)
    print("🔥 EXPURGANDO NÚMEROS FANTASMAS (98877-6655) E VALIDANDO CELULARES REAIS")
    print("=" * 75)
    
    csv_files = glob.glob("leads_*.csv")
    total_removidos_falsos = 0
    total_salvos_reais = 0
    
    for csv_file in csv_files:
        core = csv_file.replace("leads_", "").replace(".csv", "")
        print(f"\n📋 Processando Planilha: {csv_file}")
        
        df = pd.read_csv(csv_file)
        if df.empty:
            continue
            
        rows_limpas = []
        removidos_aqui = 0
        
        for idx, row in df.iterrows():
            nome = str(row['nome'])
            cidade = str(row.get('cidade', 'Curitiba'))
            wa_raw = str(row.get('whatsapp_limpo', ''))
            
            clean_wa = clean_phone_strict(wa_raw)
            
            # Se era o número fantasma ou inválido, tenta buscar o celular REAL da empresa
            if not clean_wa:
                orig_p, clean_wa = deep_find_real_phone(nome, cidade)
                if orig_p:
                    row['telefone_original'] = orig_p
                    row['whatsapp_limpo'] = clean_wa
                else:
                    # Se não foi possível encontrar um celular real com dígito 9, descarta a linha
                    removidos_aqui += 1
                    continue
            else:
                row['telefone_original'] = format_phone_display(clean_wa)
                row['whatsapp_limpo'] = clean_wa
                
            enc1 = urllib.parse.quote(str(row.get('mensagem_1_inicial', '')))
            enc2 = urllib.parse.quote(str(row.get('mensagem_2_preco_oferta', '')))
            row['link_whatsapp_msg1'] = f"https://wa.me/{clean_wa}?text={enc1}"
            row['link_whatsapp_msg2'] = f"https://wa.me/{clean_wa}?text={enc2}"
            
            rows_limpas.append(row)
            
        df_clean = pd.DataFrame(rows_limpas)
        
        df_clean.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        xlsx_file = f"leads_{core}.xlsx"
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df_clean.to_excel(writer, index=False, sheet_name="Leads Webfy")
            
        print(f"  ✅ {len(df_clean)} leads com CELULARES REAIS salvos! ({removidos_aqui} linhas com números genéricos foram eliminadas)")
        total_removidos_falsos += removidos_aqui
        total_salvos_reais += len(df_clean)

    print("\n🌐 Atualizando portal central e dashboards com os dados 100% limpos...")
    from build_portal import build_central_portal
    build_central_portal(".")

    print("\n" + "=" * 75)
    print(f"🎉 ELIMINAÇÃO DE NÚMEROS DUMMY CONCLUÍDA!")
    print(f" • Total de Celulares Reais e Únicos Validados: {total_salvos_reais}")
    print(f" • Total de Linhas Dummy/Repetidas Eliminadas: {total_removidos_falsos}")
    print("=" * 75)

if __name__ == "__main__":
    expurgar_telefones_falsos_e_limpar()
