from sqlalchemy import Column, INTEGER, VARCHAR, PrimaryKeyConstraint, Index
from database import Base
import jwt
from config import settings


class UserDao(Base):
    __tablename__ = 'user'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    first_name = Column(VARCHAR, nullable=False)
    second_name = Column(VARCHAR, nullable=False)
    password = Column(VARCHAR, nullable=False)
    login = Column(VARCHAR, nullable=False, unique=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pkey'),
        Index("login_index", "login")
    )

    def get_token(self):
        token = jwt.encode({'user_id': self.id}, key=settings.jwt_secret_key,
                           algorithm=settings.algorithm)
        return token
