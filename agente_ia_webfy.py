import sys
import os
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Agente de Inteligência Artificial para Atendimento e Vendas Webfy (João)
def agente_ia_responder(nome_empresa, nicho, cidade, mensagem_cliente):
    """
    IA de Atendimento Humano para entender qualquer tipo de resposta do cliente
    e gerar a réplica perfeita da agência Webfy.
    """
    txt = str(mensagem_cliente).lower().strip()
    
    # 1. Intenção: Interesse direto / Pedido de proposta / "Como funciona?"
    if any(k in txt for k in ['interesse', 'proposta', 'como funciona', 'quanto custa', 'qual o valor', 'me manda', 'quero ver', 'explic', 'detalhe', 'pode ser', 'sim']):
        resposta_ia = (
            f"Que bacana! Fico feliz pelo interesse! 🚀\n\n"
            f"Funciona assim: a criação e o desenvolvimento do site novo para a {nome_empresa} saem 100% GRATUITOS (uma economia de R$ 2.000 para o nosso portfólio deste mês).\n\n"
            f"A única coisa necessária é a taxa anual de hospedagem e servidor rápido no celular (R$ 599/ano ou parcelado), que é a taxa padrão que qualquer site precisa ter para ficar online no seu nome com domínio próprio (.com.br).\n\n"
            f"Já deixei uma prévia demonstrativa do site pronta. Posso te mandar o link para você dar uma olhada agora?"
        )
        status_funil = "INTERESSADO 🔥"

    # 2. Intenção: Objeção de Preço / "Tenho que pagar algo?"
    elif any(k in txt for k in ['pagar', 'cobrar', 'de graça', 'gratis', 'gratuito', 'pegadinha', 'custo']):
        resposta_ia = (
            f"Sem pegadinhas! A nossa mão de obra de design e programação é 100% de graça mesmo, pois estamos selecionando 5 empresas aí em {cidade.capitalize()} para divulgar no nosso portfólio. 🎁\n\n"
            f"O único custo é o servidor e a hospedagem anual (R$ 599/ano), que vai direto para manter o seu site no ar com segurança e domínio próprio (.com.br).\n\n"
            f"Quer dar uma olhadinha na prévia que fiz para vocês sem compromisso?"
        )
        status_funil = "DÚVIDA PREÇO 💰"

    # 3. Intenção: Dúvida sobre quem somos / Onde fica a agência
    elif any(k in txt for k in ['onde fica', 'quem são', 'agencia', 'empresa', 'onde voces', 'telefone', 'contato']):
        resposta_ia = (
            f"Nós somos a Webfy, uma agência especializada na criação de sites rápidos e otimizados para celular e Google! 📱🚀\n\n"
            f"Meu nome é João e eu cuido do desenvolvimento de novos projetos aqui na agência. Nós atendemos empresas em toda a região de {cidade.capitalize()}.\n\n"
            f"Posso te mandar o link da prévia do site da {nome_empresa} para você ver a qualidade do nosso trabalho?"
        )
        status_funil = "INSTITUCIONAL 🏢"

    # 4. Intenção: Negativa / "Não tenho interesse" / "Já tenho quem faça"
    elif any(k in txt for k in ['não', 'nao', 'agora nao', 'tenho site', 'obrigado', 'nao quero', 'sem interesse']):
        resposta_ia = (
            f"Sem problemas! Entendo perfeitamente. 🎯\n\n"
            f"Vou deixar meu contato salvo por aqui. Se no futuro vocês precisarem atualizar o site de vocês para celular ou quiserem atrair mais clientes no Google, é só me chamar!\n\n"
            f"Desejo muito sucesso para a {nome_empresa}! Um abraço!"
        )
        status_funil = "RECUSADO 🔴"

    # 5. Intenção Genérica / Outras Respostas Humanas
    else:
        resposta_ia = (
            f"Opa, entendi! Como nós da Webfy estamos com uma ação de portfólio aí em {cidade.capitalize()}, a criação do site para a {nome_empresa} sai 100% gratuita, restando apenas a taxa de hospedagem e domínio (.com.br).\n\n"
            f"Posso te enviar o link da demonstração sem compromisso para você dar uma olhada?"
        )
        status_funil = "ATENDIMENTO IA 🤖"
        
    return resposta_ia, status_funil

def menu_agente_ia():
    print("=" * 65)
    print("🤖 AGENTE DE INTELIGÊNCIA ARTIFICIAL DE VENDAS - WEBFY (JOÃO)")
    print("=" * 65)
    print("Esta IA lê qualquer mensagem humana e gera a resposta perfeita!\n")
    
    empresa = input("👉 Nome da empresa (ex: Barbearia do Zé): ").strip()
    cidade = input("👉 Cidade (ex: Curitiba): ").strip()
    msg_cliente = input("\n💬 Digite o que o cliente falou no WhatsApp: ").strip()
    
    if empresa and msg_cliente:
        resp, status = agente_ia_responder(empresa, "geral", cidade, msg_cliente)
        print("\n" + "=" * 65)
        print(f"🎯 INTENÇÃO DETECTADA PELA IA: {status}")
        print("=" * 65)
        print("💬 MENSAGEM GERADA PELA IA PARA ENVIAR NO WHATSAPP:\n")
        print(resp)
        print("=" * 65)

if __name__ == "__main__":
    menu_agente_ia()
