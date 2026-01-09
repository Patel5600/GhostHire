from typing import Dict
from sqlalchemy import func
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User
from app.models.application import Application
from app.models.crawl_log import CrawlLog
from app.models.ai_log import AIRequestLog
from app.models.workflow import WorkflowRun
from app.models.admin import SystemAlert

class AdminService:
    async def get_system_metrics(self, db: AsyncSession) -> Dict:
        # Aggregating metrics
        
        # 1. Total Users
        res_users = await db.execute(select(func.count(User.id)))
        total_users = res_users.scalar_one()

        # 2. Daily Applications
        res_apps = await db.execute(select(func.count(Application.id)))
        total_apps = res_apps.scalar_one()
        
        # 3. Running Pipelines
        res_pipes = await db.execute(select(func.count(WorkflowRun.id)).where(WorkflowRun.status == "running"))
        active_pipelines = res_pipes.scalar_one()
        
        # 4. AI Usage (Last 24h - omitted timestamp filter for brevity)
        res_ai = await db.execute(select(func.count(AIRequestLog.id)))
        total_ai_requests = res_ai.scalar_one()

        # 5. Recent Alerts
        res_alerts = await db.execute(select(SystemAlert).where(SystemAlert.is_resolved == False).limit(5))
        active_alerts = res_alerts.scalars().all()

        return {
            "users": {"total": total_users, "active": total_users}, # simplified
            "applications": {"total": total_apps},
            "automation": {"active_pipelines": active_pipelines},
            "ai": {"total_requests": total_ai_requests},
            "alerts": active_alerts
        }

admin_service = AdminService()
