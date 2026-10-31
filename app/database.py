from sqlmodel import (
    SQLModel, Field, Relationship,
    create_engine, Session
)
from typing import Optional, List, Generator
import os

from app.paths import DB_PATH

class Kit(SQLModel, table=True):
    __tablename__ = 'kits'

    id: str = Field(primary_key=True, index=True, description="The official LEGO item number (e.g., '71374').")
    name: str = Field(index=True, description="The en_US name of the LEGO set within the product catalog.")
    theme: str = Field(index=True, description="The theme group designation (e.g., 'LEGO® Icons').")
    pieces: Optional[int] = Field(default=None, description="The total pieces the kit contains, excluding spare parts.")
    year: Optional[int] = Field(default=None, description="The official commercial market release year.")
    age_group: Optional[str] = Field(default=None, description="The targeted age demographic (e.g. '18+', '7-12').")
    cover_url: Optional[str] = Field(default=None, description="URL for the cover image on LEGO's CDN.")
    is_cover_cached: bool = Field(default=False, description="Indicates if the cover image has been added to the local server storage.")

    instructions: List['Instruction'] = Relationship(
        back_populates='kit',
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    model_config = {
        "json_schema_extra": {
            # generated via beekeeper
            "examples": [{"id":"10334","name":"Retro Radio","theme":"LEGO® Icons","pieces":906,"year":2024,"age_group":"18+","cover_url":"https://www.lego.com/cdn/product-assets/product.img.pri/10334_Prod.png","is_cover_cached":True}]
        }
    }

class Instruction(SQLModel, table=True):
    __tablename__ = 'instructions'

    id: str = Field(primary_key=True, description="The official LEGO Building Instruction design identifier, typically printed on the back of the booklet.")
    kit_id: str = Field(foreign_key="kits.id", ondelete="CASCADE", description="The parent kit ID this booklet is tied to.")
    description: str = Field(description="The booklet-specific printed title description (e.g., 'Nintendo Entertainment System™ (1/2)').")
    size_mb: Optional[float] = Field(default=None, description="The size of the booklet PDF according to LEGO, in megabytes.")
    pdf_url: str = Field(description="URL for the booklet PDF on LEGO's CDN.")
    cover_url: Optional[str] = Field(default=None, description="URL for the booklet's cover image on LEGO's CDN.")
    is_pdf_cached: bool = Field(default=False, description="Indicates if the booklet PDF has been added to the local server storage.")
    is_cover_cached: bool = Field(default=False, description="Indicates if the booklet cover image has been added to the local server storage.")

    kit: Optional[Kit] = Relationship(back_populates="instructions")

    model_config = {
        "json_schema_extra": {
            # generated via beekeeper
            "examples": [{"id":"6521147","kit_id":"10334","description":"Retro Radio (1/1)","size_mb":72.69,"pdf_url":"https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6521147.pdf","cover_url":"https://www.lego.com/cdn/product-assets/product.bi.core.img/6521147.png","is_pdf_cached":True,"is_cover_cached":True}]
        }
    }


# Resolve storage paths
# noinspection bad-argument-type
DATABASE_URI_DEFAULT = f"sqlite:///{DB_PATH}"
DATABASE_URI = os.environ.get('PLAYWELL_DB_URI', DATABASE_URI_DEFAULT)

# Create database engine
engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})

def init_db():
    """
    Initialize database
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Session generator for FastAPI.
    """
    with Session(engine) as session:
        yield session
