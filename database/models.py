from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Data(Base):
    __tablename__ = 'my_data'

    id      = Column(Integer, primary_key=True, index=True)
    name    = Column(String)
    msg     = Column(String)

    @classmethod
    def a(cls):
        return 'a'

class User(Base):
    __tablename__ = 'users'

    user_name       = Column(String, primary_key=True, index=True)
    user_data       = Column(String)
    hashed_password = Column(String)
    disabled        = Column(Boolean)

# db = {
#     'user_1_should_be_name': {
#         'user_name': 'user_1_should_be_name',
#         'user_data': 'some random data',
#         'hashed_password': '$2b$12$GQu6M9Jw8GzEoKigjYVNWePEcHvnknNkX1eo/UM3MuE/Y.SyftFou',#1234
#         'disabled': False
#     }
# }