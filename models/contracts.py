from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.database import Base


class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    sold = Column(Float, nullable=False)
    date_created = Column(Date, nullable=False)
    status = Column(Boolean, nullable=False)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    client = relationship('Client', back_populates='contracts')
    events = relationship('Event', back_populates='contract')
