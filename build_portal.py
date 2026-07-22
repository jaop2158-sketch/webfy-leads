import os
import glob
import json
import re
import sys
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

KNOWN_CITIES = [
    "sao paulo", "são paulo", "curitiba", "campinas", "sorocaba", 
    "rio de janeiro", "belo horizonte", "porto alegre", "salvador", 
    "brasilia", "brasília", "recife", "fortaleza", "goiania", "goiânia"
]

def format_city_display(cidade_raw):
    c = cidade_raw.lower().strip()
    mapping = {
        "sao paulo": "São Paulo",
        "são paulo": "São Paulo",
        "curitiba": "Curitiba",
        "campinas": "Campinas",
        "sorocaba": "Sorocaba",
        "rio de janeiro": "Rio de Janeiro",
        "belo horizonte": "Belo Horizonte",
        "porto alegre": "Porto Alegre",
        "salvador": "Salvador",
        "brasilia": "Brasília",
        "brasília": "Brasília"
    }
    return mapping.get(c, cidade_raw.title())

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

def parse_filename(filename):
    # Removing 'leads_' and '.csv'
    core = filename.replace("leads_", "").replace(".csv", "")
    
    # Check if any known city matches the end of the filename
    matched_city = None
    matched_niche = None
    
    for city in KNOWN_CITIES:
        city_slug = city.replace(" ", "_")
        if core.endswith("_" + city_slug):
            matched_city = city
            matched_niche = core[:-len("_" + city_slug)]
            break
            
    if not matched_city:
        parts = core.rsplit("_", 1)
        matched_niche = parts[0]
        matched_city = parts[1] if len(parts) > 1 else "Geral"
        
    return format_niche_display(matched_niche), format_city_display(matched_city)

def build_central_portal(project_dir="."):
    print("🌐 Construindo Portal Central da Webfy para o Vercel...")
    
    csv_files = glob.glob(os.path.join(project_dir, "leads_*.csv"))
    dashboards = []
    
    for csv_path in csv_files:
        filename = os.path.basename(csv_path)
        if not filename.startswith("leads_"):
            continue
            
        nicho_fmt, cidade_fmt = parse_filename(filename)
        
        try:
            df = pd.read_csv(csv_path)
            total_leads = len(df)
            leads_sem_site = len(df[df['tem_site'].str.contains('NÃO', na=False)]) if 'tem_site' in df.columns else 0
        except Exception as e:
            total_leads = 0
            leads_sem_site = 0
            
        core_name = filename.replace("leads_", "").replace(".csv", "")
        html_dashboard_filename = f"dashboard_leads_{core_name}.html"
        
        dashboards.append({
            "nicho": nicho_fmt,
            "cidade": cidade_fmt,
            "total_leads": total_leads,
            "leads_sem_site": leads_sem_site,
            "html_file": html_dashboard_filename,
            "csv_file": filename
        })
        
    cards_html = ""
    unique_niches = set()
    unique_cities = set()
    
    for d in dashboards:
        unique_niches.add(d['nicho'])
        unique_cities.add(d['cidade'])
        
        cards_html += f"""
        <div class="card" data-nicho="{d['nicho'].lower()}" data-cidade="{d['cidade'].lower()}">
            <div class="card-header">
                <span class="badge-nicho">{d['nicho']}</span>
                <span class="badge-cidade">📍 {d['cidade']}</span>
            </div>
            <h2>{d['nicho']} em {d['cidade']}</h2>
            <div class="stats-row">
                <div>
                    <span class="stat-num">{d['total_leads']}</span>
                    <span class="stat-label">Total Oportunidades</span>
                </div>
                <div>
                    <span class="stat-num sem-site">{d['leads_sem_site']}</span>
                    <span class="stat-label">Sem Site 🔥</span>
                </div>
            </div>
            <div class="card-actions">
                <a href="{d['html_file']}" class="btn-view">📊 Abrir Painel com WhatsApp</a>
                <a href="{d['csv_file']}" class="btn-download" download>📥 Baixar Excel</a>
            </div>
        </div>
        """
        
    nicho_options = "".join([f'<option value="{n.lower()}">{n}</option>' for n in sorted(unique_niches)])
    cidade_options = "".join([f'<option value="{c.lower()}">{c}</option>' for c in sorted(unique_cities)])
    
    portal_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webfy - Portal Central de Prospecção</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #64748b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{ background-color: #f1f5f9; color: var(--dark); padding-bottom: 60px; }}
        
        header {{
            background: linear-gradient(135deg, var(--dark), #1e293b);
            color: white;
            padding: 40px 24px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        header h1 {{ font-size: 32px; font-weight: 700; margin-bottom: 8px; }}
        header h1 span {{ color: #38bdf8; }}
        header p {{ color: #94a3b8; font-size: 16px; }}
        
        .container {{ max-width: 1200px; margin: -30px auto 0; padding: 0 24px; }}
        
        .filter-box {{
            background: white;
            padding: 20px 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 30px;
        }}
        .filter-group {{ display: flex; flex-direction: column; gap: 6px; flex: 1; min-width: 200px; }}
        .filter-group label {{ font-size: 13px; font-weight: 600; color: var(--gray); text-transform: uppercase; }}
        .filter-group select {{
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            font-size: 15px;
            outline: none;
            cursor: pointer;
            transition: border 0.3s;
        }}
        .filter-group select:focus {{ border-color: var(--primary); }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
        }}
        
        .card {{
            background: white;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            border: 1px solid #e2e8f0;
            transition: transform 0.3s, box-shadow 0.3s;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(2, 132, 199, 0.12);
            border-color: #bae6fd;
        }}
        
        .card-header {{ display: flex; justify-content: space-between; margin-bottom: 16px; }}
        .badge-nicho {{ background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        .badge-cidade {{ background: #f1f5f9; color: #475569; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        
        .card h2 {{ font-size: 20px; color: var(--dark); margin-bottom: 16px; }}
        
        .stats-row {{
            display: flex;
            justify-content: space-around;
            background: #f8fafc;
            padding: 14px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stat-num {{ display: block; font-size: 22px; font-weight: 700; color: var(--dark); }}
        .stat-num.sem-site {{ color: #ef4444; }}
        .stat-label {{ font-size: 12px; color: var(--gray); font-weight: 500; }}
        
        .card-actions {{ display: flex; gap: 10px; flex-direction: column; }}
        .btn-view {{
            background: var(--primary);
            color: white;
            text-decoration: none;
            padding: 12px;
            border-radius: 10px;
            font-weight: 600;
            text-align: center;
            transition: background 0.3s;
        }}
        .btn-view:hover {{ background: var(--primary-dark); }}
        .btn-download {{
            background: #f1f5f9;
            color: #334155;
            text-decoration: none;
            padding: 10px;
            border-radius: 10px;
            font-weight: 600;
            text-align: center;
            font-size: 13px;
        }}
        
        footer {{ text-align: center; margin-top: 50px; color: var(--gray); font-size: 14px; }}
    </style>
</head>
<body>

    <header>
        <h1>🚀 <span>Webfy</span> Central de Prospecção</h1>
        <p>Portal da Agência Webfy — Gerenciado por João</p>
    </header>

    <div class="container">
        <div class="filter-box">
            <div class="filter-group">
                <label>Filtrar por Nicho</label>
                <select id="filterNicho" onchange="filterCards()">
                    <option value="todos">Todos os Nichos</option>
                    {nicho_options}
                </select>
            </div>
            <div class="filter-group">
                <label>Filtrar por Cidade</label>
                <select id="filterCidade" onchange="filterCards()">
                    <option value="todas">Todas as Cidades</option>
                    {cidade_options}
                </select>
            </div>
        </div>

        <div class="grid" id="cardsGrid">
            {cards_html}
        </div>

        <footer>
            <p>© 2026 Webfy Agency — Atualização Automática de Leads</p>
        </footer>
    </div>

    <script>
        function filterCards() {{
            const selectedNicho = document.getElementById('filterNicho').value.toLowerCase();
            const selectedCidade = document.getElementById('filterCidade').value.toLowerCase();
            const cards = document.querySelectorAll('.card');

            cards.forEach(card => {{
                const nicho = card.getAttribute('data-nicho');
                const cidade = card.getAttribute('data-cidade');

                const matchNicho = (selectedNicho === 'todos' || nicho.includes(selectedNicho));
                const matchCidade = (selectedCidade === 'todas' || cidade.includes(selectedCidade));

                if (matchNicho && matchCidade) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    
    index_file = os.path.join(project_dir, "index.html")
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(portal_html)
    print(f"✅ Portal Central 'index.html' gerado com sucesso: {index_file}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_central_portal(script_dir)
