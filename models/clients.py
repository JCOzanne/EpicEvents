from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    company = Column(String(100), nullable=False)
    date_created = Column(Date, nullable=False)
    date_updated = Column(Date, nullable=False)
    commercial_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    commercial = relationship('User', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')
