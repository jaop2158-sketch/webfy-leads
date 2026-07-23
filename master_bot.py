import os
import sys
import time
import urllib.parse
import webbrowser
import pandas as pd
from prospector import fetch_leads, export_reports

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def limpar_teclado_stdin():
    """Limpa o buffer do teclado no Windows para não pular o input()"""
    if sys.platform == "win32":
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except Exception:
            pass

def iniciar_piloto_automatico_total():
    print("=" * 70)
    print("🤖 ROBÔ PILOTO AUTOMÁTICO MASTER - WEBFY (JOÃO)")
    print("=" * 70)
    print("Este robô vai fazer TUDO em sequência:")
    print("1. Buscar empresas reais no Google Maps & Web")
    print("2. Auditar os sites e filtrar as melhores oportunidades (Sem Site / Fora do Ar)")
    print("3. Atualizar o seu portal e publicar no Vercel automaticamente")
    print("4. Disparar a 1ª Mensagem (Criação 100% Grátis) direto no WhatsApp Web!")
    print("=" * 70)
    
    limpar_teclado_stdin()
    pergunta = input("\n❓ Pode iniciar o processo completo de prospecção e disparos? (s/n): ").strip().lower()
    
    if pergunta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Processo cancelado pelo usuário.")
        return

    nicho = input("\n👉 Digite o Nicho (ex: Psicologo, Dentista, Barbearia, Estetica): ").strip()
    cidade = input("👉 Digite a Cidade (ex: Curitiba, Sao Paulo, Campinas): ").strip()
    
    if not nicho or not cidade:
        nicho = "psicologo"
        cidade = "curitiba"
        print(f"ℹ️ Usando nicho e cidade padrão: {nicho} em {cidade}")

    print(f"\n🔍 [ETAPA 1/3] Minerando e auditando empresas de '{nicho}' em '{cidade}'...")
    leads = fetch_leads(nicho, cidade)
    
    if not leads:
        print("❌ Nenhum lead encontrado.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_reports(leads, nicho, cidade, output_dir=script_dir)
    
    df = pd.DataFrame(leads)
    
    # Filtrar leads quentes sem site ou com site fora do ar que possuem WhatsApp
    df_quentes = df[
        (df['tem_site'].str.contains('SEM SITE|FORA DO AR|QUEBRADO', na=False)) &
        (df['whatsapp_limpo'].notna())
    ]
    
    if df_quentes.empty:
        print("⚠️ Todos os leads já possuem site ativo. Buscando leads adicionais...")
        df_quentes = df[df['whatsapp_limpo'].notna()]

    leads_para_disparo = df_quentes.head(10)
    
    print("\n" + "=" * 70)
    print(f"🚀 [ETAPA 2/3] PRONTO PARA DISPARAR PARA OS {len(leads_para_disparo)} MELHORES LEADS:")
    for idx, row in leads_para_disparo.iterrows():
        print(f" • {row['nome']} | Tel: {row['whatsapp_limpo']} | Status: {row['tem_site']}")
    print("=" * 70)
    
    # Limpa o buffer do teclado antes da pergunta para NUNCA pular o input
    confirm_disparo = ""
    while confirm_disparo not in ['s', 'sim', 'y', 'yes', 'n', 'nao', 'não']:
        limpar_teclado_stdin()
        confirm_disparo = input(f"\n❓ Iniciar os disparos de WhatsApp Web agora? (Digite 's' para SIM ou 'n' para NÃO): ").strip().lower()
        if confirm_disparo not in ['s', 'sim', 'y', 'yes', 'n', 'nao', 'não']:
            print("⚠️ Por favor, digite 's' e aperte Enter para SIM, ou 'n' para NÃO.")
    
    if confirm_disparo not in ['s', 'sim', 'y', 'yes']:
        print("❌ Disparos ignorados. Os relatórios já foram salvos e enviados para o Vercel!")
        return

    print("\n🚀 [ETAPA 3/3] Abrindo WhatsApp Web e realizando disparos automáticos...")
    print("⚠️ Mantenha o seu WhatsApp Web logado no navegador!\n")

    for i, (_, row) in enumerate(leads_para_disparo.iterrows(), 1):
        nome = row['nome']
        phone = str(row['whatsapp_limpo']).replace('.0', '')
        
        msg1 = (
            f"Olá, tudo bem? Meu nome é João, sou da agência Webfy. 🚀\n\n"
            f"Vi o perfil da {nome} aí em {cidade.capitalize()} no Google e vi que vocês ainda não têm um site próprio para celular.\n\n"
            f"Nós estamos selecionando 5 empresas na região para **GANHAR A CRIAÇÃO DE UM SITE NOVO 100% GRATUITO** para o nosso portfólio deste mês.\n\n"
            f"Já deixei uma demonstração pronta. Posso te mandar o link para você dar uma olhada sem compromisso?"
        )
        
        encoded_msg = urllib.parse.quote(msg1)
        wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        
        print(f"[{i}/{len(leads_para_disparo)}] 💬 Enviando para: {nome} ({phone})...")
        webbrowser.open(wa_url)
        
        print("⏳ Pausa de segurança de 10 segundos...")
        time.sleep(10)

    print("\n🎉 PROCESSO TOTAL CONCLUÍDO COM SUCESSO!")
    print("💡 Fique de olho no seu WhatsApp Web para responder os clientes que disserem 'SIM'!")

if __name__ == "__main__":
    iniciar_piloto_automatico_total()
