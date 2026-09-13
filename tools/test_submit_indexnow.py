import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

MODULE_PATH = Path(__file__).with_name("submit_indexnow.py")
SPEC = importlib.util.spec_from_file_location("submit_indexnow", MODULE_PATH)
assert SPEC and SPEC.loader
INDEXNOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEXNOW)
ROOT = MODULE_PATH.resolve().parents[1]
SITE = "https://lse6.com"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
INS = {**NS, "i": "http://www.google.com/schemas/sitemap-image/1.1"}
VNS = {**NS, "v": "http://www.google.com/schemas/sitemap-video/1.1"}
EXCLUDED_PREFIXES = (".git/", ".github/", "tools/")
EXCLUDED_FILES = {
    ".gitattributes", ".gitignore", ".htaccess", "_headers", "_redirects", "404.html",
    "lse6-assets/public-media/README_REEMPLAZA_ARCHIVOS.txt",
    "lse6-mayo-2025/lse6-pdf/LSE6_MAYO_2025_EXTRA.txt",
}
PUBLIC_SUFFIXES = {".gif", ".html", ".ico", ".jpeg", ".jpg", ".js", ".json", ".mp4", ".pdf", ".png", ".svg", ".txt", ".webm", ".webmanifest", ".webp"}
IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".webm"}


def public_file(path):
    rel = path.relative_to(ROOT).as_posix()
    return path.is_file() and rel not in EXCLUDED_FILES and not rel.startswith(EXCLUDED_PREFIXES) and path.suffix.lower() in PUBLIC_SUFFIXES


def public_url(path):
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + quote(rel[:-10], safe="/-._~")
    return SITE + "/" + quote(rel, safe="/-._~")


class IndexNowTests(unittest.TestCase):
    def test_master_sitemap_covers_every_public_repo_route(self):
        active = INDEXNOW.current_urls()
        expected = {public_url(p) for p in ROOT.rglob("*") if public_file(p)}
        missing = expected - active
        self.assertFalse(missing, f"Public URLs missing from sitemap.xml: {sorted(missing)}")
        for forbidden in EXCLUDED_FILES:
            self.assertNotIn(SITE + "/" + quote(forbidden, safe="/-._~"), active)

    def test_all_specialized_sitemaps_cover_their_public_assets(self):
        image_root = ET.parse(ROOT / "sitemap-images.xml").getroot()
        image_urls = {n.text.strip() for n in image_root.findall("s:url/i:image/i:loc", INS) if n.text}
        expected_images = {public_url(p) for p in ROOT.rglob("*") if public_file(p) and p.suffix.lower() in IMAGE_SUFFIXES}
        self.assertFalse(expected_images - image_urls, f"Images missing from sitemap-images.xml: {sorted(expected_images-image_urls)}")

        video_root = ET.parse(ROOT / "sitemap-video.xml").getroot()
        content_urls = {n.text.strip() for n in video_root.findall("s:url/v:video/v:content_loc", VNS) if n.text}
        expected_videos = {public_url(p) for p in ROOT.rglob("*") if public_file(p) and p.suffix.lower() in VIDEO_SUFFIXES}
        self.assertFalse(expected_videos - content_urls, f"Local videos missing from sitemap-video.xml: {sorted(expected_videos-content_urls)}")
        video_hosts = {n.text.strip() for n in video_root.findall("s:url/s:loc", VNS) if n.text}
        catalog = json.loads((ROOT / "music-links.json").read_text(encoding="utf-8-sig"))
        released = {t["slug"] for t in catalog.get("tracks", []) if t.get("status") == "released" and t.get("slug")}
        self.assertFalse(released - video_hosts, f"Released track pages missing from sitemap-video.xml: {sorted(released-video_hosts)}")

        org_root = ET.parse(ROOT / "sitemap-lse6-org.xml").getroot()
        org_urls = {n.text.strip() for n in org_root.findall("s:url/s:loc", NS) if n.text}
        expected_org = {public_url(p) for p in ROOT.glob("lse6-org*/index.html")}
        self.assertEqual(expected_org, org_urls)

    def test_robots_declares_every_sitemap(self):
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8-sig")
        for name in ("sitemap.xml", "sitemap-images.xml", "sitemap-video.xml", "sitemap-lse6-org.xml"):
            self.assertIn(f"Sitemap: {SITE}/{name}", robots)

    def test_single_canonical_page_change_is_targeted(self):
        active = INDEXNOW.current_urls()
        selected = INDEXNOW.select_changed_urls({"ley-del-sexto/index.html"}, active, set())
        self.assertEqual({"https://lse6.com/ley-del-sexto/"}, selected)

    def test_global_crawl_change_submits_all_public_urls(self):
        active = INDEXNOW.current_urls()
        selected = INDEXNOW.select_changed_urls({"robots.txt"}, active, set())
        self.assertEqual(active, selected)

    def test_tooling_change_does_not_submit_public_urls(self):
        active = INDEXNOW.current_urls()
        selected = INDEXNOW.select_changed_urls({"tools/validate_music_routes.py"}, active, set())
        self.assertEqual(set(), selected)

    def test_key_file_matches_indexnow_contract(self):
        self.assertEqual("LSE6-3001FEC3240DA9D0-616-666", INDEXNOW.read_key())


if __name__ == "__main__":
    unittest.main()
