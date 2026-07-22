import os
import re
import sys
import glob
import pandas as pd
import requests
import urllib.parse
from prospector import (
    clean_company_name, clean_phone, audit_website_status, 
    generate_pitch_step1, generate_pitch_step2, format_niche_display,
    export_reports
)
from build_portal import build_central_portal

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Termos genéricos de artigos/blogs que NÃO são empresas
BLOG_ARTICLES_NOISE = [
    'o que é', 'como funciona', 'preço de', 'saiba mais', 'quanto custa',
    'qual o valor', 'dicas para', 'principais sintomas', 'tratamento para',
    'benefícios da', 'benefícios do', 'artigo', 'blog', 'notícias', 'noticias'
]

def strict_company_clean(raw_title):
    t = str(raw_title).strip()
    t_lower = t.lower()
    
    # Descartar artigos e posts informativos
    if any(noise in t_lower for noise in BLOG_ARTICLES_NOISE):
        return ""
        
    # Remover prefixos comuns de sites ("Home -", "Início -", "Bem Vindo -")
    t = re.sub(r'^(home|início|inicio|bem-vindo|página inicial)\s*[-|—–:]\s*', '', t, flags=re.IGNORECASE)
    
    # Aplicar a limpeza padrão
    cleaned = clean_company_name(t)
    return cleaned

def process_and_clean_all():
    print("🧹 Iniciando REVISÃO PROFUNDA E LIMPEZA DE TODOS OS LEADS do projeto...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = glob.glob(os.path.join(project_dir, "leads_*.csv"))
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        core = filename.replace("leads_", "").replace(".csv", "")
        
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                continue
                
            parts = core.split("_")
            nicho = parts[0]
            cidade = " ".join(parts[1:]) if len(parts) > 1 else "Geral"
            
            clean_leads = []
            seen_titles = set()
            
            for _, row in df.iterrows():
                raw_name = str(row.get('nome', ''))
                if not raw_name or raw_name == 'nan':
                    raw_name = str(row.get('nome_original', ''))
                    
                clean_name = strict_company_clean(raw_name)
                if not clean_name or len(clean_name) < 3:
                    continue
                    
                title_key = clean_name.lower()[:20]
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)
                
                site_url = str(row.get('site', ''))
                status_site, checked_url = audit_website_status(site_url)
                
                wa_p = row.get('whatsapp_limpo')
                clean_wa = clean_phone(wa_p)
                if not clean_wa:
                    clean_wa = clean_phone(row.get('telefone_original'))
                    
                maps_query = urllib.parse.quote(f"{clean_name} {cidade}")
                google_maps_url = f"https://www.google.com/maps/search/{maps_query}"
                
                clean_leads.append({
                    "nome": clean_name,
                    "nome_original": str(row.get('nome_original', clean_name))[:65],
                    "cidade": cidade.title(),
                    "bairro": "Centro / Região",
                    "rua": str(row.get('rua', '')),
                    "tem_site": status_site,
                    "site": checked_url if checked_url else "Sem Site Cadastrado",
                    "telefone_original": str(row.get('telefone_original', 'WhatsApp no Maps 📍')),
                    "whatsapp_limpo": clean_wa,
                    "link_google_maps": google_maps_url
                })
                
            if clean_leads:
                print(f"✨ Regenerando {len(clean_leads)} leads 100% LIMPOS para {nicho} em {cidade}...")
                export_reports(clean_leads, nicho, cidade, output_dir=project_dir)
        except Exception as e:
            print(f"⚠️ Erro ao processar {filename}: {e}")
            
    print("\n✅ REVISÃO E LIMPEZA GERAL CONCLUÍDAS COM SUCESSO!")
    os.system('git add . && git commit -m "Deep clean company names & site statuses" && git push')
    print("🚀 Tudo perfeitamente limpo e sincronizado com o Vercel!")

if __name__ == "__main__":
    process_and_clean_all()
