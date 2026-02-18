"""Fetch tree species thumbnail URLs from the Wikipedia API."""

from __future__ import annotations

import time

import httpx

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "TreeManagerETL/1.0 (https://github.com/tree-manager; contact@tree-manager.dev) httpx"
REQUEST_DELAY = 0.15

# Species whose scientific name doesn't match their Wikipedia article title
ALTERNATE_TITLES: dict[str, str] = {
    "Prunus dulcis": "Almond",
    "Malus domestica": "Apple",
    "Ceratonia siliqua": "Carob",
    "Ficus carica": "Fig",
    "Pyrus communis subsp. sativa": "Pyrus communis",
    "Gleditsia triacanthos": "Honey locust",
    "Cryptomeria japonica": "Cryptomeria",
    "Ziziphus jujuba": "Jujube",
    "Citrus x limon": "Lemon",
    "Citrus x sinensis": "Orange (fruit)",
    "Platanus x hispanica": "London plane",
    "Eriobotrya japonica": "Loquat",
    "Nerium oleander": "Nerium",
    "Olea europaea": "Olive",
    "Punica granatum": "Pomegranate",
    "Cydonia oblonga": "Quince",
    "Hippophae rhamnoides": "Sea buckthorn",
    "Sorbus domestica": "Service tree",
    "Pinus pinea": "Stone pine",
    "Castanea sativa": "Sweet chestnut",
    "Sorbus torminalis": "Wild service tree",
}


def _fetch_thumbnail(client: httpx.Client, title: str) -> str:
    """Fetch thumbnail URL from Wikipedia for a given page title."""
    resp = client.get(
        WIKIPEDIA_API,
        params={
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "format": "json",
            "pithumbsize": 400,
        },
    )
    if resp.status_code != 200:
        return ""
    pages = resp.json().get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    return page.get("thumbnail", {}).get("source", "")


def fetch_species_images(species_list: list[dict[str, object]]) -> list[dict[str, object]]:
    """Enrich species records with Wikipedia thumbnail URLs."""
    client = httpx.Client(
        timeout=10,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )
    found = 0

    for species in species_list:
        sci_name = str(species["scientific_name"])

        # Try scientific name first, then alternate title
        titles_to_try = [sci_name]
        if sci_name in ALTERNATE_TITLES:
            titles_to_try.append(ALTERNATE_TITLES[sci_name])

        thumb = ""
        for title in titles_to_try:
            thumb = _fetch_thumbnail(client, title)
            if thumb:
                break
            time.sleep(REQUEST_DELAY)

        if thumb:
            species["image_url"] = thumb
            found += 1

        time.sleep(REQUEST_DELAY)

    client.close()
    print(f"Fetched images for {found}/{len(species_list)} species.")
    return species_list
