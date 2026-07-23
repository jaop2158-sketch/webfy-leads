import sys
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def menu_respostas():
    print("=" * 60)
    print("💬 WEBFY - GERENCIADOR DE RESPOSTAS RÁPIDAS DE FECHAMENTO")
    print("=" * 60)
    print("1 - Cliente respondeu SIM / PODE SIM (Enviar oferta R$ 0 criação / R$ 599 hospedagem)")
    print("2 - Cliente respondeu NÃO / AGORA NÃO (Enviar contorno educado)")
    print("3 - Cliente perguntou QUAL O VALOR / COMO FUNCIONA")
    print("=" * 60)
    
    opcao = input("\n👉 Escolha a opção (1, 2 ou 3): ").strip()
    
    if opcao == '1':
        print("\n✅ MENSAGEM 2 DE FECHAMENTO (Copie e envie no WhatsApp):\n")
        msg = (
            "É que vi que vocês ainda não têm um site próprio para celular e estão perdendo clientes do Google todos os dias para a concorrência.\n\n"
            "Um site desse nível no mercado custa entre R$ 2.000 e R$ 3.000, mas nós da Webfy estamos com uma ação de portfólio onde a criação e mão de obra saem 100% DE GRAÇA. 🚀\n\n"
            "Você não paga nada pela criação. A única coisa necessária é a taxa de hospedagem de R$ 599/ano (ou em até 12x) para o site ficar online no seu nome com domínio próprio.\n\n"
            "Já deixei uma prévia demonstrativa do site de vocês pronta. Posso te mandar o link para você dar uma olhada sem compromisso?"
        )
        print(msg)
    elif opcao == '2':
        print("\n⚠️ MENSAGEM DE CONTORNO PARA 'NÃO' (Copie e envie no WhatsApp):\n")
        msg = (
            "Sem problemas! Entendo perfeitamente. 🎯\n\n"
            "Caso no futuro vocês decidam atualizar a presença online de vocês no Google ou precisarem de um site moderno que converte mais clientes no celular, pode me chamar por aqui!\n\n"
            "Vou deixar meu contato salvo. Desejo muito sucesso nos negócios! 👍"
        )
        print(msg)
    elif opcao == '3':
        print("\n💰 MENSAGEM EXPLICANDO VALORES (Copie e envie no WhatsApp):\n")
        msg = (
            "A criação do design e desenvolvimento saem 100% GRATUITOS na nossa ação de portfólio deste mês. 🎁\n\n"
            "O único investimento é a hospedagem e manutenção anual do site no ar (R$ 599/ano que pode parcelar no cartão).\n\n"
            "Incluso: Registro de domínio (.com.br), servidor super rápido para celular, botão de WhatsApp integrado e otimização no Google!\n\n"
            "Quer dar uma olhada na demonstração que fiz pra vocês?"
        )
        print(msg)

if __name__ == "__main__":
    menu_respostas()
