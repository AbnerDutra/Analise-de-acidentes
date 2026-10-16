from sqlalchemy import Column, ForeignKey, Identity, Index, Integer, String
from sqlalchemy.orm import relationship

from ..config.database import Base


class Veiculo(Base):
    __tablename__ = "veiculo"

    idveiculo = Column(Integer, Identity(), primary_key=True)
    idacidente = Column(
        Integer,
        ForeignKey("acidente.idacidente"),
        nullable=False,
    )
    nome_veiculo = Column(String, nullable=False)

    acidente = relationship("Acidente", back_populates="veiculos")

    __table_args__ = (Index("idx_veiculo_idacidente", "idacidente"),)
