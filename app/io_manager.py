import asyncio
from sqlmodel import Session

from app import database, storage, scraper

LOCKS: dict[str, asyncio.Lock] = {}

def get_kit_lock(kit_id: str) -> asyncio.Lock:
    if kit_id not in LOCKS:
        LOCKS[kit_id] = asyncio.Lock()
    return LOCKS[kit_id]

async def database_worker(kit_id: str, db_engine) -> None:
    """
    Background worker that runs asynchronously after the API response is sent.
    Streams raw image assets and instruction PDFs to sharded disk locations,
    then updates the database flags to True upon successful download completion.
    """
    with Session(db_engine, expire_on_commit=False) as session:
        kit = session.get(database.Kit, kit_id)
        if not kit:
            return

        # Kit cover art
        if kit.cover_url and not kit.is_cover_cached:
            ext = kit.cover_url.split(".")[-1].split("?")[0] or "png"
            path = storage.resolve_kit_cover_path(kit_id, extension=ext)

            success = await scraper.download_remote_asset(kit.cover_url, path)
            if success:
                kit.is_cover_cached = True
                session.add(kit)
                session.commit()

        # Instructions
        for instruction in kit.instructions:

            # Instruction manual cover
            if instruction.cover_url and not instruction.is_cover_cached:
                ext = instruction.cover_url.split(".")[-1].split("?")[0] or "png"
                path = storage.resolve_instruction_cover_path(instruction.id, extension=ext)

                success = await scraper.download_remote_asset(instruction.cover_url, path)
                if success:
                    instruction.is_cover_cached = True
                    session.add(instruction)
                    session.commit()

            # Instruction manual PDF
            if not instruction.is_pdf_cached:
                path = storage.resolve_instruction_pdf_path(instruction.id)

                success = await scraper.download_remote_asset(instruction.pdf_url, path)
                if success:
                    instruction.is_pdf_cached = True
                    session.add(instruction)
                    session.commit()
