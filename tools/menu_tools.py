from langchain.tools import tool
from rag.vector_store import retriever


@tool
def search_food(query: str) -> str:
    """
    Search food items from the menu database.
    Use this tool whenever user asks for food recommendations.
    """

    docs = retriever.invoke(query)

    if not docs:
        return "No food items found."

    results = []

    for d in docs:
        m = d.metadata

        results.append(
            f"""
Food: {m['name']}
Restaurant: {m['restaurant']}
Price: ₹{m['price']}
Type: {m['type']}
Protein: {m['protein']}
Rating: {m['rating']}
"""
        )

    return "\n".join(results)