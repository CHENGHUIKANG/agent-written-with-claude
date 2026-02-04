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

            response = await self.client.chat.completions.create(**kwargs)

            tool_call_buffer = {}
            reasoning_buffer = ""
            in_reasoning = False
            
            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                
                if delta:
                    # 检查是否有 reasoning 字段
                    if hasattr(delta, 'reasoning') and delta.reasoning:
                        reasoning_buffer += delta.reasoning
                        if not in_reasoning:
                            in_reasoning = True
                            yield "[REASONING_START]"
                    
                    if hasattr(delta, 'content') and delta.content:
                        # 如果之前在 reasoning 中，现在结束了
                        if in_reasoning and reasoning_buffer:
                            yield f"[REASONING_END]{reasoning_buffer}[/REASONING_END]"
                            reasoning_buffer = ""
                            in_reasoning = False
                        yield delta.content
                    
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if hasattr(tool_call, 'function'):
                                func = tool_call.function
                                if hasattr(func, 'name'):
                                    tool_name = func.name
                                    
                                    if tool_name not in tool_call_buffer:
                                        tool_call_buffer[tool_name] = {
                                            "name": tool_name,
                                            "arguments": ""
                                        }
                                    
                                    if hasattr(func, 'arguments') and func.arguments:
                                        tool_call_buffer[tool_name]["arguments"] += func.arguments
                    
                    if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                        # 如果还有未输出的 reasoning
                        if in_reasoning and reasoning_buffer:
                            yield f"[REASONING_END]{reasoning_buffer}[/REASONING_END]"
                        
                        for tool_name, tool_data in tool_call_buffer.items():
                            arguments_str = tool_data["arguments"]
                            try:
                                import json
                                if arguments_str and arguments_str.strip():
                                    arguments = json.loads(arguments_str)
                                else:
                                    arguments = {}
                                yield f"[TOOL_CALL:{tool_name}:{arguments_str}]"
                            except json.JSONDecodeError:
                                yield f"[TOOL_CALL:{tool_name}:{arguments_str}]"
                        
                        yield "[DONE]"
                        
        except Exception as e:
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
