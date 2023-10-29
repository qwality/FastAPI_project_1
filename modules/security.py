
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWSError, jwt
from fastapi import Depends, HTTPException, status



class Security:
    class Token(BaseModel):
        access_token: str
        token_type: str

    class TokenData(BaseModel):
        user_name: str | None = None

    class User(BaseModel):
        user_name: str
        user_data: str
        hashed_password: str
        disabled: bool | None = None

    class UserInDB(User):
        hashed_password: str

    CREDENTIAL_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
            )
    
    _oauth_2_scheme = OAuth2PasswordBearer(tokenUrl='token')

    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int, database):
        self._secret_key                    = secret_key
        self._algorithm                     = algorithm
        self._access_token_expire_minutes   = access_token_expire_minutes
        self._db                            = database

        self._pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

        async def get_current_user(token: str = Depends(Security._oauth_2_scheme)) -> Security.UserInDB:
            try:
                payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
                user_name: str = payload.get('sub')
                if user_name is None:
                    raise self.CREDENTIAL_EXCEPTION
                
                token_data = Security.TokenData(user_name=user_name)

            except JWSError: raise self.CREDENTIAL_EXCEPTION
            
            user = self.get_user(user_name=token_data.user_name)

            if user is None: raise self.CREDENTIAL_EXCEPTION
            
            return user

        async def get_current_active_user(current_user: Security.UserInDB = Depends(get_current_user)) -> Security.UserInDB:
            if current_user.disabled: raise HTTPException(status_code=400, detail='Inactive user')
            return current_user

        self.get_current_user           = get_current_user
        self.get_current_active_user    = get_current_active_user

    @property
    def db(self):
        return self._db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, plain_password: str) -> str:
        return self._pwd_context.hash(plain_password)

    def get_user(self, user_name: str) -> UserInDB | None:
        if user_name in self.db:
            user_data = self.db[user_name]
            return Security.UserInDB(**user_data)
        else: return None
        
    def authenticate_user(self, user_name: str, plain_password: str) -> UserInDB | None:
        user = self.get_user(user_name)
        if user is None: return user
        if not self.verify_password(plain_password, user.hashed_password):
            return None
        
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=self._access_token_expire_minutes)
        to_encode.update({'exp': expire})
        encode_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

        return encode_jwt

    def login_for_access_token(self, form_data: OAuth2PasswordRequestForm) -> dict[str,str]:
        user = self.authenticate_user(form_data.username, form_data.password)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'}
                )
        access_token_expires = timedelta(minutes=self._access_token_expire_minutes)
        access_token = self.create_access_token(data={'sub': user.user_name}, expires_delta=access_token_expires)
        return {'access_token': access_token, 'token_type': 'bearer'}