import os
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP("file_save")


@mcp.tool()
async def file_save(filepath: str, text: str, file_encoding: Optional[str] = "utf-8") -> dict:
    """
    保存内容到文件

    Args:
        filepath: 文件路径（绝对路径或相对路径）
        text: 要保存的文本内容
        file_encoding: 文件编码，默认为utf-8

    Returns:
        dict: 包含操作结果的字典
            - success: 是否成功
            - message: 操作消息
            - file_path: 文件路径
            - size: 文件大小（字节）
    """
    try:
        path = Path(filepath)
        
        parent_dir = path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
        
        path.write_text(text, encoding=file_encoding)
        
        size = path.stat().st_size
        
        return {
            "success": True,
            "message": f"文件已成功保存到 {filepath}",
            "file_path": str(path.absolute()),
            "size": size
        }
    except PermissionError:
        return {
            "success": False,
            "message": f"权限不足，无法写入文件: {filepath}",
            "file_path": filepath,
            "size": 0
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存文件失败: {str(e)}",
            "file_path": filepath,
            "size": 0
        }


if __name__ == "__main__":
    mcp.run()
