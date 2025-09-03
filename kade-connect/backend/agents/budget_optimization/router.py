from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def budget_optimization_health():
    return {"status": "healthy", "service": "budget-optimization-agent"}
