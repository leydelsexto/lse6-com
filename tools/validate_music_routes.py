from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
SITE = "https://lse6.com"
ARCHIVE = "https://lse6.org/"
CANONICAL_STATEMENT = """LEY DEL SEXTO (LSE6) es un sistema nacido de la simbiosis entre humano, tecnología y entorno.
Percepción, cultura, economia, politica, mediática, poder, lenguaje, caos, contradicción, símbolo, música y estructura dejan de existir como piezas separadas y forman un mismo organismo. Sus patrones pueden cambiar de nombre, rostro o narrativa sin perder la arquitectura que los conecta.
AlekSix LM es el cuerpo y la voz visible del sistema. La música es su lenguaje principal. Sixtem es la voz técnica del sistema y el sistema es LSE6 (LEY DEL SEXTO)
01 — LEY DEL SEXTO
02 — ZONA GRIS
03 — CLONES Y FANTASMAS
04 — NADA ME BORRA
05 — LIBRE PRISIONERO
06 — LSE6
07 — ERROR 404
Este álbum reúne siete piezas que funcionan como órganos de una misma criatura. Cada una entra por una grieta distinta, pero todas pertenecen al mismo núcleo.
Aquí, sistema y antisistema, Dios y Diablo, orden y caos, humano y máquina no son extremos separados: son fuerzas que se modifican entre sí hasta revelar aquello que ya estaba operando antes de recibir un nombre.
La Ley del Sexto no se interpreta: se es.
Antes de la idea, ya estaba la Ley.
La Ley del Sexto no cura.
Tú eliges el fuego en el que vas a arder.
LSE6 – AlekSix LM
@leydelsexto
LSE6.com · LSE6.org"""

TRACKS = [
    ("ley-del-sexto", "LEY DEL SEXTO", "pdcQBdp-xhg", "$Global:LSE6_Firma", "2026-01-06", "1.LSE6_LeyDelSexto.txt"),
    ("zona-gris", "ZONA GRIS", "Re5mvPwaoG4", "$Global:LSE6_Nivel", "2026-02-06", "2.LSE6_ZonaGris.txt"),
    ("clones-y-fantasmas", "CLONES Y FANTASMAS", "jdpOHKF_dXQ", "$Global:LSE6_Frecuencia", "2026-03-06", "3.LSE6_ClonesyFantasmas.txt"),
    ("nada-me-borra", "NADA ME BORRA", "9wk6CUoYwFo", "$Global:LSE6_motorIntencion", "2026-04-06", "4.LSE6_NadaMeBorra.txt"),
    ("libre-prisionero", "LIBRE PRISIONERO", "M0N5CoOKyEY", "$Global:LSE6_Autoridad", "2026-05-06", "5.LSE6_LibrePrisionero.txt"),
    ("lse6", "LSE6", "v40hHkTtdig", "$Global:LSE6_Sistema", "2026-06-06", "6.LSE6_LSE6.txt"),
    ("error-404", "ERROR 404", "Fafu9xC-npY", "$Global:LSE6_ID", "2026-07-07", "7.LSE6_ERROR404.txt"),
]

VIDEO_METADATA = {
    "ley-del-sexto": {
        "uploadDate": "2026-01-06T18:00:06-08:00",
        "duration": "PT3M28S",
        "durationSeconds": 208,
        "description": "Video oficial de LEY DEL SEXTO por LSE6 - AlekSix LM. El origen visible de la Ley del Sexto.",
    },
    "zona-gris": {
        "uploadDate": "2026-02-06T18:00:06-08:00",
        "duration": "PT3M40S",
        "durationSeconds": 220,
        "description": "Video oficial de ZONA GRIS por LSE6 - AlekSix LM. Quien manipula lo invisible, controla lo que se ve.",
    },
    "clones-y-fantasmas": {
        "uploadDate": "2026-03-06T18:46:36-08:00",
        "duration": "PT4M3S",
        "durationSeconds": 243,
        "description": "Video oficial de CLONES Y FANTASMAS por LSE6 - AlekSix LM. Identidad, duplicación y residuos de presencia.",
    },
    "nada-me-borra": {
        "uploadDate": "2026-04-06T20:25:16-07:00",
        "duration": "PT3M39S",
        "durationSeconds": 219,
        "description": "Video oficial de NADA ME BORRA por LSE6 - AlekSix LM ft. Docer4LM. La herida como sello de permanencia.",
    },
    "libre-prisionero": {
        "uploadDate": "2026-05-07T20:03:10-07:00",
        "duration": "PT3M58S",
        "durationSeconds": 238,
        "description": "Video oficial de LIBRE PRISIONERO por LSE6 - AlekSix LM. Ni libre ni preso: grados de esclavitud.",
    },
    "lse6": {
        "uploadDate": "2026-06-06T23:16:41-07:00",
        "duration": "PT3M45S",
        "durationSeconds": 225,
        "description": "Video oficial de LSE6 por LSE6 - AlekSix LM. La serpiente del 6 completa. SISTEMA ROTO.",
    },
    "error-404": {
        "uploadDate": "2026-07-10T18:06:06-07:00",
        "duration": "PT3M30S",
        "durationSeconds": 210,
        "description": "Video oficial de ERROR 404 por LSE6 - AlekSix LM. Cierre de la primera parte y expansión del mapa variable.",
    },
}

HTML_PAGES = {
    f"{SITE}/": ROOT / "index.html",
    f"{SITE}/lse6-leydelsexto/": ROOT / "lse6-leydelsexto" / "index.html",
    f"{SITE}/lse6-aleksixlm/": ROOT / "lse6-aleksixlm" / "index.html",
    f"{SITE}/lse6-redes-sociales/": ROOT / "lse6-redes-sociales" / "index.html",
    f"{SITE}/lse6-zona-gris/": ROOT / "lse6-zona-gris" / "index.html",
    f"{SITE}/lse6-mayo-2025/": ROOT / "lse6-mayo-2025" / "index.html",
    f"{SITE}/lse6-sixtem/": ROOT / "lse6-sixtem" / "index.html",
    f"{SITE}/mandela/": ROOT / "mandela" / "index.html",
    f"{SITE}/ontology/SystemAnomaly/": ROOT / "ontology" / "SystemAnomaly" / "index.html",
    f"{SITE}/ontology/LocalDocumentedSystem/": ROOT / "ontology" / "LocalDocumentedSystem" / "index.html",
    f"{SITE}/license/": ROOT / "license" / "index.html",
    **{f"{SITE}/{slug}/": ROOT / slug / "index.html" for slug, *_ in TRACKS},
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1 = 0
        self.meta: dict[str, str] = {}
        self.canonical: list[str] = []
        self.anchors: list[str] = []
        self.image_alts: list[str] = []
        self.json_ld: list[dict] = []
        self._json_parts: list[str] | None = None
        self.visible_text: list[str] = []
        self._nonvisible_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag in {"script", "style", "template"}:
            self._nonvisible_depth += 1
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            key = data.get("name") or data.get("property")
            if key:
                self.meta[key.lower()] = data.get("content", "")
        elif tag == "link":
            rel = data.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
        elif tag == "a":
            self.anchors.append(data.get("href", ""))
        elif tag == "img":
            self.image_alts.append(data.get("alt", ""))
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._nonvisible_depth == 0:
            self.visible_text.append(data)
        if self._json_parts is not None:
            self._json_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._json_parts is not None:
            payload = "".join(self._json_parts).strip()
            if payload:
                self.json_ld.append(json.loads(payload))
            self._json_parts = None
        if tag in {"script", "style", "template"} and self._nonvisible_depth:
            self._nonvisible_depth -= 1


def parse_page(path: Path) -> tuple[PageParser, str]:
    text = path.read_text(encoding="utf-8-sig")
    parser = PageParser()
    parser.feed(text)
    return parser, text


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError("not JPEG")
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 8 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset : offset + 2], "big")
        if marker in sof:
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        offset += length
    raise ValueError("JPEG dimensions not found")


errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate_html_surface() -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()
    incoming: dict[Path, int] = {path.resolve(): 0 for path in HTML_PAGES.values()}
    missing_links: list[str] = []
    for canonical, path in HTML_PAGES.items():
        require(path.exists(), f"Missing HTML: {path.relative_to(ROOT)}")
        if not path.exists():
            continue
        try:
            page, text = parse_page(path)
        except Exception as exc:
            errors.append(f"Invalid HTML/JSON-LD {path.relative_to(ROOT)}: {exc}")
            continue
        require(page.canonical == [canonical], f"Canonical mismatch: {path.relative_to(ROOT)} -> {page.canonical}")
        require(page.h1 == 1, f"Expected one H1: {path.relative_to(ROOT)} got {page.h1}")
        require(bool(page.title.strip()), f"Missing title: {path.relative_to(ROOT)}")
        require(bool(page.meta.get("description")), f"Missing description: {path.relative_to(ROOT)}")
        if canonical == f"{SITE}/":
            description_length = len(page.meta.get("description", ""))
            require(25 <= description_length <= 160, f"Home description length outside Bing range: {description_length}")
            require(bool(page.image_alts), "Home has no image alt inventory")
            require(all(alt.strip() for alt in page.image_alts), "Home has a missing or empty image alt")
        require("noindex" not in page.meta.get("robots", "").lower(), f"Accidental noindex: {path.relative_to(ROOT)}")
        for key in ("og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:title", "twitter:description", "twitter:image"):
            require(bool(page.meta.get(key)), f"Missing {key}: {path.relative_to(ROOT)}")
        require(page.meta.get("og:url") == canonical, f"og:url mismatch: {path.relative_to(ROOT)}")
        require(any(href.startswith(ARCHIVE) for href in page.anchors), f"Missing visible LSE6.ORG link: {path.relative_to(ROOT)}")
        require(bool(page.json_ld), f"Missing JSON-LD: {path.relative_to(ROOT)}")
        require(page.title not in titles, f"Duplicate title: {page.title}")
        require(page.meta.get("description") not in descriptions, f"Duplicate description: {path.relative_to(ROOT)}")
        titles.add(page.title)
        descriptions.add(page.meta.get("description", ""))
        require("https://github.com/LSE6leydelsexto" not in text, f"Wrong GitHub URL: {path.relative_to(ROOT)}")

        for href in page.anchors:
            parsed = urlparse(href)
            if parsed.scheme in {"mailto", "tel", "data", "javascript", "intent", "youtube"}:
                continue
            if parsed.scheme in {"http", "https"} and parsed.netloc not in {"lse6.com", "www.lse6.com"}:
                continue
            raw_path = unquote(parsed.path)
            if not raw_path:
                continue
            target = ROOT / raw_path.lstrip("/") if raw_path.startswith("/") else path.parent / raw_path
            if raw_path.endswith("/") or target.is_dir():
                target = target / "index.html"
            target = target.resolve()
            if not target.exists():
                missing_links.append(f"{path.relative_to(ROOT)} -> {href}")
            if target in incoming:
                incoming[target] += 1

        for payload in page.json_ld:
            if not isinstance(payload, dict) or "@graph" in payload:
                continue
            node_type = payload.get("@type")
            if node_type == "MusicRecording":
                require(ref_id(payload.get("byArtist")) == f"{SITE}/#artist", f"Track schema artist mismatch: {path.relative_to(ROOT)}")
            elif node_type == "WebPage":
                require(ref_id(payload.get("isPartOf")) == f"{SITE}/#website", f"WebPage schema site mismatch: {path.relative_to(ROOT)}")
                require(ref_id(payload.get("creator")) == f"{SITE}/#artist", f"WebPage schema creator mismatch: {path.relative_to(ROOT)}")

    require(not missing_links, f"Broken internal links: {missing_links[:12]}")
    home = (ROOT / "index.html").resolve()
    orphans = [path.relative_to(ROOT).as_posix() for path, count in incoming.items() if path != home and count == 0]
    require(not orphans, f"Canonical HTML pages without incoming links: {orphans}")


def validate_visible_canonical_statement() -> None:
    page, html = parse_page(ROOT / "index.html")
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    expected = normalize(CANONICAL_STATEMENT)
    visible = normalize(" ".join(page.visible_text))
    require(visible.count(expected) == 1, "Canonical LSE6 statement must appear exactly once as visible homepage text")
    section = re.search(
        r'<section class="block" id="declaracion-canonica-lse6">(?P<body>.*?)</section>',
        html,
        re.S,
    )
    require(bool(section), "Canonical LSE6 statement must use the visible semantic homepage section")
    if section:
        opening = section.group(0).split(">", 1)[0].lower()
        require(" hidden" not in opening and 'aria-hidden="true"' not in opening, "Canonical LSE6 statement cannot be hidden")
    require(expected not in normalize((ROOT / "llms.txt").read_text(encoding="utf-8-sig")), "Canonical LSE6 statement must remain visible-only, not duplicated in llms.txt")


def json_ld_graph(path: Path) -> list[dict]:
    page, _ = parse_page(path)
    for payload in page.json_ld:
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            return [node for node in payload["@graph"] if isinstance(node, dict)]
    raise ValueError(f"No JSON-LD graph in {path.relative_to(ROOT)}")


def dynamic_identity_graph() -> list[dict]:
    script = r"""
import fs from 'node:fs';
const source = fs.readFileSync(process.argv[1], 'utf8').replace(/^\uFEFF/, '');
const moduleUrl = 'data:text/javascript;base64,' + Buffer.from(source).toString('base64');
globalThis.console.log = () => {};
const identity = await import(moduleUrl);
process.stdout.write(JSON.stringify(identity.buildWebsiteJsonLd()));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script, str(ROOT / "site_identity_LSE6.js")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    payload = json.loads(result.stdout)
    return [node for node in payload.get("@graph", []) if isinstance(node, dict)]


def entity_map(graph: list[dict]) -> dict[str, dict]:
    return {node["@id"]: node for node in graph if node.get("@id")}


def ref_id(value: object) -> str | None:
    return value.get("@id") if isinstance(value, dict) else None


def ref_ids(value: object) -> set[str]:
    values = value if isinstance(value, list) else [value]
    return {item for item in (ref_id(value) for value in values) if item}


def validate_identity() -> None:
    graphs = {
        "home": json_ld_graph(ROOT / "index.html"),
        "social": json_ld_graph(ROOT / "lse6-redes-sociales" / "index.html"),
        "dynamic": dynamic_identity_graph(),
    }
    expected = {
        f"{SITE}/#website": ("WebSite", "LEY DEL SEXTO | LSE6 - AlekSix LM | Sistema LSE6 • LSEØ | LSE6.com"),
        f"{SITE}/#artist": ("MusicGroup", "LSE6 - AlekSix LM"),
        f"{SITE}/#brand": ("Brand", "LEY DEL SEXTO"),
        f"{SITE}/#system": (["SoftwareApplication", "Thing"], "LSEØ - SIXTEM"),
    }
    legacy_ids = {f"{SITE}/#organization", f"{SITE}/#law", f"{SITE}/#sixtem"}
    maps: dict[str, dict[str, dict]] = {}
    for label, graph in graphs.items():
        entities = entity_map(graph)
        maps[label] = entities
        require(not (legacy_ids & set(entities)), f"{label}: legacy entity IDs remain: {sorted(legacy_ids & set(entities))}")
        for entity_id, (kind, name) in expected.items():
            require(entity_id in entities, f"{label}: missing canonical entity {entity_id}")
            if entity_id not in entities:
                continue
            require(entities[entity_id].get("@type") == kind, f"{label}: wrong type for {entity_id}")
            require(entities[entity_id].get("name") == name, f"{label}: wrong name for {entity_id}")

    canonical_artist = maps["home"][f"{SITE}/#artist"]
    canonical_same_as = canonical_artist.get("sameAs")
    require(canonical_artist.get("alternateName") == ["LSE6", "AlekSix LM"], "home: artist aliases mix another entity")
    require(len(canonical_same_as or []) == 13, "home: expected 13 verified artist sameAs URLs")
    for label in ("social", "dynamic"):
        artist = maps[label].get(f"{SITE}/#artist", {})
        require(artist.get("alternateName") == canonical_artist.get("alternateName"), f"{label}: artist aliases diverge")
        require(artist.get("sameAs") == canonical_same_as, f"{label}: artist sameAs diverges")

    for label, entities in maps.items():
        website = entities.get(f"{SITE}/#website", {})
        artist = entities.get(f"{SITE}/#artist", {})
        brand = entities.get(f"{SITE}/#brand", {})
        system = entities.get(f"{SITE}/#system", {})
        require(ref_id(website.get("publisher")) == f"{SITE}/#artist", f"{label}: WebSite publisher must be canonical artist")
        require(ref_id(website.get("creator")) == f"{SITE}/#artist", f"{label}: WebSite creator must be canonical artist")
        require(ref_id(website.get("mainEntity")) == f"{SITE}/#artist", f"{label}: WebSite mainEntity must be canonical artist")
        require(ref_ids(website.get("about")) == {f"{SITE}/#artist", f"{SITE}/#brand", f"{SITE}/#system"}, f"{label}: WebSite about graph diverges")
        require(ref_id(artist.get("brand")) == f"{SITE}/#brand", f"{label}: artist brand relation diverges")
        require(brand.get("alternateName") == ["Ley Del Sexto", "ley del sexto"], f"{label}: brand aliases diverge")
        require("isPartOf" not in brand, f"{label}: Brand cannot be modeled as part of WebSite")
        require(ref_id(brand.get("mainEntityOfPage")) == f"{SITE}/#website", f"{label}: Brand page relation diverges")
        require(ref_id(system.get("creator")) == f"{SITE}/#artist", f"{label}: system creator diverges")
        require(ref_id(system.get("isPartOf")) == f"{SITE}/#website", f"{label}: system WebSite relation diverges")
        subjects = artist.get("subjectOf", [])
        subjects = subjects if isinstance(subjects, list) else [subjects]
        forbidden_subjects = {f"{SITE}/#brand", f"{SITE}/#system", f"{SITE}/#zona-gris"}
        require(not (forbidden_subjects & {ref_id(item) for item in subjects}), f"{label}: artist subjectOf contains a non-CreativeWork")

    home_entities = maps["home"]
    canon = home_entities.get(f"{SITE}/#canon", {})
    require(ref_id(canon.get("isPartOf")) == f"{SITE}/#website", "home: canon must be part of WebSite, not Brand")
    zone = home_entities.get(f"{SITE}/#zona-gris", {})
    require("isPartOf" not in zone, "home: DefinedTerm Zona Gris cannot use CreativeWork.isPartOf")
    require(ref_id(zone.get("mainEntityOfPage")) == f"{SITE}/#website", "home: Zona Gris page relation diverges")
    for node in graphs["home"]:
        if node.get("@type") == "MusicRecording":
            artists = node.get("byArtist")
            artists = artists if isinstance(artists, list) else [artists]
            require(any(ref_id(artist) == f"{SITE}/#artist" for artist in artists), f"Track missing canonical artist: {node.get('@id')}")


def validate_tracks() -> None:
    links = json.loads((ROOT / "music-links.json").read_text(encoding="utf-8-sig"))
    catalog = json.loads((ROOT / "lse6-aleksixlm" / "index.json").read_text(encoding="utf-8-sig"))
    pulse = json.loads((ROOT / "machine-pulse.json").read_text(encoding="utf-8-sig"))
    link_tracks = links.get("tracks", [])
    released = catalog.get("released_tracks", [])
    pulse_tracks = pulse.get("canon", [])
    require(len(link_tracks) == len(released) == len(pulse_tracks) == 7, "Machine catalogs must contain seven released tracks")
    require(not catalog.get("planned_tracks"), "Catalog still contains planned tracks")
    if not (len(link_tracks) == len(released) == len(pulse_tracks) == 7):
        return
    redirects = (ROOT / "_redirects").read_text(encoding="utf-8-sig")
    home = (ROOT / "index.html").read_text(encoding="utf-8-sig")
    hub = (ROOT / "lse6-aleksixlm" / "index.html").read_text(encoding="utf-8-sig")
    require(pulse.get("timestamps", {}).get("lastmod") == "2026-08-10", "machine-pulse lastmod is stale")
    require(pulse.get("dataset_structured_data", {}).get("date_modified") == "2026-08-10", "machine-pulse date_modified is stale")
    require('"dateModified": "2026-08-10"' in home, "Homepage dataset dateModified is stale")
    for index, (slug, title, video_id, variable, date, lyrics_file) in enumerate(TRACKS):
        route_url = f"{SITE}/{slug}/"
        youtube = f"https://youtube.com/watch?v={video_id}"
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        page_path = ROOT / slug / "index.html"
        parsed_page, page = parse_page(page_path)
        lyrics_path = ROOT / "lse6-aleksixlm" / "lse6-pdf" / lyrics_file
        require(f'href="/{slug}/"' in home, f"Homepage missing route: {slug}")
        require(f"/{slug} /{slug}/ 301" in redirects, f"Missing slash redirect: {slug}")
        require(not re.search(rf"^/{re.escape(slug)}/\s+https?://", redirects, re.M), f"Canonical route redirects off-site: {slug}")
        for token in (route_url, video_id, "ABRIR EN LA APP DE YOUTUBE", "intent://youtube.com/watch?v=", "youtube://watch?v=", ARCHIVE, lyrics_file):
            require(token in page, f"{slug}: missing {token}")
        iframe_pattern = rf'<iframe\s+[^>]*src="{re.escape(embed_url)}"[^>]*allowfullscreen'
        require(bool(re.search(iframe_pattern, page)), f"{slug}: missing visible YouTube watch player")
        recordings = [item for item in parsed_page.json_ld if item.get("@type") == "MusicRecording"]
        require(len(recordings) == 1, f"{slug}: expected one MusicRecording JSON-LD object")
        if recordings:
            video = recordings[0].get("subjectOf", {})
            expected = VIDEO_METADATA[slug]
            require(video.get("@type") == "VideoObject", f"{slug}: subjectOf is not VideoObject")
            require(video.get("@id") == f"{route_url}#video", f"{slug}: VideoObject @id mismatch")
            require(video.get("embedUrl") == embed_url, f"{slug}: VideoObject embedUrl mismatch")
            require(video.get("uploadDate") == expected["uploadDate"], f"{slug}: VideoObject uploadDate mismatch")
            require(video.get("duration") == expected["duration"], f"{slug}: VideoObject duration mismatch")
            require(video.get("description") == expected["description"], f"{slug}: VideoObject description mismatch")
            require(video.get("thumbnailUrl") == f"{SITE}/lse6-assets/youtube-thumbnails/{video_id}.jpg", f"{slug}: VideoObject thumbnail mismatch")
            require(video.get("inLanguage") == "es-MX", f"{slug}: VideoObject language mismatch")
            require(expected["description"] in " ".join(parsed_page.visible_text), f"{slug}: VideoObject description is not visible")
        require(lyrics_path.exists(), f"Missing lyrics file: {lyrics_file}")
        thumb = ROOT / "lse6-assets" / "youtube-thumbnails" / f"{video_id}.jpg"
        try:
            require(jpeg_dimensions(thumb) == (1280, 720), f"Wrong thumbnail dimensions: {video_id}")
        except Exception as exc:
            errors.append(f"Invalid thumbnail {video_id}: {exc}")
        for source, label in ((link_tracks, "music-links"), (released, "catalog"), (pulse_tracks, "machine-pulse")):
            if index >= len(source):
                continue
            item = source[index]
            require(item.get("status", "").lower() in {"released", "lanzada"}, f"{label} status mismatch: {title}")
            require(item.get("variable") == variable, f"{label} variable mismatch: {title}")
        require(link_tracks[index].get("title") == title, f"music-links title mismatch: {title}")
        require(released[index].get("slug") == slug, f"Catalog slug mismatch: {title}")
        require(pulse_tracks[index].get("track") == title, f"Machine pulse title mismatch: {title}")
        require(link_tracks[index].get("release_date") == date, f"music-links date mismatch: {title}")
        require(released[index].get("landing_url") == route_url, f"Catalog landing mismatch: {title}")
        require(video_id in released[index].get("youtube_url", ""), f"Catalog video mismatch: {title}")
        require(video_id in pulse_tracks[index].get("url", ""), f"Machine pulse video mismatch: {title}")
        require(video_id in hub, f"Visible canon hub video missing: {title}")


def validate_crawl_contract() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8-sig")
    require(f"Sitemap: {SITE}/sitemap.xml" in robots, "robots missing main sitemap")
    require(f"Sitemap: {SITE}/sitemap-images.xml" in robots, "robots missing image sitemap")
    require(f"Sitemap: {SITE}/sitemap-video.xml" in robots, "robots missing video sitemap")
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [node.text for node in sitemap.findall("s:url/s:loc", ns)]
    require(set(HTML_PAGES).issubset(set(locations)), "Main sitemap is missing required canonical HTML pages")
    require(len(locations) == len(set(locations)), "Duplicate URL in main sitemap")
    lastmods = {
        node.findtext("s:loc", default="", namespaces=ns):
        node.findtext("s:lastmod", default="", namespaces=ns)
        for node in sitemap.findall("s:url", ns)
    }
    for slug, *_ in TRACKS:
        value = lastmods.get(f"{SITE}/{slug}/", "")
        require(not value or value == "2026-08-21", f"Track sitemap lastmod is stale: {slug}")
    image_root = ET.parse(ROOT / "sitemap-images.xml").getroot()
    ins = {"s": ns["s"], "i": "http://www.google.com/schemas/sitemap-image/1.1"}
    hosts = [node.text for node in image_root.findall("s:url/s:loc", ins)]
    images = [node.text for node in image_root.findall("s:url/i:image/i:loc", ins)]
    require(len(hosts) == 8 and len(set(hosts)) == 8, "Image sitemap must have home plus seven track pages")
    require(len(images) == 28 and len(set(images)) == 28, "Image sitemap must contain 28 unique images")
    for url in hosts:
        require(url in HTML_PAGES, f"Image sitemap host is not canonical HTML: {url}")
    for url in images:
        parsed = urlparse(url)
        require(parsed.netloc == "lse6.com", f"External image in sitemap: {url}")
        require((ROOT / parsed.path.lstrip("/")).exists(), f"Missing sitemap image: {url}")
    video_root = ET.parse(ROOT / "sitemap-video.xml").getroot()
    vns = {"s": ns["s"], "v": "http://www.google.com/schemas/sitemap-video/1.1"}
    video_entries = video_root.findall("s:url", vns)
    require(len(video_entries) == 7, "Video sitemap must contain seven watch pages")
    video_hosts: list[str] = []
    track_by_url = {f"{SITE}/{slug}/": (slug, title, video_id) for slug, title, video_id, *_ in TRACKS}
    for entry in video_entries:
        host = entry.findtext("s:loc", default="", namespaces=vns)
        video_hosts.append(host)
        require(host in track_by_url, f"Unexpected video sitemap host: {host}")
        if host not in track_by_url:
            continue
        slug, title, video_id = track_by_url[host]
        expected = VIDEO_METADATA[slug]
        require(entry.findtext("v:video/v:thumbnail_loc", default="", namespaces=vns) == f"{SITE}/lse6-assets/youtube-thumbnails/{video_id}.jpg", f"Video sitemap thumbnail mismatch: {slug}")
        require(entry.findtext("v:video/v:title", default="", namespaces=vns) == f"{title} · video oficial", f"Video sitemap title mismatch: {slug}")
        require(entry.findtext("v:video/v:description", default="", namespaces=vns) == expected["description"], f"Video sitemap description mismatch: {slug}")
        require(entry.findtext("v:video/v:player_loc", default="", namespaces=vns) == f"https://www.youtube.com/embed/{video_id}", f"Video sitemap player mismatch: {slug}")
        require(entry.findtext("v:video/v:duration", default="", namespaces=vns) == str(expected["durationSeconds"]), f"Video sitemap duration mismatch: {slug}")
        require(entry.findtext("v:video/v:publication_date", default="", namespaces=vns) == expected["uploadDate"], f"Video sitemap publication date mismatch: {slug}")
    require(len(video_hosts) == len(set(video_hosts)), "Duplicate watch page in video sitemap")
    not_found, not_found_text = parse_page(ROOT / "404.html")
    require("noindex" in not_found.meta.get("robots", "").lower(), "404.html must be noindex")
    require(not not_found.canonical, "404.html must not canonicalize to home")
    require("href=\"/\"" in not_found_text, "404.html needs recovery link")
    redirects = (ROOT / "_redirects").read_text(encoding="utf-8-sig")
    require("301!" not in redirects and not re.search(r"^https?://", redirects, re.M), "Unsupported Cloudflare Pages redirect syntax")
    require("/favicon.ico /favicon.png 301" in redirects, "Missing favicon redirect")
    require("/lse6-aleksixlm/machine-pulse.json /machine-pulse.json 301" in redirects, "Missing machine-pulse redirect")
    headers = (ROOT / "_headers").read_text(encoding="utf-8-sig")
    require("/site.webmanifest\n  X-Robots-Tag: noindex, nofollow" in headers, "site.webmanifest must be noindex")
    require("https://:project.pages.dev/*\n  X-Robots-Tag: noindex, nofollow" in headers, "Stable Pages host must be noindex")
    require("https://:version.:project.pages.dev/*\n  X-Robots-Tag: noindex, nofollow" in headers, "Preview Pages hosts must be noindex")
    thumbnail_rule = re.search(r"/lse6-assets/youtube-thumbnails/\*\s+(?P<body>(?:[^\n]+\n?)*)", headers)
    require(bool(thumbnail_rule) and "immutable" not in thumbnail_rule.group("body").split("\n\n", 1)[0], "YouTube thumbnails must not be immutable")
    for ghost in ("license/index.json", "ontology/SystemAnomaly/index.json", "ontology/LocalDocumentedSystem/index.json"):
        require(ghost not in (ROOT / ghost.removesuffix("index.json") / "index.html").read_text(encoding="utf-8-sig"), f"Ghost alternate remains: {ghost}")


validate_html_surface()
validate_visible_canonical_statement()
validate_identity()
validate_tracks()
validate_crawl_contract()

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("VALIDATION PASSED")
print("html=18 h1=18 schema=coherent tracks=7 thumbnails=7 main_sitemap=18 image_sitemap=28 video_sitemap=7 soft404_guard=1")
