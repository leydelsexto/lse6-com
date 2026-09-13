#!/usr/bin/env python3
"""Require every public LSE6.org bridge page on lse6.com to be in both sitemaps."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://lse6.com"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def locs(name: str) -> list[str]:
    root = ET.parse(ROOT / name).getroot()
    return [n.text.strip() for n in root.findall(".//s:loc", NS) if n.text and n.text.strip()]


def main() -> int:
    bridge_dirs = sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and p.name.startswith("lse6-org") and (p / "index.html").exists()
    )
    expected = {f"{SITE}/{p.name}/" for p in bridge_dirs}
    bridge = locs("sitemap-lse6-org.xml")
    main_urls = set(locs("sitemap.xml"))
    bridge_set = set(bridge)
    errors = []
    if len(bridge) != len(bridge_set):
        errors.append("duplicate bridge URLs")
    if bridge_set != expected:
        errors.append(f"bridge coverage differs: missing={sorted(expected - bridge_set)} extra={sorted(bridge_set - expected)}")
    if not bridge_set.issubset(main_urls):
        errors.append(f"bridge pages absent from main sitemap: {sorted(bridge_set - main_urls)}")
    external = sorted(url for url in bridge_set if not url.startswith(f"{SITE}/"))
    if external:
        errors.append(f"cross-host URLs would collide with native lse6.org ownership: {external}")
    if errors:
        print("BRIDGE SITEMAP FAILED")
        for error in errors:
            print(" -", error)
        return 1
    print(f"BRIDGE SITEMAP OK pages={len(expected)} native_host_owned_by_lse6.org=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
