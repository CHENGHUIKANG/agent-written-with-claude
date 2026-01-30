# ============================================================================
# LLM Schemas
# ============================================================================
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ============================================================================
# LLM Config Schemas
# ============================================================================
class LLMConfigBase(BaseModel):
    """LLM配置基础Schema"""
    provider: str = Field(..., pattern=r"^(openai|anthropic|custom)$", description="LLM提供商: openai, anthropic, custom")
    model_name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    api_key: Optional[str] = Field(None, max_length=255, description="API密钥")
    base_url: Optional[str] = Field(None, max_length=500, description="自定义API端点")
    max_tokens: int = Field(4096, ge=1, le=32768, description="最大生成长度")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数 (0.00 - 2.00)")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Top P 采样")
    is_default: bool = Field(False, description="是否为默认配置")


class LLMConfigCreate(LLMConfigBase):
    """创建LLM配置Schema"""
    pass


class LLMConfigUpdate(BaseModel):
    """更新LLM配置Schema"""
    provider: Optional[str] = Field(None, pattern=r"^(openai|anthropic|custom)$")
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, max_length=255)
    base_url: Optional[str] = Field(None, max_length=500)
    max_tokens: Optional[int] = Field(None, ge=1, le=32768)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_default: Optional[bool] = None


class LLMConfigResponse(LLMConfigBase):
    """LLM配置响应Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
