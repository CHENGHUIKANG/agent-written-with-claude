# API v1 module
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, mcp, llm, agent

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(mcp.router)
api_router.include_router(llm.router)
api_router.include_router(agent.router)
