import asyncio

from backend.mcp_client.instance import initialize, manager


async def main():
    print("Initializing MCP clients...")

    await initialize()

    print("\nDiscovered tools:")
    for tool in manager.get_tools():
        print(f" - {tool}")

    print("\nCalling list_notes...\n")

    try:
        result = await manager.call_tool(
            "list_notes",
            {},
        )

        print("SUCCESS")
        print(result)

    except Exception as e:
        print("FAILED")
        print(type(e).__name__)
        print(e)


if __name__ == "__main__":
    asyncio.run(main())