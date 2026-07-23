import time
import os
import sys
import urllib.parse
import webbrowser
import pandas as pd
from gerenciar_crm import carregar_crm, salvar_e_publicar_crm

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def limpar_teclado_stdin():
    if sys.platform == "win32":
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except Exception:
            pass

def disparar_mensagens_automaticas(csv_path, max_leads=12):
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo de planilha não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    leads_quentes = df[
        (df['tem_site'].str.contains('SEM SITE|FORA DO AR|QUEBRADO', na=False)) & 
        (df['whatsapp_limpo'].notna())
    ]
    
    if leads_quentes.empty:
        print("⚠️ Nenhum lead sem site com WhatsApp válido encontrado nesta planilha.")
        return

    leads_selecionados = leads_quentes.head(max_leads)
    
    print("=" * 65)
    print("🚀 DISPARADOR AUTOMÁTICO DE WHATSAPP - WEBFY (JOÃO)")
    print("=" * 65)
    print(f"🎯 Selecionamos os {len(leads_selecionados)} melhores leads sem site/fora do ar:\n")
    
    for idx, row in leads_selecionados.iterrows():
        print(f" • {row['nome']} | Tel: {row['whatsapp_limpo']} | Status: {row['tem_site']}")
        
    print("\n" + "=" * 65)
    
    resposta = ""
    while resposta not in ['s', 'sim', 'y', 'yes', 'n', 'nao', 'não']:
        limpar_teclado_stdin()
        resposta = input(f"❓ Deseja iniciar o disparo da 1ª Mensagem para esses {len(leads_selecionados)} leads? (Digite 's' para SIM ou 'n' para NÃO): ").strip().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada por você. Nenhum disparo foi realizado.")
        return

    print("\n🚀 Iniciando disparos automáticos no WhatsApp Web...")
    print("⚠️ DICA: Mantenha o WhatsApp Web aberto e conectado no seu navegador!\n")

    df_crm = carregar_crm()

    for i, (_, row) in enumerate(leads_selecionados.iterrows(), 1):
        nome = row['nome']
        cidade = row.get('cidade', 'Geral')
        nicho = os.path.basename(csv_path).replace('leads_', '').split('_')[0].capitalize()
        phone = str(row['whatsapp_limpo']).replace('.0', '')
        msg1 = row['mensagem_1_inicial']
        
        encoded_msg = urllib.parse.quote(msg1)
        wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        
        print(f"[{i}/{len(leads_selecionados)}] 💬 Abrindo conversa e enviando para: {nome} ({phone})...")
        
        webbrowser.open(wa_url)
        
        if nome not in df_crm['nome'].values:
            new_id = len(df_crm) + 1
            new_row = {
                "id": new_id, "nome": nome, "cidade": cidade, "nicho": nicho,
                "telefone": phone, "status_site": "SEM SITE",
                "status_resposta": "AGUARDANDO RESPOSTA (MSG ENVIADA 📩)", "valor_faturado": 0.0
            }
            df_crm = pd.concat([df_crm, pd.DataFrame([new_row])], ignore_index=True)
        
        print("⏳ Aguardando 10 segundos antes do próximo envio (Proteção anti-bloqueio)...")
        time.sleep(10)

    salvar_e_publicar_crm(df_crm)

    print("\n✅ TODOS OS DISPAROS FORAM CONCLUÍDOS E REGISTRADOS COMO ENVIADOS NO CRM!")
    print("💡 Fique atento ao WhatsApp Web para responder os clientes que disserem 'SIM' com a 2ª Mensagem!")

def main():
    print("🤖 GERENCIADOR DE DISPAROS WEBFY")
    planilha = input("👉 Digite o nome da planilha (ex: leads_barbearia_curitiba.csv): ").strip()
    if not planilha.endswith('.csv'):
        planilha += '.csv'
    disparar_mensagens_automaticas(planilha, max_leads=12)

if __name__ == "__main__":
    main()
