import sys
import pandas as pd
from agente_ia_webfy import agente_ia_responder

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def menu_respostas():
    print("=" * 70)
    print("💬 WEBFY - GERENCIADOR DE RESPOSTAS E PERSUASÃO RÁPIDA (JOÃO)")
    print("=" * 70)
    print("1 - Cliente respondeu SIM / PODE SER (Avisar início da construção + hospedagem)")
    print("2 - Cliente respondeu NÃO / AGORA NÃO (Mandar pontos positivos + o que está perdendo)")
    print("3 - Cliente perguntou VALOR / COMO FUNCIONA (Explicação transparente R$ 599)")
    print("=" * 70)
    
    opcao = input("\n👉 Escolha a opção (1, 2 ou 3): ").strip()
    empresa = input("👉 Nome da Empresa: ").strip() or "Empresa"
    cidade = input("👉 Cidade: ").strip() or "Curitiba"
    nicho = input("👉 Nicho: ").strip() or "serviços"
    
    if opcao == '1':
        msg, _ = agente_ia_responder(empresa, nicho, cidade, "sim pode dar inicio")
    elif opcao == '2':
        msg, _ = agente_ia_responder(empresa, nicho, cidade, "nao tenho interesse")
    elif opcao == '3':
        msg, _ = agente_ia_responder(empresa, nicho, cidade, "quanto custa a hospedagem")
    else:
        print("Opção inválida.")
        return

    print("\n" + "=" * 70)
    print("💬 MENSAGEM PRONTA (Copie e envie no WhatsApp):\n")
    print(msg)
    print("=" * 70)

if __name__ == "__main__":
    menu_respostas()
