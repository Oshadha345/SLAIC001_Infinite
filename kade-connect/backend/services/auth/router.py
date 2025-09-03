"""
Authentication Service Router
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def auth_health():
    return {"status": "healthy", "service": "auth"}
