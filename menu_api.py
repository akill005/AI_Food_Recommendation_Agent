from fastapi import FastAPI
import json

app = FastAPI()
with open("data/menu.json") as f:
    menu = json.load(f)

@app.get("/menu")
def get_menu():
    return menu
