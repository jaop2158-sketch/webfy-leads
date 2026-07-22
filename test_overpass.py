import requests
import json
import urllib.parse
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def search_overpass(nicho, cidade):
    city_boxes = {
        "sao paulo": (-23.68, -46.75, -23.45, -46.50),
        "curitiba": (-25.55, -49.35, -25.35, -49.18),
        "campinas": (-22.97, -47.14, -22.82, -47.00),
        "rio de janeiro": (-23.00, -43.40, -22.80, -43.15),
        "belo horizonte": (-19.98, -44.02, -19.80, -43.90)
    }
    
    cidade_clean = cidade.lower().strip()
    bbox = city_boxes.get(cidade_clean, (-23.68, -46.75, -23.45, -46.50))
    south, west, north, east = bbox
    
    nicho_clean = nicho.lower().strip()
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node["name"~"{nicho_clean}", i]({south},{west},{north},{east});
      node["amenity"~"{nicho_clean}", i]({south},{west},{north},{east});
      node["healthcare"~"{nicho_clean}", i]({south},{west},{north},{east});
      way["name"~"{nicho_clean}", i]({south},{west},{north},{east});
    );
    out body 50;
    """
    
    headers = {"User-Agent": "CriaSiteStudio/1.0"}
    try:
        r = requests.post(overpass_url, data={"data": query}, headers=headers, timeout=25)
        data = r.json()
    except Exception as e:
        print("Erro Overpass:", e)
        return []
        
    elements = data.get("elements", [])
    leads = []
    
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
            
        website = tags.get("website") or tags.get("contact:website") or tags.get("url")
        phone = tags.get("phone") or tags.get("contact:phone") or tags.get("mobile")
        street = tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        suburb = tags.get("addr:suburb", "") or tags.get("addr:district", "")
        
        full_address = f"{street} {housenumber}".strip()
        if suburb:
            full_address += f" - {suburb}"
            
        has_website = bool(website and len(str(website).strip()) > 5)
        
        leads.append({
            "nome": name,
            "cidade": cidade.capitalize(),
            "bairro": suburb if suburb else f"{cidade.capitalize()} / Centro",
            "rua": full_address if full_address else "Endereço registrado",
            "tem_site": "SIM" if has_website else "NÃO (OPORTUNIDADE 🔥)",
            "site": website if has_website else "Sem site cadastrado",
            "telefone_original": phone if phone else "Buscar WhatsApp no Google/IG",
            "whatsapp_limpo": re.sub(r'\D', '', phone) if phone and len(re.sub(r'\D', '', phone)) >= 10 else None
        })
        
    return leads

if __name__ == "__main__":
    leads = search_overpass("dentista", "sao paulo")
    print(f"Total encontrado: {len(leads)}")
    for l in leads[:5]:
        print("-", l["nome"], "| Site:", l["tem_site"])
