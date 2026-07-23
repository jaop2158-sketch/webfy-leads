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

def auditoria_completa_site(project_dir="."):
    print("=" * 70)
    print("🔍 AUDITORIA GLOBAL E REVISÃO TOTAL DO SITE WEBFY")
    print("=" * 70)
    
    erros_encontrados = 0
    sucessos = 0
    
    # 1. Verificar vercel.json
    vercel_path = os.path.join(project_dir, "vercel.json")
    if os.path.exists(vercel_path):
        with open(vercel_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "builds" in content:
                print("❌ [vercel.json] Encontrada restrição de builds! Corrigindo...")
                with open(vercel_path, "w", encoding="utf-8") as f_out:
                    f_out.write('{\n  "version": 2\n}\n')
                print("✅ [vercel.json] Corrigido para permitir todos os tipos de arquivo!")
            else:
                print("✅ [vercel.json] Configuração de downloads estáticos OK!")
                sucessos += 1
                
    # 2. Verificar crm_vendas.html
    crm_html_path = os.path.join(project_dir, "crm_vendas.html")
    if not os.path.exists(crm_html_path):
        print("❌ [crm_vendas.html] Arquivo não encontrado! Gerando...")
        from gerenciar_crm import carregar_crm, gerar_html_crm
        df_crm = carregar_crm()
        gerar_html_crm(df_crm)
        print("✅ [crm_vendas.html] Gerado com sucesso!")
    else:
        print("✅ [crm_vendas.html] Arquivo de CRM do funil OK!")
        sucessos += 1

    # 3. Auditando todas as categorias e dashboards
    dashboards = glob.glob(os.path.join(project_dir, "dashboard_leads_*.html"))
    print(f"\n📂 Encontrados {len(dashboards)} relatórios de categorias para verificação profunda:")
    
    for dash_path in dashboards:
        filename = os.path.basename(dash_path)
        core = filename.replace("dashboard_leads_", "").replace(".html", "")
        
        xlsx_file = os.path.join(project_dir, f"leads_{core}.xlsx")
        pptx_file = os.path.join(project_dir, f"relatorio_{core}.pptx")
        csv_file = os.path.join(project_dir, f"leads_{core}.csv")
        
        print(f"\n📌 Auditando Categoria: '{core}'")
        
        if not os.path.exists(xlsx_file):
            print(f"  ❌ Excel (.xlsx) FALTANDO: leads_{core}.xlsx")
            erros_encontrados += 1
        else:
            print(f"  ✅ Excel (.xlsx) presente: leads_{core}.xlsx ({os.path.getsize(xlsx_file)} bytes)")
            sucessos += 1

        if not os.path.exists(pptx_file):
            print(f"  ❌ PowerPoint (.pptx) FALTANDO: relatorio_{core}.pptx")
            erros_encontrados += 1
        else:
            print(f"  ✅ PowerPoint (.pptx) presente: relatorio_{core}.pptx ({os.path.getsize(pptx_file)} bytes)")
            sucessos += 1

        if not os.path.exists(csv_file):
            print(f"  ❌ CSV (.csv) FALTANDO: leads_{core}.csv")
            erros_encontrados += 1
        else:
            print(f"  ✅ CSV (.csv) presente: leads_{core}.csv")
            sucessos += 1
            
        with open(dash_path, "r", encoding="utf-8") as f:
            html_text = f.read()
            
            if re.search(r'<td>\s*(Google Maps|Maps|Google|Empresa|Home|Contato)\s*</td>', html_text, re.IGNORECASE):
                print(f"  ⚠️ Alerta de nome genérico em '{filename}'!")
                erros_encontrados += 1
            else:
                print(f"  ✅ Nomes das empresas auditados e limpos em '{filename}'!")
                sucessos += 1
                
            if "Buscar no Maps" in html_text or "WhatsApp no Maps" in html_text or "Buscar no Google" in html_text:
                print(f"  ⚠️ Alerta de texto de busca em telefone em '{filename}'!")
                erros_encontrados += 1
            else:
                print(f"  ✅ Telefones com números e botões diretos de WhatsApp em '{filename}'!")
                sucessos += 1

    # 4. Verificar index.html (Portal Central)
    index_path = os.path.join(project_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            idx_html = f.read()
            if "crm_vendas.html" in idx_html and ".xlsx" in idx_html and ".pptx" in idx_html:
                print("\n✅ [index.html] Portal Central com todos os links, CRM, Excel e PowerPoint OK!")
                sucessos += 1
            else:
                print("\n❌ [index.html] Portal Central incompleto. Reconstruindo...")
                from build_portal import build_central_portal
                build_central_portal(project_dir)
                print("✅ [index.html] Reconstruído com sucesso!")
                
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO DA REVISÃO GERAL DO SITE:")
    print(f" • Checagens Aprovadas com Sucesso: {sucessos}")
    print(f" • Ajustes/Erros Restantes: {erros_encontrados}")
    print("=" * 70)

if __name__ == "__main__":
    auditoria_completa_site()
