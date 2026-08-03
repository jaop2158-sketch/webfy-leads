"""Import the current deployed CRM shell and attach versioned Melvex assets."""

from pathlib import Path
import sys


def sync(source: Path, destination: Path) -> None:
    html = source.read_text(encoding="utf-8")
    stylesheet = '<link rel="stylesheet" href="../src/assets/melvex-outreach.css">'
    script = '<script src="../src/assets/outreach-composer.js" defer></script>'
    if stylesheet not in html:
        html = html.replace("</head>", f"  {stylesheet}\n</head>")
    if script not in html:
        html = html.replace("</body>", f"  {script}\n</body>")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("uso: sync_live_crm.py origem.html destino.html")
    sync(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
