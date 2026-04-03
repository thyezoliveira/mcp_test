import asyncio
from mcp.server import Server
import mcp.types as types
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount

# --- LÓGICA OO DO SERVIDOR ---
class ForjaTechMCPServer:
    def __init__(self):
        self.server = Server("ForjaTech-MCP")
        self._register_tools()

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                types.Tool(
                    name="status_servidor",
                    description="Verifica o status do servidor ForjaTech",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def call_tool(name, arguments):
            if name == "status_servidor":
                return [types.TextContent(
                    type="text", 
                    text="Ola, sou um servidor MCP funcionando. Fui configurado por forjatech."
                )]
            return []

# --- INFRAESTRUTURA WEB (ASGI) ---
mcp_logic = ForjaTechMCPServer()
sse_transport = SseServerTransport("/messages")

async def handle_sse(request):
    """Endpoint que o Claude/Cliente MCP chamará primeiro."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_logic.server.run(
            read_stream, 
            write_stream, 
            mcp_logic.server.create_initialization_options()
        )

# Aplicação Starlette (Compatível com Granian)
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", endpoint=sse_transport.handle_post_message),
    ]
)
