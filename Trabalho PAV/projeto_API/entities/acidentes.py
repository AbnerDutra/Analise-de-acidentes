from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.orm import relationship

from ..config.database import Base


class Acidente(Base):
    __tablename__ = "acidente"

    idacidente = Column(Integer, Identity(), primary_key=True)
    idlocal = Column(Integer, ForeignKey("local.idlocal"), nullable=False)
    data_acidente = Column(Date, nullable=False)
    hora_acidente = Column(TIME(precision=0), nullable=False)
    nome_clima = Column(String, nullable=False)
    tipo_gravidade = Column(String, nullable=False)
    qtd_vitimas = Column(Integer, nullable=False, default=0)
    qtd_veiculos = Column(Integer, nullable=False)

    local = relationship("Local", back_populates="acidentes")
    veiculos = relationship(
        "Veiculo",
        back_populates="acidente",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "EXTRACT(SECOND FROM hora_acidente) = 0",
            name="ck_hora_hhmm",
        ),
        CheckConstraint("qtd_vitimas >= 0", name="ck_vitimas_nao_negativa"),
        Index("idx_acidente_idlocal", "idlocal"),
    )
