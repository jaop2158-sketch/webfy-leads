import json
import re
import sys
from prospector import generate_pitch_step2

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def processar_resposta_recebida(nome_empresa, nicho, cidade, texto_resposta_cliente):
    """
    Analisa o texto que o cliente respondeu e gera a 2ª mensagem perfeita ou o contorno
    """
    texto = str(texto_resposta_cliente).lower().strip()
    
    # Palavras-chave de interesse (SIM)
    palavras_sim = ['sim', 'pode', 'quero', 'manda', 'mostra', 'claro', 'com certeza', 'como funciona', 'interesse']
    # Palavras-chave de recusa (NÃO)
    palavras_nao = ['não', 'nao', 'agora não', 'tenho site', 'obrigado', 'não tenho interesse']
    
    if any(word in texto for word in palavras_sim):
        print(f"🎯 CLIENTE RESPONDEU 'SIM'! ({nome_empresa})")
        msg2 = generate_pitch_step2(nome_empresa, nicho, cidade, status_site="SEM SITE")
        print("\n💬 [ENVIO AUTOMÁTICO DA 2ª MENSAGEM - OFERTA R$ 599]:\n")
        print(msg2)
        return "ENVIAR_MSG2", msg2
    elif any(word in texto for word in palavras_nao):
        print(f"⚠️ CLIENTE RESPONDEU 'NÃO' ({nome_empresa})")
        msg_contorno = "Sem problemas! Fico à disposição caso no futuro precisem de um site moderno que converte no celular. Abraços!"
        return "ENVIAR_CONTORNO", msg_contorno
    else:
        print(f"❓ RESPOSTA DIVERSA RECEBIDA DE {nome_empresa}: '{texto_resposta_cliente}'")
        msg_padrao = generate_pitch_step2(nome_empresa, nicho, cidade, status_site="SEM SITE")
        return "ENVIAR_MSG2", msg_padrao

if __name__ == "__main__":
    print("🤖 TESTE DE DETECÇÃO AUTOMÁTICA DE RESPOSTAS")
    test_text = input("👉 Simule a resposta do cliente (ex: 'Pode mandar o link'): ")
    processar_resposta_recebida("Barbearia Exemplo", "barbearia", "curitiba", test_text)
