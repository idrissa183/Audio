from datetime import datetime

from sqlalchemy import Boolean, Column, String, Integer, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.app.db.database import Base
from sqlalchemy.ext.hybrid import hybrid_property


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(length=50), nullable=False)
    lastname = Column(String(length=50), nullable=False)
    email = Column(String(length=100), unique=True, index=True, nullable=False)
    password = Column(String(length=128), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relations
    sessions = relationship('Session', back_populates='user')

    # google_sub = Column(String(length=100), unique=True, nullable=True)
    # github_sub = Column(String(length=100), unique=True, nullable=True)
    # profile_picture = Column(String(length=255), nullable=True)

    # auth_type = Column(String(length=20), nullable=False)  # 'credentials', 'google', 'github'
    # is_active = Column(Boolean, default=True)

    # updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)

    @hybrid_property
    def username(self):
        return f"{self.lastname[0]}{self.firstname[0]}".upper()



class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(Integer, ForeignKey('users.uid'), nullable=False)
    session_name = Column(String(length=100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    user = relationship('User', back_populates='sessions')
    messages = relationship('Message', back_populates='session')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    sender = Column(String(length=100), nullable=False)  # Could be username or email
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    session = relationship('Session', back_populates='messages')