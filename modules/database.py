# @app.get('/db')
# async def read_data(db: Session = Depends(get_db)):
#     return db.query(models.Data).all()

# @app.post('/db')
# async def post_data(data: Data, db: Session = Depends(get_db)):
#     data_model = models.Data()
#     data_model.name = data.name
#     data_model.msg = data.msg

#     db.add(data_model)
#     db.commit()

#     return data

# @app.put('/db/{data_id}')
# async def update_data(data_id: int, data: Data, db: Session = Depends(get_db)):
#     data_model = db.query(models.Data).filter(models.Data.id == data_id).first()
#     if data_model is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f'data with id: {data_id} does not exist'
#         )
    
#     data_model.name = data.name
#     data_model.msg  = data.msg
    
#     db.add(data_model)
#     db.commit()

#     return data

# @app.delete('/db/{data_id}')
# async def delete_data(data_id: int, db: Session = Depends(get_db)):
#     data_model = db.query(models.Data).filter(models.Data.id == data_id).first()
#     if data_model is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f'data with id: {data_id} does not exist'
#         )
#     db.query(models.Data).filter(models.Data.id == data_id).delete()
#     db.commit()
#     return True
  
from pydantic import BaseModel, Field

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class Data(BaseModel):
    name: str = Field(min_length=1)
    msg : str = Field(min_length=1)

class Database:
    class models:
        Base = declarative_base()

        class BaseData(Base):
            __tablename__ = 'my_data'

            id      = Column(Integer, primary_key=True, index=True)
            name    = Column(String)
            msg     = Column(String)

        class BaseUser(Base):
            __tablename__ = 'users'

            user_name       = Column(String, primary_key=True, index=True)
            user_data       = Column(String)
            hashed_password = Column(String)
            disabled        = Column(Boolean)

        #pridat neco na pridavani modelu

    def __init__(self, path: str):
        self.engine         = create_engine(
                                    path,
                                    connect_args={'check_same_thread': False}
                                )
        self.SessionLocal   = sessionmaker(
                                    autocommit=False,
                                    autoflush=False,
                                    bind=self.engine
                                )

    @property
    def session(self):
        try:
            session = self.SessionLocal()
            yield session
        finally: session.close()

    def create_all(self):
        self.models.Base.metadata.create_all(bind=self.engine)

#udelat funkci na prevod mezi detmi BaseModel a Base bo jinak se to zatim robi rucne

a = Data(name='pepa', msg='novak je gay')
print(a)