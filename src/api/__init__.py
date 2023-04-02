"""Package for the FastAPI.

Contains the entry point for FastAPI.
"""

import fastapi
from fastapi.middleware.cors import CORSMiddleware

from . import main
from configs import settings
from .schemas import list_supported_assets

# Initialize FastAPI
app = fastapi.FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    debug=settings.DEBUG,
)

app.include_router(main.router)

"""
To fix errors like this in the console:
Origin null is not allowed by Access-Control-Allow-Origin. Status code: 200
Failed to load resource: Origin null is not allowed by Access-Control-Allow-Origin.
Status code: 200

CORS stands for Cross-Origin Resource Sharing. It is a security mechanism implemented
in web browsers to prevent web pages from making requests to a different domain than
the one that served the original
web page.

In simple terms, if a web page hosted on domain A wants to make a request to domain B,
the browser will prevent this request from being made by default,
as a security measure to protect users from malicious websites.
This is known as the Same-Origin Policy.

CORS is a way to relax the Same-Origin Policy, allowing web applications to make
cross-origin requests when necessary. It works by adding additional HTTP headers to
the response from the server that instruct the browser to allow the cross-origin request.

The CORS middleware used in the code above adds the necessary headers to the response
so that the client can make requests to the server from any origin.
By default, CORS middleware blocks all cross-origin requests, but
by specifying the allow_origins parameter as ["*"], it allows requests from any origin.

In addition, the allow_credentials, allow_methods, and allow_headers parameters
are also set to allow the client to send credentials, use any HTTP method,
and include any headers in the request respectively.
These parameters can be customized as needed to fit the specific requirements
of the web application.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", name="redirect", include_in_schema=False)
async def redirect_root() -> fastapi.responses.Response:
    """Redirect when the root path is contacted."""
    return fastapi.responses.Response("Hello, world!", media_type="text/plain")


@app.get("/healthz", name="healthz", include_in_schema=False)
async def healthz() -> fastapi.responses.Response:
    """Route for getting health of app used by Kubernetes monitoring API."""
    return fastapi.responses.Response("OK")


@app.get("/readyz", name="readyz", include_in_schema=False)
async def readyz() -> fastapi.responses.Response:
    """Route for getting health of app used by Kubernetes monitoring API."""
    return fastapi.responses.Response("OK")


@app.get("/livez", name="livez", include_in_schema=False)
async def livez() -> fastapi.responses.Response:
    """Route for getting health of app used by Kubernetes monitoring API."""
    return fastapi.responses.Response("OK")


@app.get("/keytest", name="test key", include_in_schema=False)
async def test_key() -> fastapi.responses.Response:
    """Route for checkin if API Key works."""
    return fastapi.responses.Response("Valid Key")


@app.get("/supported-assets", name="supported assets")
async def supported_assets() -> fastapi.responses.Response:
    """Route for checking supported assets."""
    return fastapi.responses.JSONResponse(
        content={"supported_assets": list_supported_assets()}
    )


@app.get("/two-numbers", name="two-numbers")
async def one_input() -> fastapi.responses.Response:
    """Response content is two numbers."""
    return fastapi.responses.JSONResponse(content={"x": 5.3, "y": 7.9})


@app.get("/identity", name="identity")
async def identity(value: float) -> fastapi.responses.Response:
    """Response content is one numer: same as the input."""
    return fastapi.responses.JSONResponse(content={"value": value})


@app.get("/multiply", name="multiply")
async def multiply(x: float, y: float, factor: float) -> fastapi.responses.Response:
    """Route to multiply two numbers by a factor."""
    return fastapi.responses.JSONResponse(
        content={"x_multiplied": x * factor, "y_multiplied": y * factor}
    )
