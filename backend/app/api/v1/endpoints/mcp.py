# ============================================================================
# MCP API Endpoints
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.mcp_server import MCPServer, ServerType, ServerStatus
from app.services.mcp_service import MCPService
from app.schemas.mcp import (
    MCPServerCreate,
    MCPServerUpdate,
    MCPServerResponse,
    MCPToolResponse
)
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.post("/servers", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server_in: MCPServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """添加MCP服务器"""
    mcp_server = await MCPService.create_mcp_server(
        db=db,
        user_id=current_user.id,
        name=server_in.name,
        description=server_in.description,
        server_type=server_in.server_type,
        connection_params=server_in.connection_params
    )
    return mcp_server


@router.get("/servers", response_model=List[MCPServerResponse])
async def get_mcp_servers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的MCP服务器列表"""
    servers = await MCPService.get_user_mcp_servers(db, current_user.id)
    return servers


@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定MCP服务器"""
    server = await MCPService.get_mcp_server_by_id(db, server_id, current_user.id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP服务器不存在"
        )
    return server


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: int,
    server_in: MCPServerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新MCP服务器配置"""
    server = await MCPService.get_mcp_server_by_id(db, server_id, current_user.id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP服务器不存在"
        )
    
    updated_server = await MCPService.update_mcp_server(
        db=db,
        server=server,
        name=server_in.name,
        description=server_in.description,
        connection_params=server_in.connection_params,
        status=server_in.status
    )
    return updated_server


@router.delete("/servers/{server_id}", response_model=MessageResponse)
async def delete_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除MCP服务器"""
    success = await MCPService.delete_mcp_server(db, server_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP服务器不存在"
        )
    return {"message": "MCP服务器已删除", "success": True}


@router.post("/servers/{server_id}/test", response_model=dict)
async def test_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """测试MCP服务器连接"""
    server = await MCPService.get_mcp_server_by_id(db, server_id, current_user.id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP服务器不存在"
        )

    test_result = await MCPService.test_mcp_connection(
        connection_params=server.connection_params,
        server_type=server.server_type
    )
    return test_result
