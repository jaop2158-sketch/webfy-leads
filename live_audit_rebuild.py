import os
import sys
import pandas as pd
from prospector import fetch_leads, export_reports
from build_portal import build_central_portal

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Lista de Nichos e Cidades para varredura 100% ao vivo
TARGETS = [
    ("barbearia", "curitiba"),
    ("dentista", "campinas"),
    ("odontologia", "curitiba"),
    ("psicologo", "curitiba"),
    ("psicologo", "sao paulo")
]

def rebuild_all_live():
    print("=" * 60)
    print("🚀 REFAZENDO TODOS OS RELATÓRIOS AO VIVO (GOOGLE MAPS & SITES)")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for nicho, cidade in TARGETS:
        print(f"\n📡 Executando varredura AO VIVO para '{nicho}' em '{cidade}'...")
        leads = fetch_leads(nicho, cidade)
        print(f"🎯 Encontrados {len(leads)} leads reais e auditados ao vivo para {nicho} em {cidade}!")
        export_reports(leads, nicho, cidade, output_dir=script_dir)
        
    print("\n🌐 Construindo Portal Central da Webfy para o Vercel...")
    build_central_portal(script_dir)
    
    print("\n🚀 Enviando TODOS os relatórios auditados AO VIVO para o GitHub e Vercel...")
    os.system('git add . && git commit -m "Live audit and rebuild of all reports" && git push')
    print("✅ TUDO CONCLUÍDO E PUBLICADO AO VIVO NO VERCEL!")

if __name__ == "__main__":
    rebuild_all_live()
