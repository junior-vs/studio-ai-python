"""API router configuration."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/items")
async def list_items() -> dict[str, list[str]]:
    """List all items."""
    return {"items": ["item1", "item2", "item3"]}


@router.get("/items/{item_id}")
async def get_item(item_id: int) -> dict[str, int]:
    """Get a specific item by ID."""
    return {"item_id": item_id}


@router.post("/items")
async def create_item(name: str) -> dict[str, str]:
    """Create a new item."""
    return {"name": name, "status": "created"}
