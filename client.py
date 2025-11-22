import asyncio

from fastmcp import Client

# MCP server URL
SERVER_URL = "http://147.93.28.130/mcp"


async def test_connection():
    """Test basic connection to the server and show only totals"""
    print("🔌 Connecting to MCP server...")

    # Ignorar verificación SSL
    client = Client(SERVER_URL)

    async with client:
        # Ping the server
        try:
            await client.ping()
            print("✅ Server is responding correctly\n")
        except Exception as e:
            print(f"❌ Ping error: {e}")
            return

        # List tools and show only totals
        try:
            tools_response = await client.list_tools()
            tools = getattr(
                tools_response,
                "tools",
                tools_response if isinstance(tools_response, list) else [],
            )
            print(f"🔧 Total available tools: {len(tools)}")
            for t in tools:
                print(f" - {getattr(t, 'name', 'No name')}")
        except Exception as e:
            print(f"❌ Error listing tools: {e}")

        # List resources and show only totals
        try:
            resources_response = await client.list_resources()
            resources = getattr(
                resources_response,
                "resources",
                resources_response if isinstance(resources_response, list) else [],
            )
            print(f"📊 Total available resources: {len(resources)}")
            for r in resources:
                print(f" - {getattr(r, 'name', 'No name')}")
        except Exception as e:
            print(f"❌ Error listing resources: {e}")

        # List prompts and show only totals
        try:
            prompts_response = await client.list_prompts()
            prompts = getattr(
                prompts_response,
                "prompts",
                prompts_response if isinstance(prompts_response, list) else [],
            )
            print(f"💬 Total available prompts: {len(prompts)}")
            for p in prompts:
                print(f" - {getattr(p, 'name', 'No name')}")
        except Exception as e:
            print(f"❌ Error listing prompts: {e}")

        print("\n✅ Connection and totals ready")


async def test_tool_call(tool_name: str, arguments: dict):
    """Example of calling a tool and showing only totals"""
    client = Client(SERVER_URL, verify_ssl=False)

    async with client:
        try:
            result = await client.call_tool(tool_name, arguments=arguments)
            # If the result has many details, summarize only totals
            if isinstance(result, dict):
                total_keys = [
                    k for k in result.keys() if isinstance(result[k], (int, float))
                ]
                print(f"🧪 Summary result for {tool_name}:")
                for k in total_keys:
                    print(f" - {k}: {result[k]}")
            else:
                print(f"🧪 Result of {tool_name}: {result}")
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")


async def main():
    """Main function"""
    print("\n🔍 MCP CLIENT - ZOHO BOOKS (Totals Summary)\n")
    await test_connection()

    # Example of calling a tool with parameters (uncomment and adjust)
    # await test_tool_call("YourToolName", {"param1": "value1"})


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Client interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
