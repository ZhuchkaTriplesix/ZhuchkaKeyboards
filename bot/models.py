import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from config import user, password, host, db_name

Base = declarative_base()

engine = create_engine(f'postgresql+pg8000://{user}:{password}@{host}/{db_name}', echo=False)

Session = sessionmaker(bind=engine)
session = scoped_session(Session)
conn = engine.connect()


class Users(Base):
    __tablename__ = "kbusers"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(length=32))
    group = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


class UsersCrud:
    @staticmethod
    def add_user(telegram_id: int, username: str) -> object:
        sess = Session()
        user = sess.query(Users).where(Users.id == telegram_id).first()
        if user is not None:
            sess.close()
            return False
        else:
            user = Users(id=telegram_id, username=username)
            sess.add(user)
            sess.commit()
            sess.close()
            return True

    @staticmethod
    def get_user(telegram_id: int) -> object:
        sess = Session()
        user = sess.query(Users).where(Users.id == telegram_id).first()
        if user is not None:
            answer = {"id": user.id, "username": user.username, "group": user.group}
            return answer
        else:
            return False

    @staticmethod
    def update_group(telegram_id: int, group: int) -> object:
        sess = Session()
        user = sess.query(Users).where(Users.id == telegram_id).first()
        if user is not None:
            user.group = group
            sess.commit()
            answer = {"id": user.id, "username": user.username, "group": user.group}
            sess.close()
            return answer
        else:
            sess.close()
            return False

    @staticmethod
    def delete_user(telegram_id: int) -> object:
        sess = Session()
        user = sess.query(Users).where(Users.id == telegram_id).first()
        if user is not None:
            sess.delete(user)
            sess.commit()
            sess.close()
            return True
        else:
            sess.close()
            return False


Base.metadata.create_all(engine)
