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

from datetime import datetime, timedelta
from jose import JWSError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_name: str or None = None

class User(BaseModel):
    user_name: str
    user_data: str
    hashed_password: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl='token')

app = FastAPI()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def get_user(db, user_name: str) -> UserInDB | None:
    # ic(user_name)
    if user_name in db:
        # ic('user exists')
        user_data = db[user_name]
        # ic(f'user data exists {user_data}')
        return UserInDB(**user_data)
    else: return None
    
def authenticate_user(db, user_name: str, plain_password: str) -> UserInDB | None:
    user = get_user(db, user_name)
    if user is None:
        return None
    if not verify_password(plain_password, user.hashed_password):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)) -> UserInDB:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get('sub')
        if user_name is None:
            raise credential_exception
        
        token_data = TokenData(user_name=user_name)

    except JWSError:
        raise credential_exception
    
    user = get_user(db, user_name=token_data.user_name)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user

# from icecream import ic

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends()):
    print(f'user_login: {form_data.username}, {form_data.password}')
    user = authenticate_user(db, form_data.username, form_data.password)
    # ic(f'user: {user}')
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
            )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.user_name}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.get('/user/me/', response_model=User)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    print(current_user.user_name)
    return current_user
#fgregre
#fewrter

# @app.get('/user/me/', response_model=User)
# async def read_user_data(current_user: User = Depends(get_current_active_user)):
#     return current_user.user_data


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
def delete_data(data_id: int, db: Session = Depends(get_db)):
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
    
    if trigger_event is not None:
        trigger_event_json = json.loads(trigger_event)
        event_type = trigger_event_json['type']
    else: event_type = 'random shit'
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


