import requests
import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configurações do Meta Cloud API (Preencha com seus dados do Meta for Developers)
META_ACCESS_TOKEN = os.environ.get("META_WA_ACCESS_TOKEN", "SEU_ACCESS_TOKEN_AQUI")
META_PHONE_NUMBER_ID = os.environ.get("META_WA_PHONE_NUMBER_ID", "SEU_PHONE_NUMBER_ID_AQUI")

def enviar_mensagem_meta_cloud_api(telefone_destino, texto_mensagem, access_token=None, phone_number_id=None):
    """
    Envia mensagens oficiais via API do WhatsApp Cloud no Meta for Developers
    """
    token = access_token if access_token else META_ACCESS_TOKEN
    num_id = phone_number_id if phone_number_id else META_PHONE_NUMBER_ID
    
    if token == "SEU_ACCESS_TOKEN_AQUI" or num_id == "SEU_PHONE_NUMBER_ID_AQUI":
        print("⚠️ Configuração do Meta Cloud API pendente. Insira o Access Token e o Phone Number ID.")
        return False, {"error": "Credenciais do Meta não configuradas."}
        
    url = f"https://graph.facebook.com/v18.0/{num_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Limpar telefone para formato internacional E.164 (ex: 5541999999999)
    phone_clean = str(telefone_destino).replace("+", "").replace("-", "").replace(" ", "").strip()
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_clean,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": texto_mensagem
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and "messages" in res_data:
            print(f"✅ Mensagem enviada via Meta API oficial para {phone_clean}!")
            return True, res_data
        else:
            print(f"❌ Erro no envio Meta API ({response.status_code}): {res_data}")
            return False, res_data
    except Exception as e:
        print(f"⚠️ Exceção ao conectar na API da Meta: {e}")
        return False, {"error": str(e)}

def menu_meta_api():
    print("=" * 65)
    print("🌐 MÓDULO OFICIAL META CLOUD API - WHATSAPP BUSINESS")
    print("=" * 65)
    print("Status das Credenciais:")
    print(f" • Token: {'Configurado ✅' if META_ACCESS_TOKEN != 'SEU_ACCESS_TOKEN_AQUI' else 'Pendente ⚠️'}")
    print(f" • Phone Number ID: {'Configurado ✅' if META_PHONE_NUMBER_ID != 'SEU_PHONE_NUMBER_ID_AQUI' else 'Pendente ⚠️'}")
    print("=" * 65)
    
    tel = input("\n👉 Digite o telefone de teste (ex: 5541999999999): ").strip()
    msg = input("👉 Digite a mensagem de teste: ").strip()
    
    if tel and msg:
        enviar_mensagem_meta_cloud_api(tel, msg)

if __name__ == "__main__":
    menu_meta_api()
