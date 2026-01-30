# ============================================================================
# MCP Server Model
# ============================================================================
from sqlalchemy import Column, BigInteger, String, Text, JSON, Enum as SQLEnum, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ServerType(str, enum.Enum):
    """MCP服务器连接类型"""
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable_http"


class ServerStatus(str, enum.Enum):
    """MCP服务器状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class MCPServer(Base):
    """MCP服务器配置模型"""
    __tablename__ = "mcp_servers"

    id = Column(BigInteger, primary_key=True, index=True, comment="MCP服务器ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属用户ID")
    name = Column(String(100), nullable=False, comment="MCP服务器名称")
    description = Column(Text, nullable=True, comment="MCP服务器描述")
    server_type = Column(String(20), nullable=False, comment="服务器连接类型")
    connection_params = Column(JSON, nullable=False, comment="连接参数(JSON格式)")
    status = Column(SQLEnum(ServerStatus, values_callable=lambda x: [e.value for e in x]), default=ServerStatus.ACTIVE, nullable=False, comment="状态")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系
    user = relationship("User", back_populates="mcp_servers")

    def __repr__(self):
        return f"<MCPServer(id={self.id}, name='{self.name}', type='{self.server_type}')>"
