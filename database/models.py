from sqlalchemy import Column, Integer, String
from .database import Base

class Data(Base):
    __tablename__ = 'my_data'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    msg = Column(String)