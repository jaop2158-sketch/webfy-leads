import os
import glob
import pandas as pd
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def build_central_portal(project_dir="."):
    print("🌐 Construindo Portal Central da Webfy com Seção de CRM & Funil de Vendas...")
    
    html_files = glob.glob(os.path.join(project_dir, "dashboard_leads_*.html"))
    
    reports = []
    total_leads_all = 0
    total_quentes_all = 0
    
    for f in html_files:
        filename = os.path.basename(f)
        core = filename.replace("dashboard_leads_", "").replace(".html", "")
        parts = core.split("_")
        nicho = parts[0].capitalize()
        cidade = " ".join(parts[1:]).capitalize() if len(parts) > 1 else "Geral"
        
        csv_corresponding = os.path.join(project_dir, f"leads_{core}.csv")
        count = 0
        quentes = 0
        if os.path.exists(csv_corresponding):
            try:
                df = pd.read_csv(csv_corresponding)
                count = len(df)
                total_leads_all += count
                if 'tem_site' in df.columns:
                    quentes = len(df[df['tem_site'].str.contains('SEM SITE|FORA DO AR|QUEBRADO', na=False)])
                    total_quentes_all += quentes
            except Exception:
                pass
                
        reports.append({
            "nicho": nicho,
            "cidade": cidade,
            "html_file": filename,
            "csv_file": f"leads_{core}.csv",
            "count": count,
            "quentes": quentes
        })
        
    reports_sorted = sorted(reports, key=lambda x: (x['cidade'], x['nicho']))
    
    cards_html = ""
    for rep in reports_sorted:
        cards_html += f"""
        <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 4px solid #0284c7; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase;">📍 {rep['cidade']}</span>
                <h2 style="margin: 12px 0 6px 0; color: #0f172a; font-size: 20px;">{rep['nicho']}</h2>
                <p style="color: #64748b; font-size: 14px; margin: 0 0 15px 0;"><strong>{rep['count']}</strong> empresas encontradas</p>
                
                <div style="background: #fef2f2; border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 4px; margin-bottom: 15px;">
                    <span style="color: #991b1b; font-size: 12px; font-weight: bold;">🔥 {rep['quentes']} Oportunidades Sem Site / Fora do Ar</span>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <a href="{rep['html_file']}" target="_blank" style="flex: 1; background: #0284c7; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📊 Abrir Painel HTML</a>
                <a href="{rep['csv_file']}" download style="background: #f1f5f9; color: #334155; text-align: center; padding: 10px 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📥 CSV</a>
            </div>
        </div>
        """
        
    # Verificar se o arquivo CRM existe para exibir os contadores
    crm_file_path = os.path.join(project_dir, "crm_vendas_master.csv")
    crm_sim = 0
    crm_nao = 0
    crm_fechados = 0
    crm_faturado = 0.0
    
    if os.path.exists(crm_file_path):
        try:
            df_crm = pd.read_csv(crm_file_path)
            crm_sim = len(df_crm[df_crm['status_resposta'] == 'RESPONDEU SIM (INTERESSADO 🔥)'])
            crm_nao = len(df_crm[df_crm['status_resposta'] == 'RESPONDEU NÃO'])
            crm_fechados = len(df_crm[df_crm['status_resposta'] == 'CLIENTE FECHADO 💰'])
            crm_faturado = df_crm['valor_faturado'].sum() if 'valor_faturado' in df_crm.columns else 0.0
        except Exception:
            pass

    portal_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webfy - Portal Central de Relatórios & CRM (João)</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; color: #0f172a; }}
            .header {{ background: linear-gradient(135deg, #0284c7, #0369a1); color: white; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 32px; font-weight: 800; }}
            .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
            .container {{ max-width: 1250px; margin: -30px auto 40px auto; padding: 0 20px; }}
            .stats-bar {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); display: flex; gap: 20px; margin-bottom: 30px; }}
            .stat-box {{ flex: 1; text-align: center; border-right: 1px solid #e2e8f0; }}
            .stat-box:last-child {{ border-right: none; }}
            .stat-box h4 {{ margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; }}
            .stat-box p {{ margin: 5px 0 0 0; font-size: 26px; font-weight: bold; color: #0284c7; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
            .crm-banner {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 20px; border-radius: 12px; margin-bottom: 30px; display: flex; align-items: center; justify-content: space-between; }}
            .crm-banner a {{ background: white; color: #059669; padding: 10px 20px; border-radius: 8px; font-weight: bold; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Webfy - Agência de Sites (João)</h1>
            <p>Portal Central de Prospecção Automatizada, Pesquisas do Google Maps & Funil de Respostas</p>
        </div>

        <div class="container">
            <div class="stats-bar">
                <div class="stat-box">
                    <h4>Cidades & Categorias</h4>
                    <p>{len(reports)}</p>
                </div>
                <div class="stat-box">
                    <h4>Total de Leads</h4>
                    <p>{total_leads_all}</p>
                </div>
                <div class="stat-box">
                    <h4>Oportunidades Quentes 🔥</h4>
                    <p style="color: #ef4444;">{total_quentes_all}</p>
                </div>
                <div class="stat-box">
                    <h4>Clientes Fechados 💰</h4>
                    <p style="color: #10b981;">{crm_fechados}</p>
                </div>
                <div class="stat-box">
                    <h4>Faturamento Total 💵</h4>
                    <p style="color: #059669;">R$ {crm_faturado:,.2f}</p>
                </div>
            </div>

            <div class="crm-banner">
                <div>
                    <h2 style="margin: 0 0 5px 0; font-size: 20px;">📊 Funil de Respostas & CRM de Vendas</h2>
                    <p style="margin: 0; opacity: 0.9; font-size: 14px;">Respondeu SIM: <strong>{crm_sim}</strong> | Respondeu NÃO: <strong>{crm_nao}</strong> | Clientes Fechados: <strong>{crm_fechados}</strong></p>
                </div>
                <a href="crm_vendas.html" target="_blank">📊 Abrir Relatório de Respostas CRM</a>
            </div>

            <h2 style="color: #1e293b; font-size: 22px; margin-bottom: 15px;">📁 Pesquisas de Leads por Cidade e Categoria:</h2>
            <div class="grid">
                {cards_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    portal_file = os.path.join(project_dir, "index.html")
    with open(portal_file, "w", encoding="utf-8") as f:
        f.write(portal_html)
    print(f"✅ Portal Central 'index.html' gerado com sucesso: {portal_file}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_central_portal(script_dir)
