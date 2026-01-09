from fastapi import APIRouter
from app.api.v1.endpoints import auth, resumes, jobs, applications, ai, ingest, automation, analytics, orchestrator, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
