"""Generate a stable CRM page from an extraction and publish validated artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence

RAW_LEADS_PATTERN = re.compile(r"const rawLeads = \[.*?\];\n", re.DOTALL)
LATEST_WORKSPACE_PATTERN = re.compile(
    r"<!-- latest-extraction:start -->.*?<!-- latest-extraction:end -->", re.DOTALL
)
REQUIRED_FIELDS = ("nome", "celular", "categoria", "endereco", "site")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug:
        raise ValueError("Segmento e cidade precisam conter letras ou números.")
    return slug


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text and text.lower() != "nan" else fallback


def _status_site(value: object) -> str:
    status = _text(value, "Sem site")
    upper = status.upper()
    if "404" in upper:
        return "Fora do ar (404)"
    if "FORA DO AR" in upper or "QUEBRADO" in upper:
        return "Fora do ar"
    if "SEM SITE" in upper:
        return "Sem site"
    return "Online"


def _score(lead: Mapping[str, object]) -> int:
    reviews = int(float(lead.get("reviewsCount") or 0))
    status = _status_site(lead.get("tem_site") or lead.get("status_site"))
    opportunity = 45 if status != "Online" else 10
    return min(200, 80 + opportunity + min(reviews, 50))


def _tier(score: int) -> str:
    if score >= 160:
        return "DIAMANTE"
    if score >= 130:
        return "PLATINUM"
    if score >= 100:
        return "OURO"
    return "PRATA"


def to_crm_lead(lead: Mapping[str, object], category: str) -> dict[str, object]:
    phone = _text(lead.get("telefone_original") or lead.get("celular"))
    site = _text(lead.get("site"), "Nao possui")
    if site in {"Sem Site Cadastrado", "Apenas Redes / Sem Site"}:
        site = "Nao possui"
    status = _status_site(lead.get("tem_site") or lead.get("status_site"))
    score = _score(lead)
    return {
        "nome": _text(lead.get("nome"), "Empresa sem nome"),
        "celular": phone,
        "avaliacao": float(lead.get("avaliacao") or 0),
        "reviewsCount": int(float(lead.get("reviewsCount") or 0)),
        "score": score,
        "tier": _tier(score),
        "tipo_site": "Sem Site" if site == "Nao possui" else "Site Oficial",
        "is_official_site": site != "Nao possui",
        "categoria": _text(lead.get("categoria"), category),
        "endereco": _text(lead.get("endereco") or lead.get("rua"), "Não encontrado"),
        "site": site,
        "status_site": status,
        "link_maps": _text(lead.get("link_google_maps") or lead.get("link_maps")),
        "proposta_status": "NUNCA CONTATADO",
    }


def validate_leads(leads: Sequence[Mapping[str, object]]) -> None:
    if not leads:
        raise ValueError("A extração não produziu leads; o site não será alterado.")
    for index, lead in enumerate(leads, start=1):
        missing = [field for field in REQUIRED_FIELDS if field not in lead]
        if missing:
            raise ValueError(f"Lead {index} sem campos obrigatórios: {', '.join(missing)}")
        if not _text(lead.get("nome")):
            raise ValueError(f"Lead {index} está sem nome.")


def render_crm(leads: Sequence[Mapping[str, object]], category: str, city: str, template: Path) -> str:
    html = template.read_text(encoding="utf-8")
    category_slug, city_slug = slugify(category), slugify(city)
    crm_leads = [to_crm_lead(lead, category) for lead in leads]
    validate_leads(crm_leads)
    payload = json.dumps(crm_leads, ensure_ascii=False, separators=(",", ":"))
    html, count = RAW_LEADS_PATTERN.subn(f"const rawLeads = {payload};\n", html, count=1)
    if count != 1:
        raise ValueError("O template não contém um bloco rawLeads válido.")
    replacements = {
        r"<title>.*?</title>": f"<title>CRM de Leads — {category} em {city}</title>",
        r'<div class="eyebrow">.*?</div>': f'<div class="eyebrow">CRM de prospecção • {category} {city}</div>',
        r'<h1 id="page-title">.*?</h1>': f'<h1 id="page-title">{category} em {city}</h1>',
        r'const categoryName = ".*?";': f'const categoryName = {json.dumps(category_slug)};',
        r'const locationName = ".*?";': f'const locationName = {json.dumps(city_slug)};',
        r'const STORAGE_KEY = ".*?";': f'const STORAGE_KEY = "maps_crm_v2_{category_slug}_{city_slug}";',
        r"leads_[a-z0-9_]+\.csv": f"leads_{category_slug}_{city_slug}.csv",
        r"backup_crm_[a-z0-9_]+\.json": f"backup_crm_{category_slug}_{city_slug}.json",
    }
    for pattern, replacement in replacements.items():
        html = re.sub(pattern, replacement, html, count=1)
    marker = f'<meta name="x-generated-at" content="{datetime.now(timezone.utc).isoformat()}">'
    return html.replace("</head>", f"  {marker}\n</head>", 1)


def update_portal_summary(
    index_path: Path, category: str, city: str, destination: Path, lead_count: int
) -> None:
    if not index_path.exists():
        return
    html = index_path.read_text(encoding="utf-8")
    href = destination.relative_to(index_path.parent).as_posix()
    updated = datetime.now().astimezone().strftime("%d/%m/%Y às %H:%M")
    summary = (
        '<!-- latest-extraction:start -->'
        '<article id="latest-extraction" class="workspace glass" '
        'style="margin-top:18px">'
        '<div class="workspace-main">'
        '<span class="workspace-kicker">Extração mais recente</span>'
        f'<h3>{category} · {city}</h3>'
        f'<p>{lead_count} leads validados · atualizado em {updated}.</p>'
        f'<a class="btn primary" href="{href}">Abrir CRM atualizado</a>'
        '</div></article>'
        '<!-- latest-extraction:end -->'
    )
    if LATEST_WORKSPACE_PATTERN.search(html):
        html = LATEST_WORKSPACE_PATTERN.sub(summary, html, count=1)
    else:
        html = html.replace("</section>", f"{summary}\n    </section>", 1)
    index_path.write_text(html, encoding="utf-8")


def run_git(project_dir: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=project_dir, check=True, text=True, capture_output=True)


def publish_files(project_dir: Path, files: Iterable[Path], message: str) -> bool:
    relative = [str(path.resolve().relative_to(project_dir.resolve())) for path in files]
    run_git(project_dir, ["add", "--", *relative])
    staged = subprocess.run(["git", "diff", "--cached", "--quiet", "--", *relative], cwd=project_dir)
    if staged.returncode == 0:
        print("ℹ️ Nenhuma mudança nova para publicar.")
        return False
    if staged.returncode != 1:
        raise RuntimeError("Não foi possível verificar as mudanças preparadas no Git.")
    run_git(project_dir, ["commit", "-m", message, "--", *relative])
    result = run_git(project_dir, ["push"])
    print(result.stdout.strip() or "✅ Push concluído; a Vercel iniciará o deploy.")
    return True


def update_site(project_dir: Path, leads: Sequence[Mapping[str, object]], category: str, city: str, artifacts: Sequence[Path] = (), publish: bool = True) -> Path:
    template = project_dir / "advocacia" / "itajuba.html"
    if not template.exists():
        raise FileNotFoundError(f"Template CRM não encontrado: {template}")
    category_slug, city_slug = slugify(category), slugify(city)
    destination = project_dir / category_slug / f"{city_slug}.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_crm(leads, category, city, template), encoding="utf-8")
    index_path = project_dir / "index.html"
    update_portal_summary(index_path, category, city, destination, len(leads))
    print(f"✅ CRM atualizado: {destination}")
    if publish:
        files = [destination, index_path, *[path for path in artifacts if path.exists()]]
        publish_files(project_dir, files, f"data(leads): update {category_slug} in {city_slug}")
    else:
        print("ℹ️ Modo local: nenhum commit ou push foi realizado.")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="Arquivo JSON com a lista de leads")
    parser.add_argument("--category", required=True)
    parser.add_argument("--city", required=True)
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()
    leads = json.loads(args.json_file.read_text(encoding="utf-8"))
    update_site(args.project_dir.resolve(), leads, args.category, args.city, publish=not args.no_publish)


if __name__ == "__main__":
    main()
