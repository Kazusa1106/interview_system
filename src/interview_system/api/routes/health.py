"""健康检查路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from interview_system.api.deps import get_database
from interview_system.infrastructure.database.connection import AsyncDatabase

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: AsyncDatabase = Depends(get_database)):
    await db.health_check()
    return {"status": "healthy", "database": "connected"}
