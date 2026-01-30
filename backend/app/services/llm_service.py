# ============================================================================
# LLM Service Module
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List, Optional
from app.models.llm_config import LLMConfig


class LLMService:
    """LLM服务类"""

    @staticmethod
    async def create_llm_config(
        db: AsyncSession,
        user_id: int,
        provider: str,
        model_name: str,
        api_key: Optional[str],
        base_url: Optional[str],
        max_tokens: int,
        temperature: float,
        top_p: Optional[float],
        is_default: bool
    ) -> LLMConfig:
        """创建LLM配置"""
        # 如果设置为默认配置，需要先将该用户的其他配置设为非默认
        if is_default:
            await db.execute(
                update(LLMConfig)
                .where(LLMConfig.user_id == user_id)
                .values(is_default=False)
            )
            await db.commit()

        llm_config = LLMConfig(
            user_id=user_id,
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            is_default=is_default
        )
        db.add(llm_config)
        await db.commit()
        await db.refresh(llm_config)
        return llm_config

    @staticmethod
    async def get_user_llm_configs(
        db: AsyncSession,
        user_id: int
    ) -> List[LLMConfig]:
        """获取用户的所有LLM配置"""
        result = await db.execute(
            select(LLMConfig)
            .where(LLMConfig.user_id == user_id)
            .order_by(LLMConfig.is_default.desc(), LLMConfig.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_default_llm_config(
        db: AsyncSession,
        user_id: int
    ) -> Optional[LLMConfig]:
        """获取用户的默认LLM配置"""
        result = await db.execute(
            select(LLMConfig)
            .where((LLMConfig.user_id == user_id) & (LLMConfig.is_default == True))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_llm_config_by_id(
        db: AsyncSession,
        config_id: int,
        user_id: int
    ) -> Optional[LLMConfig]:
        """根据ID获取LLM配置"""
        result = await db.execute(
            select(LLMConfig)
            .where((LLMConfig.id == config_id) & (LLMConfig.user_id == user_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_llm_config(
        db: AsyncSession,
        config: LLMConfig,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        is_default: Optional[bool] = None
    ) -> LLMConfig:
        """更新LLM配置"""
        # 如果设置为默认配置，需要先将该用户的其他配置设为非默认
        if is_default is True and not config.is_default:
            await db.execute(
                update(LLMConfig)
                .where((LLMConfig.user_id == config.user_id) & (LLMConfig.id != config.id))
                .values(is_default=False)
            )
            await db.commit()

        if provider is not None:
            config.provider = provider
        if model_name is not None:
            config.model_name = model_name
        if api_key is not None:
            config.api_key = api_key
        if base_url is not None:
            config.base_url = base_url
        if max_tokens is not None:
            config.max_tokens = max_tokens
        if temperature is not None:
            config.temperature = temperature
        if top_p is not None:
            config.top_p = top_p
        if is_default is not None:
            config.is_default = is_default

        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def delete_llm_config(
        db: AsyncSession,
        config_id: int,
        user_id: int
    ) -> bool:
        """删除LLM配置"""
        result = await db.execute(
            delete(LLMConfig)
            .where((LLMConfig.id == config_id) & (LLMConfig.user_id == user_id))
        )
        await db.commit()
        return result.rowcount > 0
