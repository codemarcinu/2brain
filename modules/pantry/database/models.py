from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class PantryProdukt(Base):
    """Product definition in the pantry"""
    __tablename__ = 'pantry_produkty'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String(255), unique=True, nullable=False)
    kategoria = Column(String(100))
    jednostka_miary = Column(String(50))
    cena_zakupu = Column(Numeric(10, 2))
    dostawca = Column(String(255))
    minimum_ilosc = Column(Numeric(10, 2), default=1.0)
    
    pozycje = relationship("PantryPozycjaParagonu", back_populates="produkt")
    consunptions = relationship("PantryPosilek", back_populates="produkt")

class PantryParagon(Base):
    """A purchase transaction (Receipt)"""
    __tablename__ = 'pantry_paragony'
    id = Column(Integer, primary_key=True)
    data_zakupow = Column(Date, nullable=False)
    nazwa_sklepu = Column(String(255))
    suma_calkowita = Column(Numeric(10, 2))
    hash_identyfikacyjny = Column(String(255), unique=True)
    plik_zrodlowy = Column(String(512))
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    pozycje = relationship("PantryPozycjaParagonu", back_populates="paragon", cascade="all, delete-orphan")

class PantryPozycjaParagonu(Base):
    """A specific item on a receipt (Ledger: IN)"""
    __tablename__ = 'pantry_pozycje_paragonu'
    id = Column(Integer, primary_key=True)
    paragon_id = Column(Integer, ForeignKey('pantry_paragony.id'))
    produkt_id = Column(Integer, ForeignKey('pantry_produkty.id'))
    ilosc = Column(Numeric(10, 3))
    cena_jednostkowa = Column(Numeric(10, 2))
    rabat = Column(Numeric(10, 2))
    cena_calkowita = Column(Numeric(10, 2))
    data_waznosci = Column(Date, nullable=True)
    
    paragon = relationship("PantryParagon", back_populates="pozycje")
    produkt = relationship("PantryProdukt", back_populates="pozycje")

class PantryPosilek(Base):
    """A consumption transaction (Ledger: OUT)"""
    __tablename__ = 'pantry_posilki'
    id = Column(Integer, primary_key=True)
    produkt_id = Column(Integer, ForeignKey('pantry_produkty.id'))
    ilosc = Column(Numeric(10, 3))
    jednostka_miary = Column(String(50))
    data = Column(Date, default=datetime.utcnow().date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    produkt = relationship("PantryProdukt", back_populates="consunptions")
