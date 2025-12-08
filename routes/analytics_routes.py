from fastapi import APIRouter
from services.analytics_service import (
    get_storage_stats,
    get_version_stats,
    get_daily_activity
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/storage")
def storage():
    return get_storage_stats()


@router.get("/versions")
def versions():
    return get_version_stats()


@router.get("/activity")
def activity():
    return get_daily_activity()
