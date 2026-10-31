import httpx
import aiofiles
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

# Immutable headers
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/130.0",
    "Accept-Language": "en-US,en;q=0.9"
}
LEGO_URL = "https://www.lego.com/en-us/service/building-instructions/"

def parse_metadata(soup: BeautifulSoup):
    info_container = soup.select_one("section[class^='_setId__setInfoContainer__MZxiL']")
    if not info_container:
        return None

    elements = info_container.select("[class^='ds-heading-lg _setId__productDetails__aQ9pA']")

    theme = elements[0].text
    name = elements[1].text
    year = int(elements[3].text.removeprefix('Year: '))

    _info = elements[2].text.split(' | ')

    age_group = _info[0]
    kit_id = _info[1].removeprefix('#')
    pieces = int(_info[2].removesuffix(' pieces'))

    cover_src = soup.select_one('picture[data-test="set-image"] source')

    cover_url = None
    if cover_src:
        cover_url = str(cover_src['srcset']).split('?', 1)[0]

    return {
        "id": kit_id,
        "name": name,
        "theme": theme,
        "year": year,
        "age_group": age_group,
        "pieces": pieces,
        "cover_url": cover_url,
    }

def parse_instructions(soup: BeautifulSoup):
    instructions = []

    ul_container = soup.select_one("ul[class^='_setId__instructionsList']")
    if not ul_container:
        return instructions

    cards = ul_container.find_all("li", recursive=False)

    for card in cards:
        # Booklet description
        title_el = card.find('h3')
        description = title_el.get_text(strip=True) if title_el else None

        # PDF URL
        pdf_anchor = card.find("a", href=True)
        if not pdf_anchor or ".pdf" not in str(pdf_anchor["href"]).lower():
            continue
        pdf_url = str(pdf_anchor["href"])

        # Cover URL
        cover_url = None
        source_tag = card.select_one("picture source")
        if source_tag and source_tag.has_attr("srcset"):
            cover_url = str(source_tag["srcset"]).split("?", 1)[0]

        # File size
        size_mb = None
        p_tag = card.find("p")
        if p_tag:
            size_text = p_tag.get_text(strip=True).removesuffix(" (PDF)")
            # I'm assuming instructions will always be measured within megabytes.
            size_mb = float(size_text.replace("MB", ""))

        # Building Instruction Item Number
        instruction_id = pdf_url.split('/')[-1].replace('.pdf', '')

        instructions.append({
            "id": instruction_id,
            "description": description,
            "pdf_url": pdf_url,
            "cover_url": cover_url,
            "size_mb": size_mb
        })

    return instructions

async def fetch_and_scrape_kit(kit_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches HTML using HTTPX and feeds response to helpers for parsing.
    :return: Validated layout or `None` if request isn't OK.
    """

    url = LEGO_URL + kit_id

    async with httpx.AsyncClient(headers=REQUEST_HEADERS, timeout=5.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            metadata = parse_metadata(soup)
            instructions = parse_instructions(soup)

            return {
                "metadata": metadata,
                "instructions": instructions
            }

        except httpx.RequestError:
            return None

async def download_remote_asset(url: str, dest_path: str) -> bool:
    """
    Asynchronously download a file from a remote URL directly to disk.
    """
    try:
        async with httpx.AsyncClient(headers=REQUEST_HEADERS, follow_redirects=True, timeout=15.0) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return False

                async with aiofiles.open(dest_path, "wb") as f:
                    # using 4KB chunk streaming to keep memory usage minimal
                    async for chunk in response.aiter_bytes(chunk_size=4096):
                        await f.write(chunk)

                return True

    except Exception as e:
        print(f"ERROR: Background stream failed for {url} -> {e}")
        return False
