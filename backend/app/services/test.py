

import asyncio
from app.services.mcp_service import MCPService



async def main():
    result = await MCPService._test_streamable_http_connection({"url": "https://mcp.amap.com/sse?key=8b76c70c33ddb1196a486b5919589c36"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())