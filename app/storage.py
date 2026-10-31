import os

from app.paths import CONTENTS_DIR, PLAYWELL_DATA_DIR


def init_storage() -> None:
    """
    Ensure root data and contents exist on startup.
    SHOULD BE RUN BEFORE `database.init_db()`!
    """
    os.makedirs(PLAYWELL_DATA_DIR, exist_ok=True)
    os.makedirs(CONTENTS_DIR, exist_ok=True)

def _get_shard_path(asset_id: str, filename: str) -> str:
    shard = asset_id[:2] if len(asset_id) >= 2 else "00"

    target_dir = os.path.join(CONTENTS_DIR, shard)
    os.makedirs(target_dir, exist_ok=True)

    return os.path.join(target_dir, filename)

def resolve_kit_cover_path(kit_id: str, extension: str = "png") -> str:
    """
    Returns the absolute sharded path for a kit's cover image box art.
    """
    filename = f"kit_{kit_id}_cover.{extension}"
    return _get_shard_path(kit_id, filename)

def resolve_instruction_cover_path(instruction_id: str, extension: str = "png") -> str:
    """
    Returns the absolute sharded path for an instruction's cover image.
    """
    filename = f"inst_{instruction_id}_cover.{extension}"
    return _get_shard_path(instruction_id, filename)

def resolve_instruction_pdf_path(instruction_id: str) -> str:
    """
    Returns the absolute sharded path for an instruction booklet PDF.
    """
    filename = f"inst_{instruction_id}.pdf"
    return _get_shard_path(instruction_id, filename)

