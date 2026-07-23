import sys
import os
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def agente_ia_responder(nome_empresa, nicho, cidade, mensagem_cliente):
    """
    Inteligência Conversacional da Webfy (João)
    Mapeia e responde estrategicamente a qualquer mensagem do cliente:
    - SIM: Inicia a construção imediatamente e avisa que já vai enviar o link e acertar a hospedagem.
    - NÃO: Argumenta com pontos positivos e mostra o que o cliente está perdendo sem site no celular.
    - DÚVIDAS / OUTROS: Explica a criação grátis + hospedagem transparente.
    """
    txt = str(mensagem_cliente).lower().strip()
    
    # Palavras de Aceite (SIM, PODE, VAMOS, QUERO, INTERESSE, MANDA)
    palavras_sim = ['sim', 'pode', 'quero', 'manda', 'mostra', 'claro', 'com certeza', 'vamos', 'pode ser', 'dar inicio', 'dá inicio', 'iniciar', 'interesse', 'aceito']
    
    # Palavras de Recusa (NÃO, NAO, AGORA NÃO, NÃO QUERO, SEM INTERESSE)
    palavras_nao = ['não', 'nao', 'agora não', 'agora nao', 'não quero', 'nao quero', 'sem interesse', 'não preciso', 'nao preciso', 'já tenho', 'ja tenho']

    # 1. FLUXO QUANDO O CLIENTE RESPONDE "SIM" / "PODE SER" / "QUERO VER"
    if any(k in txt for k in palavras_sim) and not any(k in txt for k in palavras_nao):
        resposta_ia = (
            f"Show de bola! 🚀\n\n"
            f"Então já vou dar início à construção do site da {nome_empresa} aqui no nosso sistema agora mesmo!\n\n"
            f"Assim que a prévia demonstrativa estiver pronta, já te mando o link por aqui para você dar uma olhada no celular. "
            f"E estando tudo do seu agrado, a gente já faz o procedimento da hospedagem (R$ 599/ano ou parcelado) para colocar o seu site online no ar com domínio próprio (.com.br)!\n\n"
            f"Já estou finalizando a estrutura aqui e em breve te chamo com o link! 👍"
        )
        status_funil = "ACEITOU / INICIAR CONSTRUÇÃO 🚀"

    # 2. FLUXO QUANDO O CLIENTE RESPONDE "NÃO" / "AGORA NÃO" (CONVENCIMENTO PERSUASIVO)
    elif any(k in txt for k in palavras_nao):
        resposta_ia = (
            f"Entendo perfeitamente o seu lado! 🎯\n\n"
            f"Mas deixa eu te fazer uma rápida reflexão: hoje mais de 82% dos clientes aí em {cidade.capitalize()} pesquisam no Google pelo celular antes de fechar com uma {nicho}.\n\n"
            f"💡 **O que você ganha com o site:**\n"
            f"• Passa 10x mais credibilidade e autoridade no mercado.\n"
            f"• Aparece no Google quando os clientes procurarem por {nicho} aí na cidade.\n"
            f"• Botão de WhatsApp direto para agendamentos rápidos.\n\n"
            f"⚠️ **O que você perde ficando sem site ou com ele parado:**\n"
            f"• Perde clientes diariamente direto para os seus concorrentes que aparecem no Google.\n\n"
            f"Como a mão de obra e a criação saem **100% GRATUITAS** no nosso portfólio este mês (você só paga a hospedagem se aprovar), você não corre risco nenhum!\n\n"
            f"Quer que eu monte a prévia sem compromisso só para você ver como ficaria?"
        )
        status_funil = "RECUSOU / ENVIAR PONTOS POSITIVOS 🔥"

    # 3. DÚVIDA SOBRE PREÇO / VALORES / HOSPEDAGEM
    elif any(k in txt for k in ['pagar', 'cobrar', 'de graça', 'gratis', 'gratuito', 'hospedagem', 'valor', 'quanto']):
        resposta_ia = (
            f"A criação e a montagem do design saem 100% GRATUITAS para o nosso portfólio deste mês! 🎁\n\n"
            f"O único investimento necessário é a taxa padrão de hospedagem e servidor rápido para celular (R$ 599/ano ou parcelado), que é o custo necessário para colocar qualquer site profissional online no seu nome com domínio próprio (.com.br).\n\n"
            f"Posso iniciar a montagem da prévia da {nome_empresa} para te mostrar?"
        )
        status_funil = "DÚVIDA VALORES 💰"

    # 4. QUALQUER OUTRO TIPO DE RESPOSTA HUMANA
    else:
        resposta_ia = (
            f"Legal! Como estamos selecionando 5 empresas aí em {cidade.capitalize()} para a ação de portfólio, a criação do site da {nome_empresa} sai 100% GRATUITO.\n\n"
            f"Se você concordar, eu já dou início à construção da prévia aqui e te mando o link para você avaliar sem compromisso!\n\n"
            f"Podemos dar início?"
        )
        status_funil = "ATENDIMENTO CONVERSACIONAL 🤖"
        
    return resposta_ia, status_funil

def menu_agente_ia():
    print("=" * 70)
    print("🤖 AGENTE IA INTELIGENTE WEBFY - ESTRATÉGIA DE VENDAS E PERSUASÃO")
    print("=" * 70)
    print("Simule a conversa com o cliente para testar as respostas automáticas:\n")
    
    empresa = input("👉 Nome da Empresa: ").strip() or "Barbearia Exemplo"
    nicho = input("👉 Nicho: ").strip() or "barbearia"
    cidade = input("👉 Cidade: ").strip() or "Curitiba"
    msg_cliente = input("\n💬 Digite o que o cliente respondeu no WhatsApp: ").strip()
    
    if msg_cliente:
        resp, status = agente_ia_responder(empresa, nicho, cidade, msg_cliente)
        print("\n" + "=" * 70)
        print(f"🎯 DECISÃO DA IA: {status}")
        print("=" * 70)
        print("💬 MENSAGEM QUE A IA VAI ENVIAR:\n")
        print(resp)
        print("=" * 70)

if __name__ == "__main__":
    menu_agente_ia()
