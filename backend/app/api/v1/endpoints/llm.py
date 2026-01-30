# ============================================================================
# LLM API Endpoints
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.llm_service import LLMService
from app.schemas.llm import (
    LLMConfigCreate,
    LLMConfigUpdate,
    LLMConfigResponse
)
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/configs", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_config(
    config_in: LLMConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """添加LLM配置"""
    llm_config = await LLMService.create_llm_config(
        db=db,
        user_id=current_user.id,
        provider=config_in.provider,
        model_name=config_in.model_name,
        api_key=config_in.api_key,
        base_url=config_in.base_url,
        max_tokens=config_in.max_tokens,
        temperature=config_in.temperature,
        top_p=config_in.top_p,
        is_default=config_in.is_default
    )
    return llm_config


@router.get("/configs", response_model=List[LLMConfigResponse])
async def get_llm_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的LLM配置列表"""
    configs = await LLMService.get_user_llm_configs(db, current_user.id)
    return configs


@router.get("/configs/default", response_model=LLMConfigResponse)
async def get_default_llm_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的默认LLM配置"""
    config = await LLMService.get_default_llm_config(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="默认LLM配置不存在"
        )
    return config


@router.get("/configs/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定LLM配置"""
    config = await LLMService.get_llm_config_by_id(db, config_id, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM配置不存在"
        )
    return config


@router.put("/configs/{config_id}", response_model=LLMConfigResponse)
async def update_llm_config(
    config_id: int,
    config_in: LLMConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新LLM配置"""
    config = await LLMService.get_llm_config_by_id(db, config_id, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM配置不存在"
        )

    updated_config = await LLMService.update_llm_config(
        db=db,
        config=config,
        provider=config_in.provider,
        model_name=config_in.model_name,
        api_key=config_in.api_key,
        base_url=config_in.base_url,
        max_tokens=config_in.max_tokens,
        temperature=config_in.temperature,
        top_p=config_in.top_p,
        is_default=config_in.is_default
    )
    return updated_config


@router.delete("/configs/{config_id}", response_model=MessageResponse)
async def delete_llm_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除LLM配置"""
    success = await LLMService.delete_llm_config(db, config_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM配置不存在"
        )
    return {"message": "LLM配置已删除", "success": True}
