from tools.menu_tools import search_food
def run_agent(query: str, session_id: str = "default"):
    try:
        result = search_food.invoke(
            {
                "query": query
            }
        )
        return {
            "output": result
        }
    except Exception as e:
        return {
            "output": str(e),
            "error": True
        }