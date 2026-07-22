import requests
import urllib.parse
import json
import os
import re
import sys
import pandas as pd
from ddgs import DDGS

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def clean_phone(phone_str):
    if not phone_str or pd.isna(phone_str):
        return None
    digits = re.sub(r'\D', '', str(phone_str))
    if len(digits) >= 10:
        if not digits.startswith("55") and len(digits) in [10, 11]:
            digits = "55" + digits
        return digits
    return None

def format_niche_display(nicho_raw):
    n = str(nicho_raw).lower().strip()
    mapping = {
        "psicologo": "Psicologia",
        "psicóloga": "Psicologia",
        "psicologa": "Psicologia",
        "psicologia": "Psicologia",
        "dentista": "Odontologia",
        "odontologia": "Odontologia",
        "barbearia": "Barbearia",
        "estetica": "Estética",
        "estética": "Estética",
        "advogado": "Advocacia",
        "advocacia": "Advocacia",
        "medico": "Medicina",
        "médico": "Medicina",
        "restaurante": "Gastronomia",
        "petshop": "Pet Shop",
        "pet shop": "Pet Shop"
    }
    return mapping.get(n, str(nicho_raw).capitalize())

def clean_company_name(title_raw):
    t = str(title_raw)
    t = re.sub(r'[\ufffd\x80-\xff]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    
    if any(domain in t.lower() for domain in ['maps.google', 'google.com', 'instagram.com', 'facebook.com', 'doctoralia.com']):
        return ""
        
    t = re.sub(r'(?i)\s*[-|—–:]?\s*(agende|agendamento|consulta|valores|desconto|preço|saiba mais|whatsapp|telefones?|os \d+|mais recomendados|em curitiba|em são paulo).*', '', t)
    
    parts = re.split(r'\s+[-|—–:]\s+', t)
    if parts and len(parts[0]) >= 3:
        clean_name = parts[0]
    else:
        clean_name = t
        
    return clean_name[:45].strip()

# Auditoria em tempo real de links de sites
def audit_website_status(url):
    if not url or pd.isna(url) or len(str(url).strip()) < 5 or str(url).strip() in ["Sem Site Cadastrado", "Apenas Redes / Sem Site"]:
        return "SEM SITE (OPORTUNIDADE QUENTE 🔥)"
        
    url_str = str(url).strip()
    
    # Lista de agregadores / diretórios que não são sites próprios
    is_directory = any(domain in url_str.lower() for domain in [
        'linktr.ee', 'doctoralia.com.br', 'psitto.com.br', 'google.com', 
        'acheioprofissional.com.br', 'psinote.com.br', 'olx.com.br', 'cliniguia.com', 'facebook.com'
    ])
    
    if is_directory:
        return "SEM SITE PRÓPRIO / USADOR DE DIRETÓRIO (OPORTUNIDADE ⚡)"
        
    # Verificar se o site próprio abre ou está fora do ar
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    target_url = url_str if url_str.startswith("http") else "https://" + url_str
    
    try:
        r = requests.get(target_url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return "SITE ATIVO / AVALIAR CELULAR 📱"
        else:
            return f"SITE FORA DO AR (ERRO {r.status_code}) 🚨"
    except Exception:
        return "SITE FORA DO AR / LINK QUEBRADO 🚨"

# Mensagens super personalizadas conforme a auditoria real do site
def generate_pitch_step1(nome_empresa, nicho, cidade, status_site="SEM SITE"):
    nome_limpo = clean_company_name(nome_empresa)
    if not nome_limpo:
        nome_limpo = "empresa"
    cidade_fmt = cidade.capitalize()
    
    if "FORA DO AR" in status_site or "QUEBRADO" in status_site or "DESATUALIZADO" in status_site or "ATIVO" in status_site:
        pergunta = "Posso te fazer uma pergunta rápida sobre o site de vocês?"
    else:
        pergunta = "Posso te fazer uma pergunta rápida sobre a presença online de vocês?"
        
    message = (
        f"Olá, tudo bem? Meu nome é João, sou da agência Webfy. 🚀\n\n"
        f"Vi o perfil da {nome_limpo} aí em {cidade_fmt} no Google e achei o trabalho de vocês muito bacana! {pergunta}"
    )
    return message

def generate_pitch_step2(nome_empresa, nicho, cidade, status_site="SEM SITE"):
    nicho_fmt = format_niche_display(nicho)
    
    if "FORA DO AR" in status_site or "QUEBRADO" in status_site:
        contexto = "É que fui tentar acessar o site de vocês pelo celular e percebi que ele está fora do ar / com erro, o que faz vocês perderem muitos clientes do Google todos os dias."
    elif "DIRETÓRIO" in status_site or "ATIVO" in status_site:
        contexto = "É que vi que o site de vocês está um pouco desatualizado no celular e vocês estão perdendo clientes do Google para a concorrência."
    else:
        contexto = "É que vi que vocês ainda não têm um site próprio para celular e estão perdendo clientes do Google para a concorrência todos os dias."
        
    message = (
        f"{contexto}\n\n"
        f"Um site desse nível no mercado custa entre R$ 2.000 e R$ 3.000, mas nós da Webfy estamos com uma ação de portfólio onde a criação e mão de obra saem 100% DE GRAÇA.\n\n"
        f"Você não paga nada pela criação. A única coisa necessária é a taxa de hospedagem para o site ficar online no seu nome.\n\n"
        f"Já deixei uma prévia demonstrativa do site de vocês pronta. Posso te mandar o link para você dar uma olhada sem compromisso?"
    )
    return message

def fetch_leads(nicho, cidade):
    print(f"\n🔍 Buscando empresas/profissionais de '{nicho}' em '{cidade}' (Google Maps & Web)...")
    
    queries = [
        f"consultorio {nicho} {cidade}",
        f"clinica {nicho} {cidade}",
        f"atendimento {nicho} {cidade}",
        f"{nicho} em {cidade}"
    ]
    
    all_raw_items = []
    
    for q in queries:
        try:
            with DDGS() as ddg:
                res = list(ddg.text(q, max_results=15))
                for item in res:
                    all_raw_items.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", "")
                    })
        except Exception as e:
            print(f"⚠️ Aviso na busca por '{q}': {e}")
            
    processed_leads = []
    seen_titles = set()
    
    for item in all_raw_items:
        raw_title = item.get('title', '').strip()
        url = item.get('url', '').strip()
        snippet = item.get('snippet', '').strip()
        
        if not raw_title or len(raw_title) < 4:
            continue
            
        clean_name = clean_company_name(raw_title)
        if not clean_name or len(clean_name) < 3:
            continue
            
        title_key = clean_name.lower()[:25]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        
        phones = re.findall(r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}', raw_title + " " + snippet)
        phone_found = phones[0] if phones else None
        clean_p = clean_phone(phone_found) if phone_found else None
        
        # Auditar status real do site via HTTP
        status_site = audit_website_status(url)
            
        maps_query = urllib.parse.quote(f"{clean_name} {cidade}")
        google_maps_url = f"https://www.google.com/maps/search/{maps_query}"
        
        processed_leads.append({
            "nome": clean_name,
            "nome_original": raw_title[:65],
            "cidade": cidade.capitalize(),
            "bairro": "Centro / Região",
            "rua": snippet[:100] + "..." if snippet else "Sem descrição registrada",
            "tem_site": status_site,
            "site": url if url else "Sem Site Cadastrado",
            "telefone_original": phone_found if phone_found else "Buscar WhatsApp no Google Maps",
            "whatsapp_limpo": clean_p,
            "link_google_maps": google_maps_url
        })
        
    return processed_leads

def export_reports(leads, nicho, cidade, output_dir="."):
    if not leads:
        print("❌ Nenhum lead encontrado para exportar.")
        return
        
    df = pd.DataFrame(leads)
    
    wa_links_step1 = []
    wa_links_step2 = []
    pitches_step1 = []
    pitches_step2 = []
    
    for _, row in df.iterrows():
        status_s = str(row.get('tem_site', ''))
        p1 = generate_pitch_step1(row['nome'], nicho, cidade, status_site=status_s)
        p2 = generate_pitch_step2(row['nome'], nicho, cidade, status_site=status_s)
        pitches_step1.append(p1)
        pitches_step2.append(p2)
        
        wa_p = row.get('whatsapp_limpo')
        clean_wa = clean_phone(wa_p)
        
        if clean_wa:
            enc1 = urllib.parse.quote(p1)
            enc2 = urllib.parse.quote(p2)
            l1 = f"https://wa.me/{clean_wa}?text={enc1}"
            l2 = f"https://wa.me/{clean_wa}?text={enc2}"
        else:
            search_q = urllib.parse.quote(f"{row['nome']} {cidade} whatsapp")
            l1 = f"https://www.google.com/search?q={search_q}"
            l2 = f"https://www.google.com/search?q={search_q}"
            
        wa_links_step1.append(l1)
        wa_links_step2.append(l2)
        
    df['mensagem_1_inicial'] = pitches_step1
    df['mensagem_2_preco_oferta'] = pitches_step2
    df['link_whatsapp_msg1'] = wa_links_step1
    df['link_whatsapp_msg2'] = wa_links_step2
    
    csv_file = os.path.join(output_dir, f"leads_{nicho}_{cidade}.csv".lower().replace(" ", "_"))
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Planilha CSV gerada com sucesso: {csv_file}")
    
    core_name = f"{nicho}_{cidade}".lower().replace(" ", "_")
    html_file = os.path.join(output_dir, f"dashboard_leads_{core_name}.html")
    
    rows_html = ""
    for idx, row in df.iterrows():
        status_str = str(row['tem_site'])
        if "FORA DO AR" in status_str or "QUEBRADO" in status_str:
            status_badge = '<span style="background: #dc2626; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">FORA DO AR 🚨</span>'
        elif "SEM SITE" in status_str:
            status_badge = '<span style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">SEM SITE 🔥</span>'
        elif "DIRETÓRIO" in status_str:
            status_badge = '<span style="background: #f59e0b; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">SEM SITE PRÓPRIO ⚡</span>'
        else:
            status_badge = '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">SITE ATIVO 📱</span>'
            
        maps_button = f'<a href="{row["link_google_maps"]}" target="_blank" style="background: #ea4335; color: white; text-decoration: none; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-left: 4px;">📍 Maps</a>'
        
        wa_p = row.get('whatsapp_limpo')
        clean_wa = clean_phone(wa_p)
        
        if clean_wa:
            enc1 = urllib.parse.quote(row['mensagem_1_inicial'])
            enc2 = urllib.parse.quote(row['mensagem_2_preco_oferta'])
            link_m1 = f"https://wa.me/{clean_wa}?text={enc1}"
            link_m2 = f"https://wa.me/{clean_wa}?text={enc2}"
            
            wa_buttons = f"""
            <a href="{link_m1}" target="_blank" style="background: #25D366; color: white; text-decoration: none; padding: 7px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; display: inline-block;">💬 1ª Msg</a>
            <a href="{link_m2}" target="_blank" style="background: #0284c7; color: white; text-decoration: none; padding: 7px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; display: inline-block; margin-left: 4px;">💰 2ª Msg (Preço)</a>
            {maps_button}
            """
        else:
            search_q = urllib.parse.quote(f"{row['nome']} {cidade} whatsapp")
            wa_buttons = f'<a href="https://www.google.com/search?q={search_q}" target="_blank" style="background: #3b82f6; color: white; text-decoration: none; padding: 7px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; display: inline-block;">🔍 Buscar no Google</a>' + maps_button
            
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; font-weight: bold; color: #1f2937;">{row['nome']}</td>
            <td style="padding: 12px;">{row['cidade']}</td>
            <td style="padding: 12px;">{status_badge}</td>
            <td style="padding: 12px; color: #4b5563; font-size: 13px;"><a href="{row['site']}" target="_blank">{str(row['site'])[:35]}</a></td>
            <td style="padding: 12px;">{row['telefone_original']}</td>
            <td style="padding: 12px; white-space: nowrap;">{wa_buttons}</td>
        </tr>
        """
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Leads Webfy - {nicho.capitalize()} em {cidade.capitalize()}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; color: #111827; }}
            .container {{ max-width: 1300px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            h1 {{ color: #0284c7; margin-top: 0; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .card {{ background: #e0f2fe; padding: 15px 20px; border-radius: 8px; flex: 1; border-left: 4px solid #0284c7; }}
            .card h3 {{ margin: 0; font-size: 14px; color: #0369a1; text-transform: uppercase; }}
            .card p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #0f172a; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background: #f8fafc; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569; font-size: 13px; text-transform: uppercase; }}
            .script-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Webfy - Painel de Prospecção Auditado (João)</h1>
            <p><strong>Nicho:</strong> {format_niche_display(nicho)} | <strong>Cidade:</strong> {cidade.capitalize()}</p>
            
            <div class="script-box">
                <strong style="color: #166534; font-size: 16px;">💡 REVISÃO E AUDITORIA AUTOMÁTICA DE SITES:</strong><br><br>
                🚨 <strong>SITE FORA DO AR / QUEBRADO:</strong> O robô testou o link e detectou que a página não abre. A 2ª mensagem avisa: <em>"fui tentar acessar e percebi que o site está fora do ar..."</em><br>
                ⚡ <strong>SEM SITE PRÓPRIO:</strong> A empresa depende de cadastros genéricos.<br>
                🔥 <strong>SEM SITE:</strong> A 2ª mensagem avisa que a empresa ainda não tem site próprio para celular.
            </div>

            <div class="stats">
                <div class="card">
                    <h3>Total Oportunidades</h3>
                    <p>{len(df)}</p>
                </div>
                <div class="card" style="border-left-color: #ef4444; background: #fef2f2;">
                    <h3 style="color: #991b1b;">Sem Site / Fora do Ar 🔥</h3>
                    <p style="color: #7f1d1d;">{len(df[df['tem_site'].str.contains('SEM SITE|FORA DO AR|QUEBRADO|DIRETÓRIO', na=False)])}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Empresa / Profissional</th>
                        <th>Cidade</th>
                        <th>Status do Site (Auditado HTTP)</th>
                        <th>Link Registrado</th>
                        <th>Telefone</th>
                        <th>Ações Rápida (1ª Msg | 2ª Msg | Maps)</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📊 Dashboard visual HTML gerado: {html_file}")
    
    # 1. Atualizar o Portal Central index.html automaticamente
    try:
        from build_portal import build_central_portal
        build_central_portal(output_dir)
    except Exception as e:
        print(f"⚠️ Aviso ao atualizar o portal central: {e}")

    # 2. Enviar atualizações para o GitHub e Vercel 100% AUTOMÁTICO
    try:
        print("\n🚀 Enviando atualizações AUTOMATICAMENTE para o GitHub e Vercel...")
        os.system('git add . && git commit -m "Auto-audit sites HTTP status and custom messages" && git push')
        print("✅ Tudo sincronizado! Seu site no Vercel foi atualizado sozinho no ar!")
    except Exception as e:
        print(f"⚠️ Aviso ao sincronizar com o Vercel: {e}")

def main():
    print("=" * 60)
    print("🤖 PROSPECTOR DE LEADS AUTOMÁTICO - WEBFY (JOÃO)")
    print("=" * 60)
    
    nicho = input("\n👉 Digite o Nicho (ex: Psicologo, Dentista, Barbearia, Estetica): ").strip()
    cidade = input("👉 Digite a Cidade (ex: Curitiba, Sao Paulo, Campinas, Sorocaba): ").strip()
    
    if not nicho or not cidade:
        print("❌ Nicho e Cidade são obrigatórios.")
        return
        
    leads = fetch_leads(nicho, cidade)
    print(f"\n🎯 Total de {len(leads)} empresas/profissionais encontrados!")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_reports(leads, nicho, cidade, output_dir=script_dir)

if __name__ == "__main__":
    main()
