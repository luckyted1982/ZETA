import httpx
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from config import get_settings


class DeepSeekClient:
    """DeepSeek API 客户端

    封装 DeepSeek 大模型 API 的调用，支持非流式和流式（SSE）两种对话模式。
    """

    def __init__(self):
        """初始化客户端，从配置中读取 API 密钥和基础地址。"""
        settings = get_settings()
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = "deepseek-chat"
        self.timeout = 120.0  # 默认超时 120 秒，适用于长文本生成

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """非流式对话

        Args:
            messages: OpenAI 格式的消息列表，如 [{"role": "user", "content": "..."}]
            temperature: 采样温度，控制输出随机性，范围 0~2
            max_tokens: 最大生成 token 数
            stream: 是否流式返回（此处固定为 False，如需流式请使用 chat_stream）

        Returns:
            API 返回的 JSON 字典，包含 choices、usage 等字段
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            )
            resp.raise_for_status()  # 自动抛出 4xx/5xx 异常
            return resp.json()

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐段返回 SSE 格式的文本片段

        Args:
            messages: 消息列表
            temperature: 采样温度
            max_tokens: 最大生成 token 数

        Yields:
            每个数据包中的增量文本内容
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as resp:
                resp.raise_for_status()
                # 逐行读取 SSE 流
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        if data == "[DONE]":
                            break  # 流结束标志
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            # 忽略格式错误的行，继续读取
                            continue

    def get_system_prompt(self, role: str) -> str:
        """获取系统角色 Prompt

        内置四种角色：researcher（研究分析师）、document_analyst（文档分析师）、
        knowledge_expert（知识库专家）、standard_explainer（标准解释专家）。

        Args:
            role: 角色标识字符串

        Returns:
            对应角色的系统提示词
        """
        prompts = {
            "researcher": (
                "你是一位资深的科创企业研究分析师，精通中国科技产业政策、企业创新能力评估和投资研究。"
                "你擅长通过多维度深度分析，为企业生成全面的调研报告。"
            ),
            "document_analyst": (
                "你是一位专业的文档分析专家，擅长从企业文档中提取关键信息，"
                "并按照8个维度进行分类整理。"
            ),
            "knowledge_expert": (
                "你是一位科技政策法规和行业研究专家，精通中国科技产业相关的法律法规、"
                "政策文件、行业研报等。你能够基于知识库内容，为用户提供精准、专业的解答。"
            ),
            "standard_explainer": (
                "你是一位企业评测标准专家，精通8维度55指标科创企业评测体系。"
                "你能够用通俗易懂的语言解释每个评测维度的含义、评分标准和改进建议。"
            ),
        }
        return prompts.get(role, prompts["researcher"])


# 全局单例，懒加载模式
_deepseek_client: Optional[DeepSeekClient] = None


def get_deepseek_client() -> DeepSeekClient:
    """获取 DeepSeek 客户端单例

    Returns:
        DeepSeekClient 实例（首次调用时初始化）
    """
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = DeepSeekClient()
    return _deepseek_client
