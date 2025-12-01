"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base item model."""

    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: str | None = Field(None, max_length=500, description="Item description")


class ItemCreate(ItemBase):
    """Model for creating items."""

    pass


class ItemResponse(ItemBase):
    """Model for item responses."""

    id: int = Field(..., description="Item ID")

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
