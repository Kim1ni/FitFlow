import asyncio
from typing import Optional, List

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset

from fit_flow.wardrobe.database import get_user_wardrobe, add_wardrobe_item, delete_wardrobe_item


class WardrobeDBToolset(BaseToolset):
    """Toolset for wardrobe database tools"""
    def __init__(self, prefix: str = "wardrobe_db_"):
        super().__init__()
        self.tool_name_prefix = prefix

        # Defining function tool instances
        self._get_user_wardrobe_tool = FunctionTool(
            func=get_user_wardrobe
        )
        self._add_to_wardrobe_tool = FunctionTool(
            func=add_wardrobe_item
        )
        self._delete_wardrobe_item_tool = FunctionTool(
            func=delete_wardrobe_item
        )
        print(f"WardrobeDBToolset initialized with prefix '{self.tool_name_prefix}'")

    async def get_tools(
            self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        print(f"ComponentDatabaseToolset get_tools() called.")
        tools_to_return = [
            self._get_user_wardrobe_tool,
            self._add_to_wardrobe_tool,
            self._delete_wardrobe_item_tool
        ]
        return tools_to_return

    async def close(self) -> None:
        # No resources to clean up in this simple example
        print(f"ComponentDatabaseToolset.close() called for prefix '{self.tool_name_prefix}'.")
        await asyncio.sleep(0)  # Placeholder for async cleanup if needed
