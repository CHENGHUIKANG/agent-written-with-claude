# ============================================================================
# Agent Schemas
# ============================================================================
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ToolDefinition(BaseModel):
    """工具定义"""
    type: str = Field(default="function", description="工具类型")
    function: Dict[str, Any] = Field(..., description="函数定义")


class FunctionDefinition(BaseModel):
    """函数定义"""
    name: str = Field(..., description="函数名称")
    description: str = Field(..., description="函数描述")
    parameters: Dict[str, Any] = Field(..., description="参数定义")


class ToolCall(BaseModel):
    """工具调用"""
    id: str = Field(..., description="工具调用ID")
    type: str = Field(default="function", description="类型")
    function: Dict[str, str] = Field(..., description="函数调用信息")


class Message(BaseModel):
    """消息"""
    role: str = Field(..., description="角色")
    content: Optional[str] = Field(None, description="内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    conversation_id: Optional[int] = Field(None, description="对话ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    content: Optional[str] = Field(None, description="响应内容")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="工具调用")
    finish_reason: Optional[str] = Field(None, description="完成原因")
    usage: Optional[Dict[str, int]] = Field(None, description="使用情况")


class ToolExecuteRequest(BaseModel):
    """工具执行请求"""
    tool_name: str = Field(..., description="工具名称")
    tool_params: Dict[str, Any] = Field(..., description="工具参数")
