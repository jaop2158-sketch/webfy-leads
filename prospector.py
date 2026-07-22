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
    if not phone_str:
        return None
    digits = re.sub(r'\D', '', str(phone_str))
    if len(digits) >= 10:
        if not digits.startswith("55") and len(digits) in [10, 11]:
            digits = "55" + digits
        return digits
    return None

def format_niche_display(nicho_raw):
    n = nicho_raw.lower().strip()
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
    return mapping.get(n, nicho_raw.capitalize())

def clean_company_name(title_raw):
    t = str(title_raw)
    t = re.sub(r'[\ufffd\x80-\xff]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    
    if any(domain in t.lower() for domain in ['maps.google', 'google.com', 'instagram.com', 'facebook.com']):
        return ""
        
    t = re.sub(r'(?i)\s*[-|—–:]?\s*(agende|agendamento|consulta|valores|desconto|preço|saiba mais|whatsapp|telefones?|os \d+|mais recomendados|em curitiba|em são paulo).*', '', t)
    
    parts = re.split(r'\s+[-|—–:]\s+', t)
    if parts and len(parts[0]) >= 3:
        clean_name = parts[0]
    else:
        clean_name = t
        
    return clean_name[:45].strip()

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
        
        is_directory_or_social = any(domain in url.lower() for domain in [
            'instagram.com', 'facebook.com', 'whatsapp.com', 'linktr.ee', 
            'doctoralia.com.br', 'psitto.com.br', 'google.com', 'youtube.com',
            'acheioprofissional.com.br', 'psinote.com.br', 'olx.com.br', 'cliniguia.com'
        ])
        
        has_custom_site = bool(url and not is_directory_or_social)
        
        maps_query = urllib.parse.quote(f"{clean_name} {cidade}")
        google_maps_url = f"https://www.google.com/maps/search/{maps_query}"
        
        processed_leads.append({
            "nome": clean_name,
            "nome_original": raw_title[:65],
            "cidade": cidade.capitalize(),
            "bairro": "Centro / Região",
            "rua": snippet[:100] + "..." if snippet else "Sem descrição registrada",
            "tem_site": "SIM" if has_custom_site else "NÃO (OPORTUNIDADE 🔥)",
            "site": url if url else "Apenas Redes / Sem Site",
            "telefone_original": phone_found if phone_found else "Buscar WhatsApp no Google/IG",
            "whatsapp_limpo": clean_p,
            "link_google_maps": google_maps_url
        })
        
    return processed_leads

# Mensagem 1: Curta e Humana (Quebra-gelo)
def generate_pitch_step1(nome_empresa, nicho, cidade):
    nome_limpo = clean_company_name(nome_empresa)
    cidade_fmt = cidade.capitalize()
    
    message = (
        f"Olá, tudo bem? Meu nome é João, sou da agência Webfy. 🚀\n\n"
        f"Vi o perfil da {nome_limpo} aí em {cidade_fmt} e achei o trabalho de vocês muito bacana! Posso te fazer uma pergunta rápida sobre o site de vocês?"
    )
    return message

# Mensagem 2: Explicando o valor normal vs oferta grátis
def generate_pitch_step2(nome_empresa, nicho, cidade):
    nicho_fmt = format_niche_display(nicho)
    
    message = (
        f"É que vi que vocês não têm um site moderno para celular e estão perdendo clientes do Google para a concorrência.\n\n"
        f"Um site desse nível no mercado custa entre R$ 2.000 e R$ 3.000, mas nós da Webfy estamos com uma ação onde a criação e mão de obra saem 100% DE GRAÇA.\n\n"
        f"A única coisa necessária é a taxa de hospedagem para o site ficar online no seu nome.\n\n"
        f"Já deixei uma prévia demonstrativa do site de vocês pronta. Posso te mandar o link para você dar uma olhada sem compromisso?"
    )
    return message

def export_reports(leads, nicho, cidade, output_dir="."):
    if not leads:
        print("❌ Nenhum lead encontrado para exportar.")
        return
        
    df = pd.DataFrame(leads)
    
    whatsapp_links = []
    pitches_step1 = []
    pitches_step2 = []
    
    for _, row in df.iterrows():
        p1 = generate_pitch_step1(row['nome'], nicho, cidade)
        p2 = generate_pitch_step2(row['nome'], nicho, cidade)
        pitches_step1.append(p1)
        pitches_step2.append(p2)
        
        if row['whatsapp_limpo']:
            encoded_pitch = urllib.parse.quote(p1)
            wa_link = f"https://wa.me/{row['whatsapp_limpo']}?text={encoded_pitch}"
        else:
            search_q = urllib.parse.quote(f"{row['nome']} {cidade} whatsapp instagram")
            wa_link = f"https://www.google.com/search?q={search_q}"
            
        whatsapp_links.append(wa_link)
        
    df['mensagem_curta_inicial'] = pitches_step1
    df['mensagem_explicacao_preco'] = pitches_step2
    df['link_whatsapp_direto'] = whatsapp_links
    
    csv_file = os.path.join(output_dir, f"leads_{nicho}_{cidade}.csv".lower().replace(" ", "_"))
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Planilha CSV gerada com sucesso: {csv_file}")
    
    html_file = os.path.join(output_dir, f"dashboard_leads_{nicho}_{cidade}.html".lower().replace(" ", "_"))
    
    rows_html = ""
    for idx, row in df.iterrows():
        status_badge = '<span style="background: #ef4444; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">NÃO TEM SITE 🔥</span>' if "NÃO" in row['tem_site'] else '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">Já tem site</span>'
        
        maps_button = f'<a href="{row["link_google_maps"]}" target="_blank" style="background: #ea4335; color: white; text-decoration: none; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-left: 6px;">📍 Ver no Maps</a>'
        
        if row['whatsapp_limpo']:
            wa_button = f'<a href="{row["link_whatsapp_direto"]}" target="_blank" style="background: #25D366; color: white; text-decoration: none; padding: 8px 14px; border-radius: 8px; font-weight: bold; display: inline-block;">💬 Enviar Oi no WhatsApp</a>' + maps_button
        else:
            wa_button = f'<a href="{row["link_whatsapp_direto"]}" target="_blank" style="background: #3b82f6; color: white; text-decoration: none; padding: 8px 14px; border-radius: 8px; font-weight: bold; display: inline-block;">🔍 Abrir no Google / IG</a>' + maps_button
            
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; font-weight: bold; color: #1f2937;">{row['nome']}</td>
            <td style="padding: 12px;">{row['cidade']}</td>
            <td style="padding: 12px;">{status_badge}</td>
            <td style="padding: 12px; color: #4b5563; font-size: 13px;"><a href="{row['site']}" target="_blank">{row['site'][:40]}</a></td>
            <td style="padding: 12px;">{row['telefone_original']}</td>
            <td style="padding: 12px;">{wa_button}</td>
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
            .container {{ max-width: 1250px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
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
            <h1>🚀 Webfy - Relatório de Prospecção Dividido em Etapas (João)</h1>
            <p><strong>Nicho:</strong> {format_niche_display(nicho)} | <strong>Cidade:</strong> {cidade.capitalize()}</p>
            
            <div class="script-box">
                <strong style="color: #166534; font-size: 16px;">💡 ROTEIRO DE VENDAS EM 3 PASSOS CURTOS:</strong><br><br>
                <strong>1º Mensagem (Botão Verde):</strong> <em>"Olá, tudo bem? Meu nome é João, sou da agência Webfy. Vi o perfil de vocês aí em {cidade.capitalize()} e achei o trabalho muito bacana! Posso te fazer uma pergunta rápida sobre o site de vocês?"</em><br><br>
                <strong>2º Mensagem (Quando ele responder "Pode sim"):</strong> <em>"É que vi que vocês não têm um site moderno para celular... Um site desse nível custa normalmente entre R$ 2.000 e R$ 3.000, mas a nossa criação sai 100% DE GRAÇA. A única coisa necessária é a taxa de hospedagem para o site ficar online no seu nome. Já deixei uma prévia pronta. Posso te mandar o link para dar uma olhada?"</em><br><br>
                <strong>3º Mensagem (Quando ele aceitar ver a prévia):</strong> Envie o link do site de demonstração + o link de afiliado para ele assinar a hospedagem!
            </div>

            <div class="stats">
                <div class="card">
                    <h3>Total de Oportunidades</h3>
                    <p>{len(df)}</p>
                </div>
                <div class="card" style="border-left-color: #ef4444; background: #fef2f2;">
                    <h3 style="color: #991b1b;">Sem Site (Oportunidades Quentes 🔥)</h3>
                    <p style="color: #7f1d1d;">{len(df[df['tem_site'].str.contains('NÃO')])}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Nome da Empresa / Profissional</th>
                        <th>Cidade</th>
                        <th>Status do Site</th>
                        <th>Link / Redes</th>
                        <th>Telefone</th>
                        <th>Ações Rápida (Enviar 1º Mensagem)</th>
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
        os.system('git add . && git commit -m "Auto-update leads & portal" && git push')
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
