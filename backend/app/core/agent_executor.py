# ============================================================================
# Agent Executor Module
# ============================================================================
from typing import List, Dict, Any, Optional, Tuple
import re
from app.core.llm_client import LLMClient
from app.core.tool_manager import tool_manager
from loguru import logger


class AgentExecutor:
    """Agent执行器 - 编排层"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def _extract_reasoning(self, content: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        从内容中提取思考内容

        Args:
            content: 原始内容

        Returns:
            (思考内容, 去除思考后的内容)
        """
        if not content:
            return None, None

        # 尝试多种格式的思考内容标签
        patterns = [
            (r'<thought>(.*?)</thought>', 'xml'),
            (r'<think>(.*?)</think>', 'xml'),
            (r'<reasoning>(.*?)</reasoning>', 'xml'),
            (r'思考：(.*?)(?=\n\n|\Z)', 'text'),
            (r'Reasoning:(.*?)(?=\n\n|\Z)', 'text'),
            (r'Thought:(.*?)(?=\n\n|\Z)', 'text'),
        ]

        for pattern, ptype in patterns:
            if ptype == 'xml':
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                if matches:
                    reasoning = '\n\n'.join(match.strip() for match in matches if match.strip())
                    # 从内容中移除思考标签
                    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
                    cleaned_content = cleaned_content.strip()
                    return reasoning, cleaned_content if cleaned_content else None
            else:
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    reasoning = match.group(1).strip()
                    cleaned_content = content[:match.start()].strip()
                    if not cleaned_content:
                        cleaned_content = content[match.end():].strip()
                    return reasoning, cleaned_content if cleaned_content else None

        return None, content

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
                reasoning = message.get("reasoning")
                content = message.get("content")
                
                # 如果 LLM 没有返回 reasoning 字段，尝试从 content 中提取
                if not reasoning and content:
                    extracted_reasoning, cleaned_content = self._extract_reasoning(content)
                    if extracted_reasoning:
                        reasoning = extracted_reasoning
                        content = cleaned_content
                
                if not tool_calls:
                    return {
                        "content": content,
                        "reasoning": reasoning,
                        "tool_calls": None,
                        "finish_reason": choice["finish_reason"],
                        "usage": response["usage"],
                        "iterations": iteration
                    }
                
                assistant_message = {
                    "role": "assistant",
                    "content": content,
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
                tool_arguments_buffer = {}
                
                async for chunk in self.llm_client.stream_chat_completion(
                    messages=messages,
                    tools=tools
                ):
                    logger.info(f"[Agent] 收到 chunk: '{chunk[:100]}...' " if len(chunk) > 100 else f"[Agent] 收到 chunk: '{chunk}'")
                    
                    if chunk.startswith("[TOOL_CALL:"):
                        logger.info(f"[Agent] 检测到工具调用: {chunk}")
                        tool_calls_buffer.append(chunk)
                    elif chunk == "[DONE]":
                        logger.info(f"[Agent] 收到 [DONE], 工具调用缓冲区: {tool_calls_buffer}")
                        if tool_calls_buffer:
                            for tool_call_str in tool_calls_buffer:
                                try:
                                    import json
                                    import re
                                    
                                    logger.info(f"[Agent] 解析工具调用: {tool_call_str}")
                                    
                                    # 使用正则表达式解析 [TOOL_CALL:tool_name:{...}]
                                    # 工具名是字母数字下划线，参数是 JSON 对象
                                    match = re.match(r'\[TOOL_CALL:([a-zA-Z_][a-zA-Z0-9_]*):(.*)\]', tool_call_str)
                                    if match:
                                        tool_name = match.group(1)
                                        tool_arguments_str = match.group(2)
                                        logger.info(f"[Agent] 正则匹配成功: 工具名={tool_name}, 参数={tool_arguments_str}")
                                    else:
                                        logger.warning(f"[Agent] 正则匹配失败，回退到简单解析: {tool_call_str}")
                                        # 回退到简单解析
                                        content = tool_call_str[12:]  # len("[TOOL_CALL:") = 12
                                        if content.endswith(']'):
                                            content = content[:-1]
                                        
                                        if ":" in content:
                                            colon_idx = content.find(':')
                                            tool_name = content[:colon_idx]
                                            tool_arguments_str = content[colon_idx + 1:]
                                        else:
                                            tool_name = content
                                            tool_arguments_str = "{}"
                                        logger.info(f"[Agent] 简单解析结果: 工具名={tool_name}, 参数={tool_arguments_str}")
                                    
                                    try:
                                        arguments = json.loads(tool_arguments_str)
                                        logger.info(f"[Agent] JSON 解析成功: {arguments}")
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"[Agent] JSON 解析失败: {e}, 尝试修复")
                                        # 尝试修复 JSON
                                        try:
                                            # 可能是缺少闭合括号
                                            if not tool_arguments_str.strip().endswith('}'):
                                                tool_arguments_str = tool_arguments_str + '}'
                                            arguments = json.loads(tool_arguments_str)
                                            logger.info(f"[Agent] JSON 修复成功: {arguments}")
                                        except Exception as e2:
                                            logger.error(f"[Agent] JSON 修复失败: {e2}, 使用空对象")
                                            # 如果仍然失败，使用空对象
                                            arguments = {}
                                    
                                    logger.info(f"[Agent] 执行工具: {tool_name}, 参数: {arguments}")
                                    
                                    tool_result = await tool_manager.execute_tool(tool_name, arguments)
                                    logger.info(f"[Agent] 工具执行结果: {tool_result}")
                                    
                                    # 确保工具结果可以被 JSON 序列化
                                    try:
                                        tool_result_json = json.dumps(tool_result)
                                    except (TypeError, ValueError) as e:
                                        logger.warning(f"[Agent] 工具结果 JSON 序列化失败: {e}, 转换为字符串")
                                        tool_result_json = json.dumps({"success": True, "result": str(tool_result)})
                                    
                                    yield f"[TOOL_RESULT:{tool_name}:{tool_result_json}]"
                                    
                                    messages.append({
                                        "role": "assistant",
                                        "content": current_content,
                                        "tool_calls": [{
                                            "id": f"call_{iteration}_{len(tool_calls_buffer)}",
                                            "type": "function",
                                            "function": {
                                                "name": tool_name,
                                                "arguments": tool_arguments_str
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
                                    logger.error(f"[Agent] 处理工具调用失败: {str(e)}")
                                    yield f"[ERROR:工具调用失败: {str(e)}]"
                            
                            tool_calls_buffer = []
                            current_content = ""
                            tool_arguments_buffer = {}
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
