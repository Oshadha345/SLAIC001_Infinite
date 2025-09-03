from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def execution_health():
    return {"status": "healthy", "service": "execution-agent"}
