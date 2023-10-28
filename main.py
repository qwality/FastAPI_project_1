# from enum import Enum
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
import jinja2

app = FastAPI()

templates = Jinja2Templates(directory='templates')

@app.get("/")
async def index(request: Request, name: str):
    return templates.TemplateResponse('home.html', {'request': request, 'name': name})

@app.get("/{other}")
async def index(request: Request):
    return '404'
#poznamka



