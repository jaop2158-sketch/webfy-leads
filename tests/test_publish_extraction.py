import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.publish_extraction import render_crm, slugify, to_crm_lead, update_site


class PublishExtractionTests(unittest.TestCase):
    def setUp(self):
        self.project = Path(__file__).resolve().parents[1]
        self.leads = [
            {
                "nome": "Silva & Lima Advocacia",
                "telefone_original": "(35) 99999-0000",
                "categoria": "Advocacia",
                "rua": "Rua Teste, 10 - Centro",
                "site": "Sem Site Cadastrado",
                "tem_site": "SEM SITE (OPORTUNIDADE QUENTE)",
                "link_google_maps": "https://www.google.com/maps/search/teste",
            }
        ]

    def test_slugify_removes_accents(self):
        self.assertEqual(slugify("São José do Rio Preto"), "sao-jose-do-rio-preto")

    def test_to_crm_lead_maps_required_fields(self):
        lead = to_crm_lead(self.leads[0], "advocacia")
        self.assertEqual(lead["celular"], "(35) 99999-0000")
        self.assertEqual(lead["endereco"], "Rua Teste, 10 - Centro")
        self.assertEqual(lead["site"], "Nao possui")
        self.assertEqual(lead["status_site"], "Sem site")

    def test_render_uses_stable_storage_key_and_payload(self):
        html = render_crm(
            self.leads,
            "Advocacia",
            "São José",
            self.project / "advocacia" / "itajuba.html",
        )
        self.assertIn('const STORAGE_KEY = "maps_crm_v2_advocacia_sao-jose";', html)
        self.assertIn("Silva & Lima Advocacia", html)
        self.assertIn('id="page-title">Advocacia em São José</h1>', html)
        self.assertIn('name="x-generated-at"', html)

    def test_no_publish_never_calls_git_and_updates_portal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "advocacia").mkdir()
            (root / "advocacia" / "itajuba.html").write_text(
                (self.project / "advocacia" / "itajuba.html").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "index.html").write_text(
                "<html><body><section id='workspaces'></section></body></html>",
                encoding="utf-8",
            )
            with patch("scripts.publish_extraction.publish_files") as publish:
                destination = update_site(
                    root, self.leads, "Advocacia", "Pouso Alegre", publish=False
                )
            self.assertTrue(destination.exists())
            portal = (root / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="latest-extraction"', portal)
            self.assertIn("1 leads validados", portal)
            self.assertIn("advocacia/pouso-alegre.html", portal)
            publish.assert_not_called()


if __name__ == "__main__":
    unittest.main()
