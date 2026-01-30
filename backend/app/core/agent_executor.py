# ============================================================================
# Agent Executor Module
# ============================================================================
from typing import List, Dict, Any, Optional
from app.core.llm_client import LLMClient
from app.core.tool_manager import tool_manager
from loguru import logger


class AgentExecutor:
    """Agent执行器 - 编排层"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def execute(
        self,
        user_message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        执行 Agent 任务
        
        Args:
            user_message: 用户输入的消息
            tools: 可用的工具列表
            conversation_history: 对话历史记录
            
        Returns:
            包含响应内容和工具调用的字典
        """
        messages = []
        
        system_prompt = self._build_system_prompt(tools)
        messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                response = await self.llm_client.chat_completion(
                    messages=messages,
                    tools=tools
                )
                
                choice = response["choices"][0]
                message = choice["message"]
                
                tool_calls = message.get("tool_calls")
                
                if not tool_calls:
                    return {
                        "content": message.get("content"),
                        "tool_calls": None,
                        "finish_reason": choice["finish_reason"],
                        "usage": response["usage"],
                        "iterations": iteration
                    }
                
                assistant_message = {
                    "role": "assistant",
                    "content": message.get("content"),
                    "tool_calls": tool_calls
                }
                messages.append(assistant_message)
                
                for tool_call in tool_calls:
                    tool_name = tool_call.get("function", {}).get("name")
                    tool_arguments = tool_call.get("function", {}).get("arguments", "{}")
                    
                    try:
                        import json
                        arguments = json.loads(tool_arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
                    
                    tool_result = await tool_manager.execute_tool(tool_name, arguments)
                    
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "name": tool_name,
                        "content": str(tool_result)
                    }
                    messages.append(tool_message)
                
            except Exception as e:
                logger.error(f"Agent 执行失败: {str(e)}")
                raise Exception(f"Agent 执行失败: {str(e)}")
        
        return {
            "content": "达到最大迭代次数，任务未完成",
            "tool_calls": None,
            "finish_reason": "max_iterations",
            "usage": {},
            "iterations": max_iterations
        }

    async def execute_stream(
        self,
        user_message: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """
        流式执行 Agent 任务
        
        Args:
            user_message: 用户输入的消息
            tools: 可用的工具列表
            conversation_history: 对话历史记录
            
        Yields:
            流式响应内容
        """
        messages = []
        
        system_prompt = self._build_system_prompt(tools)
        messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            try:
                tool_calls_buffer = []
                current_content = ""
                
                async for chunk in self.llm_client.stream_chat_completion(
                    messages=messages,
                    tools=tools
                ):
                    if chunk.startswith("[TOOL_CALL:"):
                        tool_calls_buffer.append(chunk)
                    elif chunk == "[DONE]":
                        if tool_calls_buffer:
                            for tool_call_str in tool_calls_buffer:
                                yield tool_call_str
                            
                            for tool_call_str in tool_calls_buffer:
                                try:
                                    import json
                                    match = tool_call_str.replace("[TOOL_CALL:", "").replace("]", "")
                                    if ":" in match:
                                        parts = match.split(":", 1)
                                        tool_name = parts[0]
                                        tool_arguments = parts[1] if len(parts) > 1 else "{}"
                                        
                                        arguments = json.loads(tool_arguments)
                                        
                                        logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
                                        
                                        tool_result = await tool_manager.execute_tool(tool_name, arguments)
                                        
                                        yield f"[TOOL_RESULT:{tool_name}:{json.dumps(tool_result)}]"
                                        
                                        messages.append({
                                            "role": "assistant",
                                            "content": current_content,
                                            "tool_calls": [{
                                                "id": f"call_{iteration}_{len(tool_calls_buffer)}",
                                                "type": "function",
                                                "function": {
                                                    "name": tool_name,
                                                    "arguments": tool_arguments
                                                }
                                            }]
                                        })
                                        
                                        messages.append({
                                            "role": "tool",
                                            "tool_call_id": f"call_{iteration}_{len(tool_calls_buffer)}",
                                            "name": tool_name,
                                            "content": str(tool_result)
                                        })
                                except Exception as e:
                                    logger.error(f"处理工具调用失败: {str(e)}")
                                    yield f"[ERROR:工具调用失败: {str(e)}]"
                            
                            tool_calls_buffer = []
                            current_content = ""
                        else:
                            yield chunk
                            return
                    elif chunk.startswith("[ERROR:"):
                        yield chunk
                        return
                    else:
                        current_content += chunk
                        yield chunk
                
                if not tool_calls_buffer:
                    return
                    
            except Exception as e:
                logger.error(f"Agent 流式执行失败: {str(e)}")
                yield f"[ERROR:Agent 流式执行失败: {str(e)}]"
                return
        
        yield "[ERROR:达到最大迭代次数，任务未完成]"

    def _build_system_prompt(self, tools: Optional[List[Dict[str, Any]]]) -> str:
        """
        构建系统提示
        
        Args:
            tools: 可用的工具列表
            
        Returns:
            系统提示字符串
        """
        base_prompt = """你是一个智能助手，可以帮助用户完成各种任务。

你可以使用提供的工具来帮助用户。当用户需要使用工具时，请调用相应的工具。

工具使用规则：
1. 仔细分析用户的需求
2. 确定是否需要使用工具
3. 如果需要，选择合适的工具并提供正确的参数
4. 如果不需要工具，直接回答用户的问题
"""

        if tools:
            tools_description = "\n\n可用的工具：\n"
            for tool in tools:
                tool_name = tool.get("function", {}).get("name", "unknown")
                tool_desc = tool.get("function", {}).get("description", "无描述")
                tools_description += f"- {tool_name}: {tool_desc}\n"
            
            return base_prompt + tools_description
        
        return base_prompt

    @staticmethod
    def create_agent_executor(llm_config) -> "AgentExecutor":
        """根据 LLM 配置创建 Agent 执行器"""
        llm_client = LLMClient.create_llm_client(llm_config)
        return AgentExecutor(llm_client)
