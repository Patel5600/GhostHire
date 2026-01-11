from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional

from app.models.resume import Resume
from app.models.job import Job
from app.models.match import MatchResult
from .features import FeatureExtractor
from .vectorizer import SimpleVectorizer
from .ranker import WeightedRanker

class MatchingEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.extractor = FeatureExtractor()
        self.vectorizer = SimpleVectorizer()
        self.ranker = WeightedRanker()

    async def run_match(self, resume_id: int, job_id: int) -> MatchResult:
        """
        Orchestrates the matching process.
        """
        # 1. Fetch Data
        resume = await self.session.get(Resume, resume_id)
        job = await self.session.get(Job, job_id)
        
        if not resume or not job:
            raise ValueError("Resume or Job not found")
            
        resume_text = resume.extracted_text or ""
        job_text = (job.title or "") + " " + (job.description or "")
        
        # 2. Compute Features
        resume_skills = self.extractor.extract_skills(resume_text)
        job_skills = self.extractor.extract_skills(job_text)
        
        # 3. Compute Vector Similarity
        similarity = self.vectorizer.compute_cosine_similarity(resume_text, job_text)
        
        # 4. Rank/Score
        result_data = self.ranker.score(resume_skills, job_skills, similarity)
        
        # 5. Persist Result
        match_result = MatchResult(
            resume_id=resume.id,
            job_id=job.id,
            score=result_data["total_score"],
            details=result_data,
            model_version="v1.0.0"
        )
        self.session.add(match_result)
        await self.session.commit()
        await self.session.refresh(match_result)
        
        return match_result
