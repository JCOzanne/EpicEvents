from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    role = relationship('Role', back_populates='users')
    clients = relationship('Client', back_populates='commercial')
    events = relationship('Event', back_populates='support')
