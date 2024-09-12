from typing import Optional, Type, Any
from langchain_core.tools import BaseTool, BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

DEFAULT_STATE = (
    "MATCH (n:知识实体) WHERE n.name CONTAINS $keyword "
        "MATCH (n)-[r]->(m) "
    "RETURN n, r, m"
)


class GraphSearchInput(BaseModel):
    keyword: str = Field(description="One word to search for")

class GraphSearch(BaseTool):
    name = "Graph Search"
    description = "Accept one key word, useful when you need to search for information of a specific entity."
    args_schema: Type[BaseModel] = GraphSearchInput
    return_direct: bool = False

    def _run(self,
             query: str,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""

        return f"Graph search result: {query}"

    async def _arun(
            self,
            query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        # 开销小，直接同步调用
        return self._run(query, run_manager=run_manager.get_sync())