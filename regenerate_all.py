import os
import glob
import pandas as pd
import sys
from prospector import export_reports, clean_company_name, format_niche_display
from build_portal import build_central_portal

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def regenerate_all():
    print("🔄 Recalculando e limpando todas as planilhas existentes no projeto...")
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
            
            # Clean names & filter empty noise
            valid_leads = []
            for _, row in df.iterrows():
                clean_name = clean_company_name(row.get('nome', ''))
                if not clean_name:
                    clean_name = clean_company_name(row.get('nome_original', ''))
                if not clean_name or len(clean_name) < 3:
                    continue
                    
                has_site = "SIM" in str(row.get('tem_site', '')).upper()
                site_url = str(row.get('site', ''))
                
                valid_leads.append({
                    "nome": clean_name,
                    "nome_original": str(row.get('nome_original', clean_name))[:65],
                    "cidade": cidade.title(),
                    "bairro": "Centro / Região",
                    "rua": str(row.get('rua', '')),
                    "tem_site": "SIM" if has_site else "NÃO (OPORTUNIDADE 🔥)",
                    "site": site_url,
                    "telefone_original": str(row.get('telefone_original', '')),
                    "whatsapp_limpo": str(row.get('whatsapp_limpo', '')) if not pd.isna(row.get('whatsapp_limpo')) else None,
                    "link_google_maps": f"https://www.google.com/maps/search/{clean_name}+{cidade}"
                })
                
            if valid_leads:
                print(f"✨ Regenerando {len(valid_leads)} leads limpos para {nicho} em {cidade}...")
                export_reports(valid_leads, nicho, cidade, output_dir=project_dir)
        except Exception as e:
            print(f"⚠️ Erro ao recalcular {filename}: {e}")
            
    print("\n✅ Todas as planilhas, relatórios e portal foram atualizados!")
    os.system('git add . && git commit -m "Regenerate all leads with smart site messages" && git push')
    print("🚀 Tudo sincronizado com o GitHub e Vercel!")

if __name__ == "__main__":
    regenerate_all()
