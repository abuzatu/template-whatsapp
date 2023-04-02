"""Contains the Schemas for various messages."""
from datetime import datetime
from pydantic import BaseModel, validator
from typing import List


def list_supported_assets() -> List[str]:
    """Check if the asset is supported."""
    supported_assets = ["OIL", "GOLD"]
    return supported_assets


class RequestData(BaseModel):
    """Request schema."""

    asset_name: str
    datetime: datetime
    price: float

    @validator("asset_name")
    def asset_supported(cls, asset_name: str) -> str:
        """Verify asset is supported."""
        supported_assets = ["OIL", "GOLD"]
        if asset_name not in supported_assets:
            raise ValueError(
                f"{asset_name} is not a supported asset, "
                f"but supported_assets={supported_assets}"
            )
        return asset_name

    @validator("price")
    def valid_price(cls, price: float) -> float:
        """Verify price is a positive float."""
        if price <= 0:
            raise ValueError("Price must be positve.")
        elif not isinstance(price, float):
            raise ValueError("Price must be a float.")
        return price


class ResponseData(BaseModel):
    """Response schema."""

    asset_name: str
    prices: List[float]

    class Config:
        """Response config."""

        schema_extra = {
            "example": {
                "asset_name": "OIL",
                "date": "2023-03-21",
                "price": [72.3, 74.5, 79.3],
            }
        }
