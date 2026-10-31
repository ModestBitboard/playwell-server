<p align="center">
  <img src="assets/logo.svg" alt="Playwell API Logo" width="100px"/>
</p>

## Playwell API
Playwell API is a (mostly) stateless, read-through caching REST API engine written in Python and FastAPI. It scrapes LEGO.com for metadata, images, and instructions, and stores the scraped data in a SQLite database for easy access. It presents all of this information as an easy-to-use REST API and wrappers for various languages.

## Features
* **Stateless Laziness (Read-Through Caching):** If a resource is requested that isn't stored locally, the server instantly enters a synchronized concurrency lock, scrapes LEGO's website, and adds collected information to the database; all before forwarding that info to the client.
* **Self-Healing File Boundary Hooks:** Automatically detects filesystem modifications or complete cache wipes on active HTTP requests. If a file is missing but marked as cached, SQLite flags self-repair dynamically and trigger background downloaders.
* **Chunk-Based Asynchronous Streaming:** Downloads heavy PDF assets chunk-by-chunk using non-blocking background workers (httpx + aiofiles), keeping memory and CPU footprint minimal inside containers.
* **Prefix File Sharding:** Automatically groups file caches based on the first two numeric (or potentially alphanumeric) characters of the identifiers to prevent file clashing and ensure filesystem scaling performance.

## API Blueprint Overview
All primary endpoints reside behind a versioned namespace prefix to prevent future issues.
While more than half of the endpoints aren't truly stateless, as long as a client has triggered a scrape on that particular resource, it should act statelessly from then on, as it gets cached to the database.

### Stateless
* `GET /v1/kits/{kit_id}` -- Fetches full metadata. Scrapes and populates database dynamically on cache misses.
* `GET /v1/kits/{kit_id}/instructions` -- Lists booklet entries and their file sizes available for a specific kit.
* `GET /v1/kits/{kit_id}/cover` -- Streams the kit cover image (Redirects to live CDN if not present in database).

### Requires local database entries
* `GET /v1/kits` -- Search and deep filter sets present in the database via strings, themes, or age brackets.
* `GET /v1/instructions` -- Search instruction booklets present in the database via their description.
* `GET /v1/instructions/{instruction_id}` -- Fetch full metadata on a specified booklet.
* `GET /v1/instructions/{instruction_id}/pdf` -- Streams PDF documents directly.
* `GET /v1/instructions/{instruction_id}/cover` -- Streams the booklet's cover image.

You can also view these endpoints and their usage information at `/docs` or `/redoc` for Swagger UI and ReDoc respectively.

## License
Distributed under the GPLv3 License. See [LICENSE](./LICENSE) for more information.

## Support
If you liked this project, go ahead and give it a star! And if it really helped you out, consider sending me a tip.

> **BTC**: `bc1q8tmwuyxpgkuptwu3mn4ryaemp3umvwcc0e5nkk`
