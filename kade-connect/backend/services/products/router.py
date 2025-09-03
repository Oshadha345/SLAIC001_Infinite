from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def products_health():
    return {"status": "healthy", "service": "products"}
