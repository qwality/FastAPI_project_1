# from enum import Enum
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
# from pydantic import BaseModel
# import jinja2

app = FastAPI()

templates = Jinja2Templates(directory='templates')

@app.get("/")
async def index(request: Request, name: str='empty'):
    return templates.TemplateResponse('home.html', {'request': request, 'name': name})

@app.get("/data")
async def get_data():
    data = {"message": "Toto jsou data z FastAPI!"}
    return JSONResponse(content=data)

@app.get("/button/{button_name}", response_class=HTMLResponse)
async def button(request: Request, button_name:str='empty'):
    context = {'request': request, 'data':{"message": f"<strong>button</strong> name is {button_name}"}}
    print('button pressed')
    return templates.TemplateResponse('button.html', context)


@app.get("/{other}")
async def index(request: Request):
    return '404'

#dfd


