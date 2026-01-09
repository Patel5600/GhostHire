import os
from typing import Dict, Any, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

from app.models.ai_log import AIRequestLog, AIResult
from app.services.ai.providers import LLMProvider, MockProvider, OpenAILikeProvider
from app.services.ai import prompts
from app.core.config import settings

class AIServiceManager:
    def __init__(self):
        # Determine provider based on env
        # In a real app, this might be dynamic per user tier or toggle
        api_key = settings.AI_API_KEY
        
        if api_key and api_key.startswith("gsk_"): # Example: Groq keys often start with gsk_
            self.provider = OpenAILikeProvider(api_key, "https://api.groq.com/openai/v1", "llama3-70b-8192")
        elif api_key: 
            # Default to some other if key present (e.g. together)
            self.provider = OpenAILikeProvider(api_key, "https://api.together.xyz/v1", "meta-llama/Llama-3-70b-chat-hf")
        else:
            self.provider = MockProvider()

    async def _log_request(self, db: AsyncSession, user_id: int, r_type: str, prompt: str) -> int:
        log = AIRequestLog(
            user_id=user_id,
            request_type=r_type,
            provider=self.provider.__class__.__name__,
            model=getattr(self.provider, "model", "mock"),
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log.id

    async def _log_result(self, db: AsyncSession, request_id: int, content: Any):
        # If content is str, wrap it
        c_dict = content if isinstance(content, dict) else {"text": content}
        res = AIResult(request_id=request_id, content=c_dict)
        db.add(res)
        await db.commit()

    async def optimize_resume(self, db: AsyncSession, user_id: int, resume_text: str, job_text: str) -> Dict:
        user_prompt = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_text}"
        req_id = await self._log_request(db, user_id, "optimization", user_prompt)
        
        try:
            result = await self.provider.generate_json(prompts.RESUME_OPTIMIZE_SYSTEM, user_prompt)
            await self._log_result(db, req_id, result)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def match_job(self, db: AsyncSession, user_id: int, profile_json: Dict, job_text: str) -> Dict:
        import json
        user_prompt = f"CANDIDATE PROFILE:\n{json.dumps(profile_json)}\n\nJOB:\n{job_text}"
        req_id = await self._log_request(db, user_id, "matching", user_prompt)
        
        try:
            result = await self.provider.generate_json(prompts.JOB_MATCH_SYSTEM, user_prompt)
            await self._log_result(db, req_id, result)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def generate_cover_letter(self, db: AsyncSession, user_id: int, profile_json: Dict, job_text: str) -> str:
        import json
        user_prompt = f"CANDIDATE:\n{json.dumps(profile_json)}\n\nJOB:\n{job_text}"
        req_id = await self._log_request(db, user_id, "cover_letter", user_prompt)
        
        try:
            result = await self.provider.generate_text(prompts.COVER_LETTER_SYSTEM, user_prompt)
            await self._log_result(db, req_id, {"text": result})
            return result
        except Exception as e:
            return f"Error: {str(e)}"

ai_manager = AIServiceManager()
