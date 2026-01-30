import re
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

mcp = FastMCP("file_search")


@mcp.tool()
async def file_search(
    directory: str,
    pattern: str,
    file_pattern: Optional[str] = None,
    case_sensitive: Optional[bool] = False,
    max_results: Optional[int] = 100
) -> dict:
    """
    在目录中搜索文件内容

    Args:
        directory: 搜索目录（绝对路径或相对路径）
        pattern: 搜索模式（支持正则表达式）
        file_pattern: 文件名过滤模式（支持通配符，如 *.py, *.txt）
        case_sensitive: 是否区分大小写，默认为False
        max_results: 最大返回结果数，默认为100

    Returns:
        dict: 包含搜索结果的字典
            - success: 是否成功
            - message: 操作消息
            - directory: 搜索目录
            - pattern: 搜索模式
            - results: 匹配结果列表
                - file_path: 文件路径
                - line_number: 行号
                - line_content: 行内容
                - match: 匹配内容
            - total_matches: 总匹配数
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {
                "success": False,
                "message": f"目录不存在: {directory}",
                "directory": directory,
                "pattern": pattern,
                "results": [],
                "total_matches": 0
            }
        
        if not dir_path.is_dir():
            return {
                "success": False,
                "message": f"路径不是目录: {directory}",
                "directory": directory,
                "pattern": pattern,
                "results": [],
                "total_matches": 0
            }
        
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        
        results = []
        total_matches = 0
        
        files_to_search = []
        if file_pattern:
            files_to_search = list(dir_path.rglob(file_pattern))
        else:
            files_to_search = list(dir_path.rglob("*"))
        
        for file_path in files_to_search:
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")
                
                for line_number, line in enumerate(lines, 1):
                    matches = regex.findall(line)
                    if matches:
                        for match in matches:
                            if total_matches >= max_results:
                                break
                            
                            results.append({
                                "file_path": str(file_path.relative_to(dir_path)),
                                "absolute_path": str(file_path.absolute()),
                                "line_number": line_number,
                                "line_content": line.strip(),
                                "match": match
                            })
                            total_matches += 1
                
                if total_matches >= max_results:
                    break
            except Exception:
                continue
        
        return {
            "success": True,
            "message": f"搜索完成，找到 {total_matches} 个匹配",
            "directory": str(dir_path.absolute()),
            "pattern": pattern,
            "results": results,
            "total_matches": total_matches
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索失败: {str(e)}",
            "directory": directory,
            "pattern": pattern,
            "results": [],
            "total_matches": 0
        }


if __name__ == "__main__":
    mcp.run()
