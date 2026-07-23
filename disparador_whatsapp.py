import time
import os
import sys
import urllib.parse
import webbrowser
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def disparar_mensagens_automaticas(csv_path, max_leads=12):
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo de planilha não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # Filtrar leads quentes (sem site ou fora do ar) que possuem WhatsApp válido
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
    resposta = input(f"❓ Deseja iniciar o disparo da 1ª Mensagem para esses {len(leads_selecionados)} leads? (s/n): ").strip().lower()
    
    if resposta != 's':
        print("❌ Operação cancelada por você. Nenhum disparo foi realizado.")
        return

    print("\n🚀 Iniciando disparos automáticos no WhatsApp Web...")
    print("⚠️ DICA: Mantenha o WhatsApp Web aberto e conectado no seu navegador!\n")

    for i, (_, row) in enumerate(leads_selecionados.iterrows(), 1):
        nome = row['nome']
        phone = str(row['whatsapp_limpo']).replace('.0', '')
        msg1 = row['mensagem_1_inicial']
        
        encoded_msg = urllib.parse.quote(msg1)
        wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        
        print(f"[{i}/{len(leads_selecionados)}] 💬 Abrindo conversa e enviando para: {nome} ({phone})...")
        
        # Abre a aba no WhatsApp Web pronta com a mensagem digitada
        webbrowser.open(wa_url)
        
        # Pausa de segurança de 10 segundos entre cada envio para evitar spam/bloqueios no WhatsApp
        print("⏳ Aguardando 10 segundos antes do próximo envio (Proteção anti-bloqueio)...")
        time.sleep(10)

    print("\n✅ TODOS OS DISPAROS FORAM CONCLUÍDOS COM SUCESSO!")
    print("💡 Fique atento ao WhatsApp Web para responder os clientes que disserem 'SIM' com a 2ª Mensagem!")

def main():
    print("🤖 GERENCIADOR DE DISPAROS WEBFY")
    planilha = input("👉 Digite o nome da planilha (ex: leads_barbearia_curitiba.csv): ").strip()
    if not planilha.endswith('.csv'):
        planilha += '.csv'
    disparar_mensagens_automaticas(planilha, max_leads=12)

if __name__ == "__main__":
    main()
