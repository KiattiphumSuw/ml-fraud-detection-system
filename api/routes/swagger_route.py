from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter(tags=["Documentation"])


@router.get(
    "/",
    include_in_schema=False,
    summary="Redirect root endpoint to Swagger UI",
    description=("Redirect users accessing “/” to the interactive Swagger UI page."),
)
@router.get(
    "/docs",
    include_in_schema=False,
    summary="Swagger UI",
    description="Serve the Swagger UI (HTML) for exploring the API.",
)
async def swagger_ui_html(request: Request) -> HTMLResponse:
    """
    Return the Swagger UI HTML page.

    This endpoint is mounted at both `/` and `/docs` to simplify
    initial access. It pulls your app’s OpenAPI spec from `/openapi.json`
    and sets the page title & favicon.

    Parameters:
    -----------
    request: Request
        The incoming HTTP request, used to build the correct URL to
        the `openapi.json` endpoint via `url_for`.
    """
    return get_swagger_ui_html(
        openapi_url=request.url_for("openapi_schema"),
        title=f"{request.app.title} – Swagger UI",
        swagger_favicon_url="/favicon.ico",
    )


@router.get(
    "/redoc",
    include_in_schema=False,
    summary="ReDoc UI",
    description="Serve the ReDoc HTML for an alternative OpenAPI viewer.",
)
async def redoc_ui_html(request: Request) -> HTMLResponse:
    """
    Return the ReDoc HTML page.

    Provides an alternative documentation UI at `/redoc` that some
    teams prefer for its layout and navigation style.

    Parameters:
    -----------
    request: Request
        Used to resolve the URL for the OpenAPI JSON schema.
    """
    return get_redoc_html(
        openapi_url=request.url_for("openapi_schema"),
        title=f"{request.app.title} – ReDoc",
    )


@router.get(
    "/openapi.json",
    include_in_schema=False,
    name="openapi_schema",
    summary="OpenAPI JSON schema",
    description="Dynamically generate and return the OpenAPI spec in JSON format.",
)
async def openapi_schema(request: Request) -> JSONResponse:
    """
    Build and return the application’s OpenAPI schema.

    Reads metadata directly from `app.title`, `app.version`,
    `app.description`, and the registered routes.

    Parameters:
    -----------
    request: Request
        The incoming request, whose `app` attribute holds metadata
        and routes to generate the schema.
    """
    spec = get_openapi(
        title=request.app.title,
        version=request.app.version,
        description=request.app.description,
        routes=request.app.routes,
    )
    return JSONResponse(content=spec)
