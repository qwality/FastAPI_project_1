# from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
import json
from pydantic import BaseModel, Field
# from pydantic import BaseModel
# import jinja2

import database.models as models
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Data(BaseModel):
    name: str = Field(min_length=1)
    msg : str = Field(min_length=1)


templates = Jinja2Templates(directory='templates')

@app.get("/")
async def index(request: Request, name: str='empty'):
    return templates.TemplateResponse('home.html', {'request': request, 'name': name})

@app.get("/data")
async def get_data():
    data = {"message": "Toto jsou data z FastAPI!"}
    return JSONResponse(content=data)

@app.get('/db')
def read_db(db: Session = Depends(get_db)):
    return db.query(models.Data).all()

@app.post('/db')
def post_db(data: Data, db: Session = Depends(get_db)):
    data_model = models.Data()
    data_model.name = data.name
    data_model.msg = data.msg

    db.add(data_model)
    db.commit()

    return data
    



@app.get("/button/{button_name}", response_class=HTMLResponse)
async def button(request: Request, button_name:str='empty'):
    event_type = json.loads(request.headers.get('triggering-event'))['type']
    context = {
        'request': request,
        'data': {
            'message': f'<strong>button</strong> name is {button_name}',
            'event_type': event_type
            }
        }
    
    # print(request.query_params.multi_items())
    # print()
    print()
    # print()
    # print(request.headers)
    return templates.TemplateResponse('button.html', context)


@app.get("/{other}")
async def index(request: Request):
    return '404'

#dfd


