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

# from datetime import datetime, timedelta
# from jose import JWSError, jwt
# from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi import status

app = FastAPI()
templates = Jinja2Templates(directory='templates')

#openssl rand -hex 32
SECRET_KEY = '9e21b7282bfdb4f6c2cb488d8ba9b89898da79c1990c95b338e2ee5dc253396c'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

db = {
    'user_1_should_be_name': {
        'user_name': 'user_1_should_be_name',
        'user_data': 'some random data',
        'hashed_password': '$2b$12$GQu6M9Jw8GzEoKigjYVNWePEcHvnknNkX1eo/UM3MuE/Y.SyftFou',#1234
        'disabled': False
    }
}

from modules.security import Security

security = Security(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, db)

@app.post('/token', response_model=Security.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends()):
    print(f'usr: {form_data.username}\npswd: {form_data.password}')
    return security.login_for_access_token(form_data)

@app.get('/user/me/', response_model=Security.User)
async def read_user_me(current_user: Security.User = Depends(security.get_current_active_user)):
    print(current_user.user_name)
    return current_user

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

@app.get("/")
async def index(request: Request, name: str='empty'):
    return templates.TemplateResponse('home.html', {'request': request, 'name': name})

@app.get("/data")
async def get_data():
    data = {"message": "Toto jsou data z FastAPI!"}
    return JSONResponse(content=data)

@app.get('/db')
async def read_data(db: Session = Depends(get_db)):
    return db.query(models.Data).all()

@app.post('/db')
async def post_data(data: Data, db: Session = Depends(get_db)):
    data_model = models.Data()
    data_model.name = data.name
    data_model.msg = data.msg

    db.add(data_model)
    db.commit()

    return data

@app.put('/db/{data_id}')
async def update_data(data_id: int, data: Data, db: Session = Depends(get_db)):
    data_model = db.query(models.Data).filter(models.Data.id == data_id).first()
    if data_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'data with id: {data_id} does not exist'
        )
    
    data_model.name = data.name
    data_model.msg  = data.msg
    
    db.add(data_model)
    db.commit()

    return data

@app.delete('/db/{data_id}')
async def delete_data(data_id: int, db: Session = Depends(get_db)):
    data_model = db.query(models.Data).filter(models.Data.id == data_id).first()
    if data_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'data with id: {data_id} does not exist'
        )
    db.query(models.Data).filter(models.Data.id == data_id).delete()
    db.commit()
    return True
    
@app.get("/button/{button_name}", response_class=HTMLResponse)
async def button(request: Request, button_name:str='empty'):
    trigger_event = request.headers.get('triggering-event')
    
    event_type = json.loads(trigger_event)['type'] if trigger_event is not None else 'unknown event'

    context = {
        'request': request,
        'data': {
            'message': f'<strong>button</strong> name is {button_name}',
            'event_type': event_type
            }
        }
    
    return templates.TemplateResponse('button.html', context)

@app.get("/{other}", response_class=HTMLResponse)
async def index(request: Request, other: str=''):
    return f'{other} is not a thing u fool'

#dfd


