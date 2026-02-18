"""
Main API v1 router.

This router aggregates all v1 endpoints. As the application grows,
sub-routers from different domains can be included here.

Example future structure:
    v1_router.include_router(users.router, prefix="/users", tags=["users"])
    v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_single_process.db.models import HealthCheck
from fastapi_single_process.db.session import get_db_session

v1_router = APIRouter()


@v1_router.get("/health")
async def health_check(session: Annotated[AsyncSession, Depends(get_db_session)]) -> dict[str, str]:
    """
    Health check endpoint.

    Verifies:
    - API is running
    - Database is reachable
    - Database can write and read data

    Used by load balancers and monitoring systems.
    """
    # Test the database write
    check = HealthCheck()
    session.add(check)
    await session.commit()

    # Test the database read
    result = await session.execute(select(HealthCheck).order_by(HealthCheck.id.desc()).limit(1))
    latest = result.scalar_one()

    return {
        "status": "healthy",
        "database": "connected",
        "last_check": latest.checked_at.isoformat(),
    }
