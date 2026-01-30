# ============================================================================
# MCP Service Module
# ============================================================================
import json
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.mcp_server import MCPServer, ServerType, ServerStatus
from loguru import logger


class MCPService:
    """MCP服务类"""

    @staticmethod
    async def create_mcp_server(
        db: AsyncSession,
        user_id: int,
        name: str,
        description: Optional[str],
        server_type: ServerType,
        connection_params: dict,
    ) -> MCPServer:
        """创建MCP服务器配置"""
        mcp_server = MCPServer(
            user_id=user_id,
            name=name,
            description=description,
            server_type=server_type,
            connection_params=connection_params,
            status=ServerStatus.ACTIVE,
        )
        db.add(mcp_server)
        await db.commit()
        await db.refresh(mcp_server)
        return mcp_server

    @staticmethod
    async def get_user_mcp_servers(db: AsyncSession, user_id: int) -> List[MCPServer]:
        """获取用户的所有MCP服务器配置"""
        result = await db.execute(
            select(MCPServer)
            .where(MCPServer.user_id == user_id)
            .order_by(MCPServer.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_mcp_server_by_id(
        db: AsyncSession, server_id: int, user_id: int
    ) -> Optional[MCPServer]:
        """根据ID获取MCP服务器配置"""
        result = await db.execute(
            select(MCPServer).where(
                (MCPServer.id == server_id) & (MCPServer.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_mcp_server(
        db: AsyncSession,
        server: MCPServer,
        name: Optional[str] = None,
        description: Optional[str] = None,
        connection_params: Optional[dict] = None,
        status: Optional[ServerStatus] = None,
    ) -> MCPServer:
        """更新MCP服务器配置"""
        if name is not None:
            server.name = name
        if description is not None:
            server.description = description
        if connection_params is not None:
            server.connection_params = connection_params
        if status is not None:
            server.status = status
        await db.commit()
        await db.refresh(server)
        return server

    @staticmethod
    async def delete_mcp_server(db: AsyncSession, server_id: int, user_id: int) -> bool:
        """删除MCP服务器配置"""
        result = await db.execute(
            delete(MCPServer).where(
                (MCPServer.id == server_id) & (MCPServer.user_id == user_id)
            )
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def test_mcp_connection(
        connection_params: dict, server_type: ServerType
    ) -> dict:
        """测试MCP服务器连接"""
        try:
            if server_type == ServerType.STDIO:
                return await MCPService._test_stdio_connection(connection_params)
            elif server_type == ServerType.STREAMABLE_HTTP:
                return await MCPService._test_streamable_http_connection(connection_params)
            else:
                return {
                    "success": False,
                    "message": f"不支持的MCP服务器类型: {server_type}",
                    "tools_found": 0,
                }
        except Exception as e:
            logger.error(f"MCP连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"MCP连接测试失败: {str(e)}",
                "tools_found": 0,
            }

    @staticmethod
    async def _test_stdio_connection(connection_params: dict) -> dict:
        """测试STDIO类型的MCP服务器连接"""
        try:
            from mcp import ClientSession
            from mcp.client.stdio import stdio_client

            command = connection_params.get("command")
            if not command:
                return {
                    "success": False,
                    "message": "缺少STDIO服务器命令",
                    "tools_found": 0,
                }

            args = connection_params.get("args", [])
            env = connection_params.get("env", {})

            async with stdio_client(command, args, env) as (read_stream, write_stream):
                session = ClientSession(read_stream, write_stream)

                await session.initialize()

                tools = await session.list_tools()

                result = {
                    "success": True,
                    "message": f"MCP STDIO服务器连接成功，找到 {len(tools.tools)} 个工具",
                    "tools_found": len(tools.tools),
                    "tools": [
                        {"name": tool.name, "description": tool.description}
                        for tool in tools.tools
                    ],
                }

                await session.close()

                return result
        except Exception as e:
            logger.error(f"STDIO连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"STDIO连接测试失败: {str(e)}",
                "tools_found": 0,
            }

    @staticmethod
    async def _test_streamable_http_connection(connection_params: dict) -> dict:
        """测试STREAMABLE_HTTP类型的MCP服务器连接"""
        try:
            import httpx
            
            url = connection_params.get("url")
            if not url:
                return {
                    "success": False,
                    "message": "缺少STREAMABLE_HTTP服务器URL",
                    "tools_found": 0,
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(url,headers={
                                                        "Accept": "application/json, text/event-stream"
                                                    }, json={
                                                        "jsonrpc": "2.0",
                                                        "method": "tools/list",
                                                        "id": "96d57e63-2"
                                                    })                                   
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "message": f"HTTP请求失败，状态码: {response.status_code}",
                        "tools_found": 0,
                    }
                
                try:
                    data = response.json()
                except Exception:
                    return {
                        "success": False,
                        "message": "响应不是有效的JSON格式",
                        "tools_found": 0,
                    }
                
                if "result" not in data or "tools" not in data.get("result", {}):
                    return {
                        "success": False,
                        "message": "响应中未找到tools字段",
                        "tools_found": 0,
                    }
                
                tools = data.get("result", {}).get("tools", [])

                return {
                    "success": True,
                    "message": f"MCP STREAMABLE_HTTP服务器连接成功，找到 {len(tools)} 个工具",
                    "tools_found": len(tools),
                    "tools": tools,
                }
        except Exception as e:
            logger.error(f"STREAMABLE_HTTP连接测试失败: {str(e)}")
            return {
                "success": False,
                "message": f"STREAMABLE_HTTP连接测试失败: {str(e)}",
                "tools_found": 0,
            }
