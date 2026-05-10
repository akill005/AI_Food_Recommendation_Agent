from fastapi import FastAPI

from agent.meal_agent import run_agent

app = FastAPI()


@app.get("/agent")
def meal_agent(query: str):

    response = run_agent(query)

    return {
        "response": response["output"]
    }