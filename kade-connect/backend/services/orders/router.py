from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def orders_health():
    return {"status": "healthy", "service": "orders"}
