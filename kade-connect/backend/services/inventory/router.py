from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def inventory_health():
    return {"status": "healthy", "service": "inventory"}
