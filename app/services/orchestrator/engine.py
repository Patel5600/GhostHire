from typing import Dict
from celery import chain
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.orchestrator.tasks import task_scrape_job, task_optimize_resume, task_apply_job
from app.models.workflow import WorkflowDefinition, WorkflowRun

class OrchestratorEngine:
    async def start_pipeline(self, db: AsyncSession, workflow_name: str, user_id: int, input_data: Dict) -> int:
        # 1. Fetch Definition
        res = await db.execute(select(WorkflowDefinition).where(WorkflowDefinition.name == workflow_name))
        definition = res.scalars().first()
        
        if not definition:
            # Create default if not exists for demo
            definition = WorkflowDefinition(
                name=workflow_name, 
                steps=["scrape", "optimize"]
            )
            db.add(definition)
            await db.commit()
            await db.refresh(definition)

        # 2. Create Run Record
        run = WorkflowRun(
            workflow_id=definition.id,
            user_id=user_id,
            status="running"
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # 3. Construct Celery Chain based on steps (Basic implementation)
        # Real implementation would parse a DAG from definition.steps
        
        # Example hardcoded chain for "standard_application"
        if workflow_name == "standard_pipeline":
             # Chain: Scrape -> Optimize (mocked chain)
             # task_scrape_job.s(input_data["url"]) | task_optimize_resume.s(...)
             
             # For simplicity, we just trigger first task and let it maybe trigger next, 
             # OR we use Celery chain primitive.
             c = chain(
                 task_scrape_job.s(input_data.get("url")),
                 # The output of scrape is passed to optimize? pipeline logic needs robust data passing.
                 # For MVP, we trigger independent tasks.
             )
             c.apply_async()

        return run.id

orchestrator = OrchestratorEngine()
