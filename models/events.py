from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    attendees = Column(Integer)
    notes = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    support_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    support = relationship('User', back_populates='events')
    contract_id = Column(Integer, ForeignKey('contract.id'), nullable=False)
    contract = relationship('Contract', back_populates='events')
