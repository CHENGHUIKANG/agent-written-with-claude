from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP("file_read")


@mcp.tool()
async def file_read(file_path: str, encoding: Optional[str] = "utf-8") -> dict:
    """
    读取文件内容

    Args:
        file_path: 文件路径（绝对路径或相对路径）
        encoding: 文件编码，默认为utf-8

    Returns:
        dict: 包含操作结果的字典
            - success: 是否成功
            - message: 操作消息
            - file_path: 文件路径
            - content: 文件内容
            - size: 文件大小（字节）
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "message": f"文件不存在: {file_path}",
                "file_path": file_path,
                "content": "",
                "size": 0
            }
        
        if not path.is_file():
            return {
                "success": False,
                "message": f"路径不是文件: {file_path}",
                "file_path": file_path,
                "content": "",
                "size": 0
            }
        
        content = path.read_text(encoding=encoding)
        size = path.stat().st_size
        
        return {
            "success": True,
            "message": f"文件已成功读取: {file_path}",
            "file_path": str(path.absolute()),
            "content": content,
            "size": size
        }
    except PermissionError:
        return {
            "success": False,
            "message": f"权限不足，无法读取文件: {file_path}",
            "file_path": file_path,
            "content": "",
            "size": 0
        }
    except UnicodeDecodeError:
        return {
            "success": False,
            "message": f"文件编码错误，无法解码: {file_path}",
            "file_path": file_path,
            "content": "",
            "size": 0
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"读取文件失败: {str(e)}",
            "file_path": file_path,
            "content": "",
            "size": 0
        }


if __name__ == "__main__":
    mcp.run()
