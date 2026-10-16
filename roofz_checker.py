"""
Roofz checker: kijkt of er nieuwe woningen in Amsterdam op roofz.eu staan
en stuurt een pushmelding via ntfy.sh.

De aanbodpagina van roofz.eu wordt met JavaScript opgebouwd, daarom laadt
het script de pagina in een echte (headless) browser via Playwright.
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

LISTING_URL = "https://roofz.eu/huur/woningen"
CITY = os.environ.get("ROOFZ_CITY", "AMSTERDAM").upper()
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
STATE_FILE = Path(__file__).with_name("seen.json")
SLUG_RE = re.compile(r"/huur/woningen/([a-z0-9-]+)$")


def fetch_listings():
    """Geeft een dict terug: slug -> {url, text} voor alle woningkaarten."""
    listings = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(locale="nl-NL")
        page.goto(LISTING_URL, wait_until="networkidle", timeout=60000)

        # Een paar keer scrollen voor het geval er meer kaarten bijladen
        last_count = -1
        for _ in range(10):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)
            count = page.locator("a[href*='/huur/woningen/']").count()
            if count == last_count:
                break
            last_count = count

        for a in page.locator("a[href*='/huur/woningen/']").all():
            href = a.get_attribute("href") or ""
            href = href.split("?")[0].rstrip("/")
            m = SLUG_RE.search(href)
            if not m or m.group(1).endswith("placeholder"):
                continue
            slug = m.group(1)
            text = " ".join(a.inner_text().split())
            entry = listings.setdefault(
                slug, {"url": f"https://roofz.eu/huur/woningen/{slug}", "text": ""}
            )
            # Een kaart heeft vaak twee links (foto en tekst), bewaar de langste tekst
            if len(text) > len(entry["text"]):
                entry["text"] = text
        browser.close()
    return listings


def notify(title, message, click_url=None):
    if not NTFY_TOPIC:
        print(f"[geen NTFY_TOPIC] {title}: {message}")
        return
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        method="POST",
    )
    req.add_header("Title", title.encode("utf-8"))
    req.add_header("Tags", "house")
    if click_url:
        req.add_header("Click", click_url)
    urllib.request.urlopen(req, timeout=30)


def main():
    listings = fetch_listings()
    if not listings:
        # Waarschijnlijk is de site veranderd. Fout teruggeven zodat GitHub mailt.
        print("Geen enkele woning gevonden, controleer of de site is veranderd.")
        sys.exit(1)

    in_city = {s: d for s, d in listings.items() if CITY in d["text"].upper()}
    print(f"{len(listings)} woningen totaal, {len(in_city)} in {CITY.title()}")

    first_run = not STATE_FILE.exists()
    seen = set() if first_run else set(json.loads(STATE_FILE.read_text()))
    new = [s for s in in_city if s not in seen]

    if first_run:
        notify(
            "Roofz checker staat aan",
            f"Er staan nu {len(in_city)} woningen in {CITY.title()} online. "
            "Vanaf nu krijg je alleen nog meldingen bij nieuwe.",
            LISTING_URL,
        )
    else:
        for slug in new:
            d = in_city[slug]
            notify(f"Nieuw op Roofz: {CITY.title()}", d["text"] or slug, d["url"])
            print(f"Melding gestuurd: {slug}")

    # Alles wat ooit gezien is blijft bewaard, zodat een woning die even
    # verdwijnt en terugkomt geen dubbele melding geeft.
    STATE_FILE.write_text(json.dumps(sorted(seen | set(in_city)), indent=1))


if __name__ == "__main__":
    main()
