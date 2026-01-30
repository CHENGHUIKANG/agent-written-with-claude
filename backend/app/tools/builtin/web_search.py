from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP("web_search")


@mcp.tool()
async def web_search(
    query: str,
    max_results: Optional[int] = 10,
    region: Optional[str] = "wt-wt",
    time: Optional[str] = None
) -> dict:
    """
    网络搜索工具

    Args:
        query: 搜索查询词
        max_results: 最大返回结果数，默认为10
        region: 搜索区域，默认为"wt-wt"（全球）
        time: 时间范围（如 "d"=今天, "w"=本周, "m"=本月, "y"=今年）

    Returns:
        dict: 包含搜索结果的字典
            - success: 是否成功
            - message: 操作消息
            - query: 搜索查询
            - results: 搜索结果列表
                - title: 标题
                - url: 链接
                - snippet: 摘要
            - total_results: 总结果数
    """
    try:
        from duckduckgo_search import DDGS
        
        results = []
        total_results = 0
        
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                query,
                max_results=max_results,
                region=region,
                time=time
            ))
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
                total_results += 1
        
        return {
            "success": True,
            "message": f"搜索完成，找到 {total_results} 个结果",
            "query": query,
            "results": results,
            "total_results": total_results
        }
    except ImportError:
        return {
            "success": False,
            "message": "duckduckgo-search库未安装，请运行: pip install duckduckgo-search",
            "query": query,
            "results": [],
            "total_results": 0
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索失败: {str(e)}",
            "query": query,
            "results": [],
            "total_results": 0
        }


if __name__ == "__main__":
    mcp.run()
