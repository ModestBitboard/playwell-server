import os
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse
from sqlmodel import Session, select, or_
from typing import List, Optional

from app import database, storage, scraper, io_manager

logger = logging.getLogger("playwell")

async def assure_kit_indexed(kit_id: str, background_tasks: BackgroundTasks, session: Session):
    kit = session.get(database.Kit, kit_id)
    if kit:
        logger.debug(f"Cache hit: kit #{kit_id} in SQLite index. Serving local copy.")
        return kit

    async with io_manager.get_kit_lock(kit_id):
        session.expire_all()
        kit = session.get(database.Kit, kit_id)
        if kit:
            logger.info(f"Concurrency lock: kit #{kit_id} written by parallel thread. Skipping duplicate scrape.")
            return kit


        payload = await scraper.fetch_and_scrape_kit(kit_id)
        if not payload:
            logger.warning(f"Scrape failure: #{kit_id} does not exist or was rejected by LEGO servers.")
            raise HTTPException(status_code=404, detail="Couldn't find a kit with that ID")

        db_kit = database.Kit(**payload['metadata'])
        session.add(db_kit)

        for instruction in payload['instructions']:
            db_instruction = database.Instruction(kit_id=kit_id, **instruction)
            session.add(db_instruction)

        session.commit()
        session.refresh(db_kit)

        logger.info(f"Indexing complete: Metadata for kit #{kit_id} written to database.")

        logger.info(f"Dispatching worker: background task queued to collect files for kit #{kit_id} from LEGO CDN.")
        background_tasks.add_task(io_manager.database_worker, kit_id, database.engine)

        return db_kit


kit_router = APIRouter(prefix="/kits", tags=["v1 / Kits"])
inst_router = APIRouter(prefix="/instructions", tags=["v1 / Instructions"])


@kit_router.get(
    "",
    response_model=List[database.Kit],
    summary="Search and filter cached kits",
    description="Queries the API's local database. Supports wide text searches across multiple properties or strict item lookups."
)
def list_and_filter_kits(
        search: Optional[str] = None,
        name: Optional[str] = None,
        theme: Optional[str] = None,
        age_group: Optional[str] = None,
        session: Session = Depends(database.get_session)
):
    """
    Query kits cached to the API's database.
    Supports partial matching by name and strict matches for theme and age filter.
    """
    statement = select(database.Kit)

    if search:
        # noinspection unresolved-references
        statement = statement.where(or_(
            database.Kit.name.ilike(f"%{search}%"),
            database.Kit.theme.ilike(f"%{search}%")
        ))

    if name:
        # noinspection unresolved-references
        statement = statement.where(database.Kit.name.ilike(f"%{name}%"))

    if theme:
        # noinspection unresolved-references
        statement = statement.where(database.Kit.theme.ilike(f"%{theme}%"))

    if age_group:
        statement = statement.where(database.Kit.age_group == age_group)

    return session.exec(statement).all()


@kit_router.get(
    "/{kit_id}",
    response_model=database.Kit,
    summary="Fetch metadata on kit by ID",
    description="Query the API for a kit by its ID. If it isn't found in the local database, the server will attempt to scrape it from LEGO."
)
async def get_kit(
        kit_id: str,
        background_tasks: BackgroundTasks,
        session: Session = Depends(database.get_session)
):
    return await assure_kit_indexed(kit_id, background_tasks, session)


@kit_router.get(
    "/{kit_id}/instructions",
    response_model=List[database.Instruction],
    summary="Fetch metadata on kit's instruction booklets",
    description="Get list of instructions and their metadata for a kit by its ID. If it isn't found in the local database, the server will attempt to scrape it from LEGO."
)
async def get_kit_instructions(
        kit_id: str,
        background_tasks: BackgroundTasks,
        session: Session = Depends(database.get_session)
):
    kit = await assure_kit_indexed(kit_id, background_tasks, session)
    return kit.instructions


@kit_router.get(
    "/{kit_id}/cover",
    response_class=FileResponse,
    summary="Get cover image for kit",
    description="Get the cover image for the kit. If the image is still being downloaded or isn't stored locally, redirect to LEGO's CDN."
)
async def get_kit_cover(
        kit_id: str,
        background_tasks: BackgroundTasks,
        session: Session = Depends(database.get_session)
):
    kit = await assure_kit_indexed(kit_id, background_tasks, session)

    if not kit or not kit.cover_url:
        raise HTTPException(status_code=404, detail="Asset not found. Has the kit been indexed?")

    ext = kit.cover_url.split(".")[-1].split("?")[0] or "png"
    local_path = storage.resolve_kit_cover_path(kit_id, extension=ext)
    file_exists = os.path.exists(local_path)

    if kit.is_cover_cached and not file_exists:
        kit.is_cover_cached = False
        session.add(kit)
        session.commit()

        background_tasks.add_task(io_manager.database_worker, kit_id, database.engine)

    if kit.is_cover_cached and os.path.exists(local_path):
        return FileResponse(local_path)

    # Fallback: redirect to cover URL since the image isn't cached
    return RedirectResponse(url=kit.cover_url)


@inst_router.get(
    "",
    response_model=List[database.Instruction],
    summary="Search and filter cached instruction booklets",
    description="Queries the API's local database. Supports wide text searches across multiple properties or strict item lookups."
)
def list_and_filter_instructions(
        search: Optional[str] = None,
        session: Session = Depends(database.get_session)
):
    statement = select(database.Instruction)

    if search:
        # noinspection unresolved-references
        statement = statement.where(database.Instruction.description.ilike(f"%{search}%"))

    return session.exec(statement).all()


@inst_router.get(
    "/{instruction_id}",
    response_model=database.Instruction,
    summary="Fetch metadata on instruction booklet by ID",
    description="Query the API for an instruction booklet by its ID. Requires the instruction's kit to be scraped in advance."
)
def get_instruction(
        instruction_id: str,
        session: Session = Depends(database.get_session)
):
    instruction = session.get(database.Instruction, instruction_id)
    if instruction:
        return instruction

    raise HTTPException(status_code=404, detail="Asset not found. Has the instruction been indexed?")


@inst_router.get(
    "/{instruction_id}/cover",
    response_class=FileResponse,
    summary="Get cover image for instruction booklet",
    description="Get the cover image for the instruction booklet. If the image is still being downloaded or isn't stored locally, redirect to LEGO's CDN."
)
def get_instruction_cover(
        instruction_id: str,
        background_tasks: BackgroundTasks,
        session: Session = Depends(database.get_session)
):
    instruction = session.get(database.Instruction, instruction_id)
    if not instruction or not instruction.cover_url:
        raise HTTPException(status_code=404, detail="Asset not found. Has the instruction been indexed?")

    ext = instruction.cover_url.split(".")[-1].split("?")[0] or "png"
    local_path = storage.resolve_instruction_cover_path(instruction_id, extension=ext)
    file_exists = os.path.exists(local_path)

    if instruction.is_cover_cached and not file_exists:
        logger.warning(f"Database desync: cover image for instruction #{instruction_id} does not exist in filesystem. Resolving...")

        instruction.is_cover_cached = False
        session.add(instruction)
        session.commit()

        logger.info(f"Dispatching worker: background task queued to collect missing cover image for instruction #{instruction_id} from LEGO CDN.")
        background_tasks.add_task(io_manager.database_worker, instruction.kit_id, database.engine)

    if instruction.is_cover_cached and file_exists:
        return FileResponse(local_path)

    # Fallback: redirect to cover URL since the image isn't cached
    return RedirectResponse(url=instruction.cover_url)


@inst_router.get(
    "/{instruction_id}/pdf",
    response_class=FileResponse,
    summary="Get the instruction booklet",
    description="Get the instruction booklet in PDF format. If the PDF is still being downloaded or isn't stored locally, redirect to LEGO's CDN."
)
def get_instruction_pdf(
        instruction_id: str,
        background_tasks: BackgroundTasks,
        session: Session = Depends(database.get_session)
):
    instruction = session.get(database.Instruction, instruction_id)
    if not instruction:
        raise HTTPException(status_code=404, detail="Asset not found. Has the instruction been indexed?")

    local_path = storage.resolve_instruction_pdf_path(instruction_id)
    file_exists = os.path.exists(local_path)

    # If the database is desynced from the filesystem; resync it
    if instruction.is_pdf_cached and not file_exists:
        logger.warning(f"Database desync: PDF for instruction #{instruction_id} does not exist in filesystem. Resolving...")

        instruction.is_pdf_cached = False
        session.add(instruction)
        session.commit()

        logger.info(f"Dispatching worker: background task queued to collect missing PDF for instruction #{instruction_id} from LEGO CDN.")
        background_tasks.add_task(io_manager.database_worker, instruction.kit_id, database.engine)

    if instruction.is_pdf_cached and file_exists:
        return FileResponse(
            local_path,
            media_type="application/pdf"
        )

    # Fallback: redirect to PDF URL since the PDF isn't cached
    return RedirectResponse(instruction.pdf_url)


# ----- END OF API ENDPOINTS -----
router = APIRouter()
router.include_router(kit_router)
router.include_router(inst_router)
