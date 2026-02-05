# ============================================================================
# LLM Client Module
# ============================================================================
from typing import Optional, List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
import json


class LLMClient:
    """LLM客户端类"""

    def __init__(
        self,
        provider: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0
    ):
        self.provider = provider
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

        # 初始化 OpenAI 兼容客户端
        self.client = AsyncOpenAI(
            api_key=api_key or "dummy",
            base_url=base_url,
            max_retries=3,
            timeout=60.0
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """发送聊天完成请求"""
        try:
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

            if stream:
                kwargs["stream"] = True
                response = await self.client.chat.completions.create(**kwargs)
                return {"stream": response}
            else:
                response = await self.client.chat.completions.create(**kwargs)
                return {
                    "id": response.id,
                    "choices": [
                        {
                            "index": choice.index,
                            "message": {
                                "role": choice.message.role,
                                "content": choice.message.content,
                                "reasoning": getattr(choice.message, "reasoning", None) or getattr(choice.message, "reasoning_content", None),
                                "tool_calls": [
                                    {
                                        "id": tc.id,
                                        "type": tc.type,
                                        "function": {
                                            "name": tc.function.name,
                                            "arguments": tc.function.arguments
                                        }
                                    }
                                    for tc in choice.message.tool_calls
                                ] if choice.message.tool_calls else None
                            },
                            "finish_reason": choice.finish_reason
                        }
                        for choice in response.choices
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
        except Exception as e:
            raise Exception(f"LLM API 调用失败: {str(e)}")

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成请求"""
        from loguru import logger
        
        logger.info("=" * 60)
        logger.info("[LLM] ========== 开始流式聊天完成 ==========")
        logger.info(f"[LLM] 模型: {self.model_name}")
        logger.info(f"[LLM] 消息数量: {len(messages)}")
        logger.info(f"[LLM] 工具数量: {len(tools) if tools else 0}")
        
        try:
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True
            }

            if tools:
                kwargs["tools"] = tools
                logger.info(f"[LLM] 可用工具: {[t.get('function', {}).get('name', 'unknown') for t in tools]}")

            logger.info("[LLM] 调用 LLM API...")
            response = await self.client.chat.completions.create(**kwargs)
            logger.info("[LLM] LLM API 连接成功, 开始接收流式数据...")

            # 使用 index 作为 key 来累积工具调用数据
            tool_call_buffer = {}
            reasoning_buffer = ""
            in_reasoning = False
            in_content = False
            
            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                
                if delta:
                    # 检查是否有 reasoning 字段
                    if hasattr(delta, 'reasoning') and delta.reasoning:
                        if not in_reasoning:
                            in_reasoning = True
                            yield "<think>"
                            in_content = False
                        reasoning_buffer += delta.reasoning
                    
                    if hasattr(delta, 'content') and delta.content:
                        # 如果之前在 reasoning 中，现在结束了
                        if in_reasoning:
                            yield f"{reasoning_buffer}"
                            yield "</think>"
                            reasoning_buffer = ""
                            in_reasoning = False
                        
                        if not in_content:
                            in_content = True
                        
                        yield delta.content
                    
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        from loguru import logger
                        logger.info(f"[LLM] 收到工具调用 delta: {delta.tool_calls}")
                        for tool_call in delta.tool_calls:
                            # 使用 index 作为 key
                            index = getattr(tool_call, 'index', 0)
                            
                            if index not in tool_call_buffer:
                                tool_call_buffer[index] = {
                                    "name": None,
                                    "arguments": ""
                                }
                            
                            if hasattr(tool_call, 'function'):
                                func = tool_call.function
                                
                                # 累积工具名
                                if hasattr(func, 'name') and func.name:
                                    tool_call_buffer[index]["name"] = func.name
                                    logger.info(f"[LLM] 工具名[{index}]: {func.name}")
                                
                                # 累积参数
                                if hasattr(func, 'arguments') and func.arguments:
                                    tool_call_buffer[index]["arguments"] += func.arguments
                                    logger.info(f"[LLM] 工具参数累积[{index}]: '{func.arguments}'")
                    
                    # 检查是否有 finish_reason
                    finish_reason = getattr(chunk.choices[0], 'finish_reason', None)
                    if finish_reason:
                        from loguru import logger
                        logger.info(f"[LLM] 流式响应结束，finish_reason: {finish_reason}")
                        logger.info(f"[LLM] 工具调用缓冲区: {tool_call_buffer}")
                        
                        # 如果还有未输出的 reasoning
                        if in_reasoning:
                            yield f"{reasoning_buffer}"
                            yield "</think>"
                        
                        # 输出工具调用
                        for index, tool_data in tool_call_buffer.items():
                            tool_name = tool_data["name"]
                            arguments_str = tool_data["arguments"]
                            
                            if not tool_name:
                                logger.warning(f"[LLM] 工具[{index}] 没有名称，跳过")
                                continue
                            
                            logger.info(f"[LLM] 准备输出工具调用[{index}]: {tool_name}, 参数: '{arguments_str}'")
                            try:
                                import json
                                if arguments_str and arguments_str.strip():
                                    # 验证 JSON 是否有效
                                    arguments = json.loads(arguments_str)
                                    tool_call_msg = f"[TOOL_CALL:{tool_name}:{arguments_str}]"
                                    logger.info(f"[LLM] 输出: {tool_call_msg}")
                                    yield tool_call_msg
                                else:
                                    # 如果参数为空，使用空对象
                                    tool_call_msg = f"[TOOL_CALL:{tool_name}:{{}}]"
                                    logger.info(f"[LLM] 输出(空参数): {tool_call_msg}")
                                    yield tool_call_msg
                            except json.JSONDecodeError as e:
                                logger.warning(f"[LLM] JSON 解析失败: {e}, 参数: '{arguments_str}'")
                                # JSON 解析失败，尝试修复或返回空对象
                                try:
                                    # 尝试添加缺失的闭合括号
                                    if arguments_str and not arguments_str.strip().endswith('}'):
                                        arguments_str = arguments_str + '}'
                                    arguments = json.loads(arguments_str)
                                    tool_call_msg = f"[TOOL_CALL:{tool_name}:{arguments_str}]"
                                    logger.info(f"[LLM] 输出(修复后): {tool_call_msg}")
                                    yield tool_call_msg
                                except Exception as e2:
                                    logger.error(f"[LLM] 修复失败: {e2}, 返回空对象")
                                    # 如果仍然失败，返回空对象
                                    tool_call_msg = f"[TOOL_CALL:{tool_name}:{{}}]"
                                    yield tool_call_msg
                        
                        logger.info("[LLM] 流式响应完成, 发送 [DONE]")
                        yield "[DONE]"
                        
        except Exception as e:
            logger.error(f"[LLM] 流式处理异常: {str(e)}")
            yield f"[ERROR:{str(e)}]"

    @staticmethod
    def create_llm_client(config) -> "LLMClient":
        """根据配置创建 LLM 客户端"""
        return LLMClient(
            provider=config.provider,
            model_name=config.model_name,
            api_key=config.api_key,
            base_url=config.base_url,
            max_tokens=config.max_tokens,
            temperature=float(config.temperature),
            top_p=float(config.top_p) if config.top_p else 1.0
        )
