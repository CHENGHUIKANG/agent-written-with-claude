# ============================================================================
# Agent API Endpoints
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.agent_executor import AgentExecutor
from app.core.tool_manager import tool_manager
from app.models.user import User
from app.services.llm_service import LLMService
from app.schemas.agent import ChatRequest, ChatResponse
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Agent 聊天接口
    
    接收用户消息，通过 Agent 执行器调用 LLM，返回响应
    """
    llm_config = await LLMService.get_default_llm_config(db, current_user.id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请先配置默认 LLM"
        )
    
    await tool_manager.load_external_mcp_tools(db, current_user.id)
    
    agent = AgentExecutor.create_agent_executor(llm_config)
    
    tools = tool_manager.get_all_tools()
    
    try:
        result = await agent.execute(
            user_message=request.message,
            tools=tools,
            conversation_history=None
        )
        # 确保 reasoning 字段存在
        if 'reasoning' not in result or result['reasoning'] is None:
            result['reasoning'] = None
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 执行失败: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Agent 流式聊天接口
    
    接收用户消息，通过 Agent 执行器调用 LLM，流式返回响应
    """
    llm_config = await LLMService.get_default_llm_config(db, current_user.id)
    if not llm_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请先配置默认 LLM"
        )
    
    await tool_manager.load_external_mcp_tools(db, current_user.id)
    
    agent = AgentExecutor.create_agent_executor(llm_config)
    
    tools = tool_manager.get_all_tools()
    
    async def generate():
        try:
            async for chunk in agent.execute_stream(
                user_message=request.message,
                tools=tools,
                conversation_history=None
            ):
                if chunk:
                    yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status", response_model=MessageResponse)
async def get_agent_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取 Agent 状态
    
    检查用户是否配置了默认 LLM
    """
    llm_config = await LLMService.get_default_llm_config(db, current_user.id)
    if llm_config:
        return {
            "message": f"Agent 就绪，使用模型: {llm_config.model_name}",
            "success": True
        }
    else:
        return {
            "message": "Agent 未就绪，请先配置默认 LLM",
            "success": False
        }
