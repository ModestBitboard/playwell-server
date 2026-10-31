import os
import shutil
import pytest
from tempfile import TemporaryDirectory

from app import storage

@pytest.fixture(autouse=True)
def cleanup_test_folders():
    with TemporaryDirectory() as tmpdir:
        storage.CONTENTS_DIR = os.path.join(tmpdir, "contents")

        yield

def test_storage_init_creates_directories():
    if os.path.exists(storage.CONTENTS_DIR):
        shutil.rmtree(storage.CONTENTS_DIR)

    storage.init_storage()
    assert os.path.exists(storage.PLAYWELL_DATA_DIR)
    assert os.path.exists(storage.CONTENTS_DIR)

def test_shard_path_generation_and_prefix_slicing():
    # Normal case - Standard numeric ID
    pdf_path = storage.resolve_instruction_pdf_path("6336693")
    assert "contents/63/inst_6336693.pdf" in pdf_path.replace("\\", "/")
    assert os.path.exists(os.path.dirname(pdf_path))

    # Edge case - Text-included, non-PNG cover file
    weird_id = "17101_A_Frankie the Cat"
    weird_path = storage.resolve_instruction_cover_path(weird_id, "jpg")
    assert "contents/17/inst_17101_A_Frankie the Cat_cover.jpg" in weird_path.replace("\\", "/")
    assert os.path.exists(os.path.dirname(weird_path))
