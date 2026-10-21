from sqlalchemy import Column, Identity, Integer, String
from sqlalchemy.orm import relationship

from ..config.database import Base


class Local(Base):
    __tablename__ = 'local'

    idlocal = Column(Integer, Identity(), primary_key=True)
    estado = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    bairro = Column(String)
    rua = Column(String)

    acidentes = relationship('Acidente', back_populates='local')