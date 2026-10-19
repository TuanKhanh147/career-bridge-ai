from fastapi import APIRouter, Depends
from ..services.analytics_service import get_market_intelligence
from ..auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Market Intelligence & Analytics"])

@router.get("/market-trends")
def get_trends(current_user: dict = Depends(get_current_user)):
    return get_market_intelligence()
