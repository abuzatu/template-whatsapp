"""Module for FastAPI."""

import fastapi
import numpy as np
from uuid import uuid4

from .schemas import RequestData, ResponseData
from utils.logger import request_logger  # noqa: F401

router = fastapi.APIRouter()


def initialize_logger(request_id: str, asset_name: str) -> None:
    """Initialize service-wide logger with shared request ID and asset name."""
    # create unique request ID to connect logs
    # add this to all logs in the services
    # and forward to prediction services too
    # to connect all logs at prediction time
    request_id = str(uuid4())

    global request_logger
    request_logger.set_kwargs(request_id=request_id, option_name=asset_name)
    request_logger.info(
        {
            "message": "Received a new request.",
        }
    )


@router.post("/recommendations/", status_code=200, response_model=ResponseData)
async def generate_recommendations(
    request_data: RequestData,
) -> fastapi.responses.Response:
    """Generate recommendations for an asset name, datetime and price.

    Here we will also later access a database and make some fancy calculations.
    """
    # attach request_id and asset_name to logger
    # to use in all modules for this request
    request_id = str(uuid4())
    initialize_logger(request_id=request_id, asset_name=request_data.asset_name)

    request_logger.info(
        {
            "process": "generate_recommendations",
            "message": "request_data",
            "request_id": request_id,
            "asset_name": request_data.asset_name,
            "datetime": request_data.datetime,
            "price": request_data.price,
        },
    )

    request_logger.info("TEST")
    response_asset_name = request_data.asset_name
    response_price = sorted(
        np.random.normal(loc=request_data.price, scale=request_data.price / 10.0, size=10)
    )
    response = {
        "asset_name": response_asset_name,
        "price": response_price,
    }
    request_logger.info(
        {
            "process": "generate_recommendations",
            "message": "response_data",
            "request_id": request_id,
            "asset_name": response_asset_name,
            "price": response_price,
        },
    )
    return fastapi.responses.JSONResponse(content=response, status_code=200)


@router.get("/multiply-router", name="multiply with router with get")
async def multiply_router(
    x: float, y: float, factor: float
) -> fastapi.responses.Response:
    """Route to multiply two numbers by a factor."""
    return fastapi.responses.JSONResponse(
        content={"x_double": x * factor, "y_double": y * factor}
    )


@router.post("/multiply-router-post", name="multiply with router with post")
async def multiply_router_post(
    x: float, y: float, factor: float
) -> fastapi.responses.Response:
    """Route to multiply two numbers by a factor."""
    return fastapi.responses.JSONResponse(
        content={"x_double": x * factor, "y_double": y * factor}
    )


@router.post(
    "/identity-router-post",
    name="identity with router and post",
    status_code=200,
    response_model=ResponseData,
)
async def generate_identity_router_post(
    request_data: RequestData,
) -> fastapi.responses.Response:
    """Generate recommendations for an asset name, datetime and price.

    Here we will also later access a database and make some fancy calculations.
    async def identity(value: float) -> fastapi.responses.Response:
    """
    value = request_data.price
    return fastapi.responses.JSONResponse(content={"value": value}, status_code=200)
