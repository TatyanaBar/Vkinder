from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, exc
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()
engine = create_engine('postgresql://postgres:123456@localhost:5432/vkinder', echo=False)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    sex = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    relation = Column(Integer, nullable=False)

   def __init__(self, user_id: int, sex: int, age: int, city: str, relation: int):
        super().__init__()
        self.user_id = user_id
        self.sex = sex
        self.age = age
        self.city = city
        self.relation = relation


class View(Base):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    viewed_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

    user = relationship(User, backref='views')

   def __init__(self, viewed_user: int, user_id: int):
        super().__init__()
        self.viewed_user = viewed_user
        self.user_id = user_id


class Like(Base):
    __tablename__ = 'like'
    id = Column(Integer, primary_key=True)
    liked_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

    user = relationship(User, backref='likes')

   def __init__(self, liked_user: int, user_id: int):
        super().__init__()
        self.liked_user = liked_user
        self.user_id = user_id


def is_user(user_id):
    with Session() as session:
        users = session.query(User).filter(User.user_id == user_id).all()
    return True if users else False


def is_viewed(user_id, viewed_user_id):
    with Session() as session:
        views = session.query(View).filter(View.user_id == user_id, View.viewed_user == viewed_user_id).all()
    return True if views else False


def get_user_from_db(user_id):
    with Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
    return user


def add_new_user_in_db(user_id, age, sex_id, relation_id, city):
    user = User(user_id=user_id, age=age, sex=sex_id, city=city, relation=relation_id)
    session = Session()
    try:
        session.add(user)
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
    finally:
        session.close()


def add_view_in_db(user_id, viewed_user_id):
    view = View(user_id=user_id, viewed_user=viewed_user_id)
    session = Session()
    try:
        session.add(view)
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
    finally:
        session.close()


def add_like_in_db(user_id, liked_user_id):
    like = Like(user_id=user_id, liked_user=liked_user_id)
    session = Session()
    try:
        session.add(like)
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
    finally:
        session.close()


def create_tables():
    Base.metadata.create_all(engine)