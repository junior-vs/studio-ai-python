"""API dependencies."""

from typing import Annotated

from fastapi import Header, HTTPException, status


async def verify_token(x_token: Annotated[str | None, Header()] = None) -> str:
    """Verify authentication token."""
    if x_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Token header missing",
        )
    if x_token != "secret-token":  # Replace with real auth logic
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    return x_token


async def get_current_user(token: Annotated[str, Header(alias="x-token")]) -> dict[str, str]:
    """Get current authenticated user."""
    # Replace with real user lookup logic
    return {"username": "testuser", "token": token}
