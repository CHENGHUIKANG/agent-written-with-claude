# ============================================================================
# MCP Schemas
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.mcp_server import ServerType, ServerStatus


# ============================================================================
# MCP Server Schemas
# ============================================================================
class MCPServerBase(BaseModel):
    """MCP服务器基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="MCP服务器名称")
    description: Optional[str] = Field(None, description="MCP服务器描述")
    server_type: ServerType = Field(..., description="服务器类型: stdio 或 streamable http")
    connection_params: Dict[str, Any] = Field(..., description="连接参数")


class MCPServerCreate(MCPServerBase):
    """创建MCP服务器Schema"""
    pass


class MCPServerUpdate(BaseModel):
    """更新MCP服务器Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    status: Optional[ServerStatus] = Field(None, description="状态: active 或 inactive")


class MCPServerResponse(MCPServerBase):
    """MCP服务器响应Schema"""
    id: int
    user_id: int
    status: ServerStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MCPToolResponse(BaseModel):
    """MCP工具响应Schema"""
    name: str
    description: str
    parameters: Dict[str, Any]
