from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column()
    username : Mapped[str] = mapped_column()
    telegram_id : Mapped[int] = mapped_column()
    age : Mapped[int] = mapped_column()
    sex : Mapped[str] = mapped_column()

    def __repr__(self):
        return f'{self.username} ({self.name})'

def init_db():
    engine = create_engine('sqlite:///db.sqlite3')
    Base.metadata.create_all(engine)
    return Session(bind=engine)

async def get_user(session, telegram_id):
    return await session.query(User).filter(User.telegram_id == telegram_id).first()

def save_user(session, user):
    session.add(user)
    session.commit()