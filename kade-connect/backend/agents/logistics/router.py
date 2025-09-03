from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def logistics_health():
    return {"status": "healthy", "service": "logistics-agent"}
