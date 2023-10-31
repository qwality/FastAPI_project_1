from pydantic import BaseModel, Field

from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException

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

            @classmethod
            def delete_by_id(cls, id: int, session: Session) -> None:
                query = session.query(cls).filter(cls.id == id).first()
                if query is None:
                    raise HTTPException(
                        status_code=404,
                        detail=f'data with id: {id} does not exist'
                    )
                session.query(cls).filter(cls.id == id).delete()
                session.commit()
            
            @classmethod
            def update_by_id(cls, id: int, data: Data, session: Session) -> None:
                query = session.query(cls).filter(cls.id == id).first()
                if query is None:
                    raise HTTPException(
                        status_code=404,
                        detail=f'data with id: {id} does not exist'
                    )
                
                query: cls = Database.models.to_Base(data, cls)
                
                session.add(query)
                session.commit()

            @classmethod
            def add(cls, data: Data, session: Session) -> None:
                data_model = Database.models.to_Base(data, cls)

                session.add(data_model)
                session.commit()

            @classmethod
            def get_all(cls, session: Session) -> list:
                return session.query(cls).all()

        class BaseUser(Base):
            __tablename__ = 'users'

            user_name       = Column(String, primary_key=True, index=True)
            user_data       = Column(String)
            hashed_password = Column(String)
            disabled        = Column(Boolean)

        @staticmethod
        def to_Base(base_model: BaseModel, cls):
            try:
                ret = cls()
                for key in base_model.model_dump():
                    ret.__setattr__(key, base_model.__getattribute__(key))
                return ret
            except AttributeError: 
                raise AttributeError('spatne nabindovane classy')

        @staticmethod
        def to_BaseModel(base: Base, cls):
            raise NotImplemented

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

    # class Database:
    #     def __init__(self, session: Session, model):
    #         self.session = session
    #         self.model   = model
        
    #     def delete_by_id(self, id):
    #         model = self.session.query(self.model).filter()
            





#udelat funkci na prevod mezi detmi BaseModel a Base bo jinak se to zatim robi rucne

# a = Data(name='pepa', msg='novak je gay')
# b : Database.models.BaseData = Database.models.to_Base(a, Database.models.BaseData)
# # c : Data = Database.models.to_BaseModel(b, Data)
# b.id = 0

# print(b.__dict__)

# print(b.id, b.name, b.msg)
# print(c)