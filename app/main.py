from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pydantic import BaseModel, HttpUrl, Field
from typing import List

from app.paths import LOGO_PATH
from app.logger import init_logger
from app.storage import init_storage
from app.database import init_db

# noinspection unused-parameter, shadowing-names
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    init_storage()
    init_db()

    yield

tags = [
    {
        "name": "Root",
        "description": "Information about the service itself."
    },
    {
        "name": "v1 / Kits",
        "description": "Operations related to LEGO set metadata."
    },
    {
        "name": "v1 / Instructions",
        "description": "Operations related to LEGO set instruction booklets and their metadata."
    }
]

app = FastAPI(
    title="Playwell API",
    description="A (mostly) stateless REST API server for LEGO kit information and instructions.\n\n**Source Code:** [GitHub Repository](https://github.com/ModestBitboard/playwell-server)",
    version="1.0.1",
    lifespan=lifespan,
    license_info={
        "name": "GNU General Public License v3.0 (GPLv3)",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html"
    },
    docs_url=None,
    redoc_url=None,
    openapi_tags=tags
)

class APIEndpoints(BaseModel):
    openapi_spec: HttpUrl = Field(description="The absolute URL path to the raw JSON OpenAPI specification.")
    swagger_ui: HttpUrl = Field(description="The absolute URL path to the Swagger UI interactive documentation.")
    redoc_ui: HttpUrl = Field(description="The absolute URL path to the ReDoc UI documentation.")

class ServerRootResponse(BaseModel):
    """
    Structured OpenAPI response contract emitted by the root handshake route.
    Meant to be used by client apps and SDK wrappers to negotiate version compatibility.
    """
    status: str = Field(default="up", description="The current operational health of the server. Should always be 'up'.")
    service: str = Field(description="The server's service name. Same as what appears in OpenAPI specs.")
    description: str = Field(description="A brief summary of the service.")
    developer: str = Field(description="The developer who created and/or maintains the service.")
    system_version: str = Field(description="The version number for the running service.")
    available_api_versions: List[str] = Field(description="A list of all currently supported API versions.")
    recommended_api_version: str = Field(description="Which API version the client should use, if it supports more than one.")
    source_code: HttpUrl = Field(description="The upstream public repository for the service.")
    container_registry: str = Field(description="The public registry path for running the service as a container.")
    endpoints: APIEndpoints = Field(description="The location of internal API documentation.")

@app.get(
    "/",
    tags=["Root"],
    response_model=ServerRootResponse,
    summary="Server information handshake",
    description="Returns runtime application specifications and metadata."
)
def root_info(request: Request):
    base_url = str(request.base_url).rstrip("/")

    return {
        "status": "up",
        "service": app.title,
        "description": "A (mostly) stateless REST API server for LEGO kit information and instructions.",
        "developer": "Bitboard",
        "system_version": app.version,
        "available_api_versions": [ "v1" ],
        "recommended_api_version": "v1",

        "source_code": "https://github.com/ModestBitboard/playwell-server",
        "container_registry": "ghcr.io/modestbitboard/playwell-server",

        "endpoints": {
            "openapi_spec": f"{base_url}{app.openapi_url}",
            "swagger_ui": f"{base_url}/docs",
            "redoc_ui": f"{base_url}/redoc"
        }
    }


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    # noinspection bad-argument-type
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url="/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_ui_html():
    # noinspection bad-argument-type
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_favicon_url="/favicon.ico"
    )

@app.get("/favicon.ico", include_in_schema=False)
def get_favicon():
    return FileResponse(path=LOGO_PATH, media_type="image/svg+xml")


# - -- --- ----- API versions ----- --- -- -
#  [!] set `deprecated=True` on old routers
# - -- --- ------------------------ --- -- -

from app.api.v1 import router as v1_router

app.include_router(v1_router, prefix="/v1")
