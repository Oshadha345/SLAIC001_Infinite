from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def personalization_health():
    return {"status": "healthy", "service": "personalization-agent"}
