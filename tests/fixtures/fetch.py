"""
Update the offline cache of HTML files by downloading live copies
"""
import httpx

from app.scraper import REQUEST_HEADERS, LEGO_URL

TEST_IDS = { '71374', '10334', '17101', '21134' }

with httpx.Client(headers=REQUEST_HEADERS, timeout=5.0) as client:
    for kit_id in TEST_IDS:
        resp = client.get(LEGO_URL + kit_id)
        file = kit_id + '_page.html'

        # noinspection unresolved-references
        if resp.status_code != 200:
            print("Failed to fetch page:", file)
            continue

        with open(file, 'wb') as f:
            f.write(resp.content)

        print("Updated cached page:", file)
