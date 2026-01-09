import pandas as pd
import numpy as np
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Dict

from app.models.analytics import ApplicationOutcome, DailyMetric, OptimizationSuggestion
from app.models.application import Application
from app.models.job import Job

class AnalyticsEngine:
    async def ingest_outcomes(self, db: AsyncSession, user_id: int):
        """
        Syncs application status to analytics outcomes tables.
        In a real system, this might be event-driven.
        """
        # Fetch applications with definitive status
        stmt = select(Application, Job).join(Job).where(Application.user_id == user_id)
        result = await db.execute(stmt)
        rows = result.all() # list of (Application, Job)
        
        for app, job in rows:
            # Check if outcome exists
            outcome_stmt = select(ApplicationOutcome).where(ApplicationOutcome.application_id == app.id)
            existing = (await db.execute(outcome_stmt)).scalars().first()
            
            if not existing:
                # Create default outcome record
                outcome = ApplicationOutcome(
                    application_id=app.id,
                    job_id=job.id,
                    user_id=user_id,
                    outcome_status=app.status
                )
                db.add(outcome)
            elif existing.outcome_status != app.status:
                # Update status
                existing.outcome_status = app.status
                db.add(existing)
        
        await db.commit()

    async def generate_insights(self, db: AsyncSession, user_id: int) -> Dict:
        """
        Generates user-facing insights using Pandas.
        """
        stmt = select(ApplicationOutcome, Job).join(Job).where(ApplicationOutcome.user_id == user_id)
        result = await db.execute(stmt)
        data = []
        for outcome, job in result.all():
            data.append({
                "status": outcome.outcome_status,
                "title": job.title,
                "company": job.company,
                "desc": job.description,
                "days": 0 # Placeholder for time diff
            })
            
        if not data:
            return {"message": "Not enough data"}

        df = pd.DataFrame(data)
        
        # 1. Success Rate
        total = len(df)
        interviews = len(df[df['status'] == 'interviewing'])
        success_rate = (interviews / total) * 100 if total > 0 else 0
        
        # 2. Keyword Correlation (very basic)
        # Identify words appearing more in 'interviewing' vs 'rejected'
        from collections import Counter
        def get_words(status):
            subset = df[df['status'] == status]
            text = " ".join(subset['title'].tolist()).lower()
            return Counter(text.split())
        
        interview_keywords = get_words('interviewing')
        
        # 3. Optimization Suggestion
        suggestion = "Keep applying!"
        if success_rate < 5:
            suggestion = "Consider simpler roles or optimizing resume keywords."
        elif success_rate > 20:
             suggestion = "You are doing great! Try aiming for higher seniority."

        return {
            "success_rate": round(success_rate, 2),
            "total_applications": total,
            "interview_count": interviews,
            "top_success_keywords": [k for k, v in interview_keywords.most_common(5)],
            "strategy": suggestion
        }

    async def predict_success(self, job_description: str, resume_text: str) -> float:
        """
        Mock prediction model. 
        In production, load a pickled sklearn model trained on 'ApplicationOutcome' history.
        """
        # Simple heuristic: Keyword overlap
        job_words = set(job_description.lower().split())
        resume_words = set(resume_text.lower().split())
        overlap = len(job_words.intersection(resume_words))
        
        # Normalize somewhat
        base_score = min(overlap / 20.0, 1.0) * 100
        return round(base_score, 1)

analytics_engine = AnalyticsEngine()
