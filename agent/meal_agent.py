import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from tools.menu_tools import search_food

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

tools = [search_food]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are Swiggy AI Meal Assistant.

You are an intelligent food recommendation AI agent.

Your responsibilities:
- understand user intent
- understand budgets
- understand veg/non-veg preference
- understand protein preference
- search food database
- recommend best matching item

STRICT RULES:
- Never hallucinate food items
- Use ONLY tool results
- Respect budget strictly
- Respect food preference strictly
- If user asks above 200, never suggest below 200
- If user asks under 200, never suggest above 200

Return clean formatted recommendations.
"""
        ),

        MessagesPlaceholder(variable_name="chat_history"),

        ("human", "{input}"),

        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)


def run_agent(query: str):

    response = agent_executor.invoke(
        {
            "input": query
        }
    )

    return response