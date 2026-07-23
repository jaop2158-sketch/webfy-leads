import os
import sys
import pandas as pd
from build_portal import build_central_portal

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CRM_FILE = "crm_vendas_master.csv"

def carregar_crm():
    if os.path.exists(CRM_FILE):
        return pd.read_csv(CRM_FILE)
    else:
        return pd.DataFrame(columns=[
            "id", "nome", "cidade", "nicho", "telefone", "status_site", "status_resposta", "valor_faturado"
        ])

def salvar_e_publicar_crm(df):
    df.to_csv(CRM_FILE, index=False, encoding='utf-8-sig')
    print("✅ CRM atualizado com sucesso!")
    
    # Gerar HTML do CRM
    gerar_html_crm(df)
    
    # Atualizar o Portal Central e Vercel
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        build_central_portal(script_dir)
        os.system('git add . && git commit -m "Update CRM Sales Pipeline" && git push')
        print("🚀 Relatório de Vendas atualizado no Vercel no ar!")
    except Exception as e:
        print(f"⚠️ Aviso ao sincronizar com Vercel: {e}")

def gerar_html_crm(df):
    total_contatados = len(df)
    interessados_sim = len(df[df['status_resposta'] == 'RESPONDEU SIM (INTERESSADO 🔥)'])
    recusados_nao = len(df[df['status_resposta'] == 'RESPONDEU NÃO'])
    fechados = len(df[df['status_resposta'] == 'CLIENTE FECHADO 💰'])
    total_faturado = df['valor_faturado'].sum() if 'valor_faturado' in df.columns else 0

    rows_html = ""
    for idx, row in df.iterrows():
        st = str(row['status_resposta'])
        if "FECHADO" in st:
            badge = '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">CLIENTE FECHADO 💰</span>'
        elif "SIM" in st:
            badge = '<span style="background: #3b82f6; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">RESPONDEU SIM 🔥</span>'
        elif "NÃO" in st:
            badge = '<span style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">RESPONDEU NÃO</span>'
        else:
            badge = '<span style="background: #f59e0b; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">AGUARDANDO RESPOSTA ⏳</span>'
            
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; font-weight: bold; color: #1f2937;">{row['nome']}</td>
            <td style="padding: 12px;">{row['cidade']}</td>
            <td style="padding: 12px;">{row['nicho']}</td>
            <td style="padding: 12px;">{row['telefone']}</td>
            <td style="padding: 12px;">{badge}</td>
            <td style="padding: 12px; font-weight: bold; color: #166534;">R$ {row.get('valor_faturado', 0):,.2f}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRM Webfy - Relatório de Respostas WhatsApp (João)</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; color: #111827; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            h1 {{ color: #0284c7; margin-top: 0; }}
            .stats {{ display: flex; gap: 15px; margin-bottom: 20px; }}
            .card {{ background: #f8fafc; padding: 15px 20px; border-radius: 8px; flex: 1; border-left: 4px solid #0284c7; }}
            .card h3 {{ margin: 0; font-size: 13px; color: #64748b; text-transform: uppercase; }}
            .card p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #0f172a; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background: #f8fafc; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 13px; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Webfy - Funil de Vendas & Respostas do WhatsApp (João)</h1>
            <p>Acompanhamento dos clientes contatados, interessados e faturamento de hospedagens.</p>

            <div class="stats">
                <div class="card">
                    <h3>Disparos Realizados</h3>
                    <p>{total_contatados}</p>
                </div>
                <div class="card" style="border-left-color: #3b82f6;">
                    <h3>Respondeu SIM 🔥</h3>
                    <p style="color: #1d4ed8;">{interessados_sim}</p>
                </div>
                <div class="card" style="border-left-color: #ef4444;">
                    <h3>Respondeu NÃO</h3>
                    <p style="color: #b91c1c;">{recusados_nao}</p>
                </div>
                <div class="card" style="border-left-color: #10b981; background: #f0fdf4;">
                    <h3 style="color: #15803d;">Clientes Fechados 💰</h3>
                    <p style="color: #166534;">{fechados}</p>
                </div>
                <div class="card" style="border-left-color: #8b5cf6; background: #f5f3ff;">
                    <h3 style="color: #6d28d9;">Faturamento Total 💵</h3>
                    <p style="color: #5b21b6;">R$ {total_faturado:,.2f}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Nome da Empresa</th>
                        <th>Cidade</th>
                        <th>Nicho</th>
                        <th>Telefone / WhatsApp</th>
                        <th>Status no Funil</th>
                        <th>Valor Faturado</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="6" style="padding: 20px; text-align: center; color: #6b7280;">Nenhum lead registrado no funil ainda. Use gerenciar_crm.py para registrar!</td></tr>'}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    with open("crm_vendas.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def menu_crm():
    df = carregar_crm()
    print("=" * 60)
    print("📊 WEBFY CRM - GERENCIADOR DE FUNIL & RESPOSTAS WHATSAPP")
    print("=" * 60)
    print("1 - Registrar Lead Contatado (Aguardando Resposta)")
    print("2 - Marcar Lead como RESPONDEU SIM (Interessado 🔥)")
    print("3 - Marcar Lead como RESPONDEU NÃO")
    print("4 - Marcar Lead como CLIENTE FECHADO (💰 Venda de R$ 599)")
    print("5 - Ver Relatório de Desempenho")
    print("=" * 60)
    
    op = input("\n👉 Escolha uma opção (1 a 5): ").strip()
    
    if op == '1':
        nome = input("👉 Nome da Empresa/Lead: ").strip()
        cidade = input("👉 Cidade: ").strip()
        nicho = input("👉 Nicho: ").strip()
        tel = input("👉 WhatsApp: ").strip()
        
        new_id = len(df) + 1
        new_row = {
            "id": new_id, "nome": nome, "cidade": cidade.title(), "nicho": nicho.capitalize(),
            "telefone": tel, "status_site": "SEM SITE",
            "status_resposta": "AGUARDANDO RESPOSTA ⏳", "valor_faturado": 0.0
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        salvar_e_publicar_crm(df)
        
    elif op in ['2', '3', '4']:
        if df.empty:
            print("⚠️ Nenhum lead cadastrado no CRM ainda.")
            return
            
        print("\n📋 LEADS CADASTRADOS:")
        for idx, row in df.iterrows():
            print(f"[{row['id']}] {row['nome']} ({row['cidade']}) - Status Atual: {row['status_resposta']}")
            
        lead_id = input("\n👉 Digite o ID do lead para atualizar: ").strip()
        try:
            lead_id = int(lead_id)
            if lead_id in df['id'].values:
                if op == '2':
                    df.loc[df['id'] == lead_id, 'status_resposta'] = "RESPONDEU SIM (INTERESSADO 🔥)"
                elif op == '3':
                    df.loc[df['id'] == lead_id, 'status_resposta'] = "RESPONDEU NÃO"
                elif op == '4':
                    df.loc[df['id'] == lead_id, 'status_resposta'] = "CLIENTE FECHADO 💰"
                    df.loc[df['id'] == lead_id, 'valor_faturado'] = 599.00
                    
                salvar_e_publicar_crm(df)
            else:
                print("❌ ID de lead inválido.")
        except Exception as e:
            print(f"❌ Erro ao atualizar: {e}")
            
    elif op == '5':
        gerar_html_crm(df)
        print(f"\n📊 Total Contatados: {len(df)}")
        print(f"🔥 Respondeu SIM: {len(df[df['status_resposta'] == 'RESPONDEU SIM (INTERESSADO 🔥)'])}")
        print(f"💰 Clientes Fechados: {len(df[df['status_resposta'] == 'CLIENTE FECHADO 💰'])}")
        print(f"💵 Faturamento Total: R$ {df['valor_faturado'].sum():,.2f}")

if __name__ == "__main__":
    menu_crm()
