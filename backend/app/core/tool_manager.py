import importlib
import inspect
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from app.models.mcp_server import MCPServer, ServerType


class ToolManager:
    """工具管理器 - 管理内置工具和外部MCP工具"""

    def __init__(self):
        self.builtin_tools: Dict[str, Any] = {}
        self.external_tools: Dict[str, Any] = {}
        self._tool_definitions: Dict[str, Dict[str, Any]] = {}
        self._mcp_clients: Dict[int, Any] = {}

    async def load_builtin_tools(self):
        """加载所有内置工具"""
        try:
            from app.tools.builtin import file_save, file_read, file_search, web_search

            self.builtin_tools["file_save"] = file_save.mcp
            self.builtin_tools["file_read"] = file_read.mcp
            self.builtin_tools["file_search"] = file_search.mcp
            self.builtin_tools["web_search"] = web_search.mcp

            for tool_name, tool_mcp in self.builtin_tools.items():
                tools_list = await tool_mcp.list_tools()
                if tools_list:
                    for tool_def in tools_list:
                        self._tool_definitions[tool_name] = tool_def.model_dump()

            logger.info(f"已加载 {len(self.builtin_tools)} 个内置工具")
        except Exception as e:
            logger.error(f"加载内置工具失败: {str(e)}")

    async def load_external_mcp_tools(self, db: AsyncSession, user_id: int):
        """加载用户配置的外部MCP工具"""
        try:
            from sqlalchemy import select
            from app.models.mcp_server import MCPServer, ServerStatus

            result = await db.execute(
                select(MCPServer)
                .where((MCPServer.user_id == user_id) & (MCPServer.status == ServerStatus.ACTIVE))
            )
            mcp_servers = list(result.scalars().all())

            for mcp_server in mcp_servers:
                try:
                    await self._connect_mcp_server(mcp_server)
                except Exception as e:
                    logger.error(f"连接MCP服务器 {mcp_server.name} 失败: {str(e)}")

            logger.info(f"已加载 {len(self.external_tools)} 个外部MCP工具")
        except Exception as e:
            logger.error(f"加载外部MCP工具失败: {str(e)}")

    async def _connect_mcp_server(self, mcp_server: MCPServer):
        """连接到MCP服务器并加载工具"""
        try:
            from mcp import ClientSession
            
            if mcp_server.server_type == ServerType.STDIO:
                from mcp.client.stdio import stdio_client
                command = mcp_server.connection_params.get("command")
                args = mcp_server.connection_params.get("args", [])
                env = mcp_server.connection_params.get("env", {})
                
                read_stream, write_stream = await stdio_client(command, args, env).__aenter__()
                session = ClientSession(read_stream, write_stream)
                
                await session.initialize()
                
                self._mcp_clients[mcp_server.id] = {
                    "client": session,
                    "context": (read_stream, write_stream),
                    "server": mcp_server
                }
                
                tools = await session.list_tools()
                for tool in tools.tools:
                    tool_key = f"mcp_{mcp_server.id}_{tool.name}"
                    self.external_tools[tool_key] = {
                        "mcp_server_id": mcp_server.id,
                        "tool_name": tool.name,
                        "tool": tool
                    }
                    self._tool_definitions[tool_key] = tool.model_dump()
                
                logger.info(f"MCP服务器 {mcp_server.name} 连接成功，加载了 {len(tools.tools)} 个工具")
                
            elif mcp_server.server_type == ServerType.STREAMABLE_HTTP:
                from mcp.client.stdio import stdio_client
                url = mcp_server.connection_params.get("url")
                command = mcp_server.connection_params.get("command", "mcp-client")
                args = mcp_server.connection_params.get("args", [])
                env = mcp_server.connection_params.get("env", {})
                
                read_stream, write_stream = await stdio_client(command, args, env).__aenter__()
                session = ClientSession(read_stream, write_stream)
                
                await session.initialize()
                
                self._mcp_clients[mcp_server.id] = {
                    "client": session,
                    "context": (read_stream, write_stream),
                    "server": mcp_server
                }
                
                tools = await session.list_tools()
                for tool in tools.tools:
                    tool_key = f"mcp_{mcp_server.id}_{tool.name}"
                    self.external_tools[tool_key] = {
                        "mcp_server_id": mcp_server.id,
                        "tool_name": tool.name,
                        "tool": tool
                    }
                    self._tool_definitions[tool_key] = tool.model_dump()
                
                logger.info(f"MCP服务器 {mcp_server.name} 连接成功，加载了 {len(tools.tools)} 个工具")
                
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {str(e)}")
            raise

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具的OpenAI格式定义"""
        tools = []
        
        for tool_name, tool_def in self._tool_definitions.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_def.get("description", f"{tool_name}工具"),
                    "parameters": tool_def.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            })
        
        return tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        try:
            if tool_name in self.builtin_tools:
                return await self._execute_builtin_tool(tool_name, arguments)
            elif tool_name in self.external_tools:
                return await self._execute_external_tool(tool_name, arguments)
            else:
                return {
                    "success": False,
                    "error": f"工具 {tool_name} 不存在"
                }
        except Exception as e:
            logger.error(f"执行工具 {tool_name} 失败: {str(e)}")
            return {
                "success": False,
                "error": f"执行工具失败: {str(e)}"
            }

    async def _execute_builtin_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行内置工具"""
        try:
            tool_mcp = self.builtin_tools[tool_name]
            
            result = await tool_mcp.call_tool(tool_name, arguments)
            
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    content = content[0]
                    if isinstance(content, dict) and "text" in content:
                        return content["text"]
                    return content
                return content
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"执行内置工具 {tool_name} 失败: {str(e)}")
            raise

    async def _execute_external_tool(self, tool_key: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行外部MCP工具"""
        try:
            from mcp import ClientSession
            
            external_tool = self.external_tools[tool_key]
            mcp_server_id = external_tool["mcp_server_id"]
            tool_name = external_tool["tool_name"]
            
            if mcp_server_id not in self._mcp_clients:
                return {
                    "success": False,
                    "error": f"MCP服务器 {mcp_server_id} 未连接"
                }
            
            client_info = self._mcp_clients[mcp_server_id]
            session = client_info["client"]
            
            result = await session.call_tool(tool_name, arguments)
            
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    content = content[0]
                    if isinstance(content, dict) and "text" in content:
                        return content["text"]
                    return content
                return content
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"执行外部工具 {tool_key} 失败: {str(e)}")
            raise

    async def cleanup(self):
        """清理资源，断开所有MCP连接"""
        for mcp_server_id, client_info in self._mcp_clients.items():
            try:
                context = client_info.get("context")
                if context and hasattr(context, '__aexit__'):
                    await context.__aexit__(None, None, None)
                logger.info(f"已断开MCP服务器 {mcp_server_id} 的连接")
            except Exception as e:
                logger.error(f"断开MCP服务器 {mcp_server_id} 连接失败: {str(e)}")
        
        self._mcp_clients.clear()
        self.external_tools.clear()


tool_manager = ToolManager()
