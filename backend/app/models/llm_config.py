# ============================================================================
# LLM Config Model
# ============================================================================
from sqlalchemy import Column, BigInteger, String, Integer, Boolean, Numeric, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class Provider(str, enum.Enum):
    """LLM提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class LLMConfig(Base):
    """LLM配置模型"""
    __tablename__ = "llm_configs"

    id = Column(BigInteger, primary_key=True, index=True, comment="LLM配置ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属用户ID")
    provider = Column(String(50), nullable=False, comment="LLM提供商")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    api_key = Column(String(255), nullable=True, comment="API密钥 (加密存储)")
    base_url = Column(String(500), nullable=True, comment="自定义API端点 (本地部署或自定义)")
    max_tokens = Column(Integer, nullable=False, default=4096, comment="最大生成长度")
    temperature = Column(Numeric(3, 2), nullable=False, default=0.70, comment="温度参数 (0.00 - 2.00)")
    top_p = Column(Numeric(3, 2), nullable=True, default=1.00, comment="Top P 采样")
    is_default = Column(Boolean, nullable=False, default=False, comment="是否为默认配置")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系
    user = relationship("User", backref="llm_configs")

    def __repr__(self):
        return f"<LLMConfig(id={self.id}, provider='{self.provider}', model='{self.model_name}')>"
