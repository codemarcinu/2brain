import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add shared to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from shared.config import get_settings
from shared.logging import get_logger
from modules.pantry.database.models import Base, PantryProdukt, PantryParagon, PantryPozycjaParagonu, PantryPosilek

logger = get_logger(__name__)

class ProductRepository:
    def __init__(self):
        settings = get_settings()
        self.engine = create_engine(settings.postgres_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self):
        return self.Session()

    def get_pantry_state(self) -> List[Dict]:
        """Calculates current stock: Purchased - Consumed"""
        session = self._get_session()
        try:
            produkty = session.query(PantryProdukt).order_by(PantryProdukt.kategoria, PantryProdukt.nazwa).all()
            pantry_data = []
            for p in produkty:
                # Sum of purchases
                zakupiono = session.query(func.sum(PantryPozycjaParagonu.ilosc)).filter(
                    PantryPozycjaParagonu.produkt_id == p.id
                ).scalar() or 0
                
                # Sum of consumption
                zuzyto = session.query(func.sum(PantryPosilek.ilosc)).filter(
                    PantryPosilek.produkt_id == p.id
                ).scalar() or 0
                
                stan = float(zakupiono) - float(zuzyto)

                pantry_data.append({
                    'id': p.id,
                    'kategoria': p.kategoria or 'Inne',
                    'nazwa': p.nazwa,
                    'stan': round(stan, 2),
                    'minimum_ilosc': float(p.minimum_ilosc) if p.minimum_ilosc else 1.0,
                    'jednostka_miary': p.jednostka_miary or 'szt',
                    'cena_zakupu': float(p.cena_zakupu) if p.cena_zakupu else 0.0
                })
            return pantry_data
        finally:
            session.close()

    def get_product_by_name(self, name: str) -> Optional[PantryProdukt]:
        session = self._get_session()
        try:
            return session.query(PantryProdukt).filter(func.lower(PantryProdukt.nazwa) == name.lower()).first()
        finally:
            session.close()

    def add_or_get_product(self, name: str, category: str = "Inne", unit: str = "szt") -> PantryProdukt:
        """Finds or creates a product definition"""
        session = self._get_session()
        try:
            produkt = session.query(PantryProdukt).filter(func.lower(PantryProdukt.nazwa) == name.lower()).first()
            if not produkt:
                produkt = PantryProdukt(nazwa=name, kategoria=category, jednostka_miary=unit)
                session.add(produkt)
                session.commit()
                session.refresh(produkt)
                logger.info("new_pantry_product_created", name=name)
            return produkt
        finally:
            session.close()

    def add_consumption(self, product_id: int, quantity: float, unit: str) -> bool:
        session = self._get_session()
        try:
            consumption = PantryPosilek(produkt_id=product_id, ilosc=quantity, jednostka_miary=unit)
            session.add(consumption)
            session.commit()
            return True
        except Exception as e:
            logger.error("add_consumption_failed", error=str(e))
            session.rollback()
            return False
        finally:
            session.close()

    def get_unprocessed_receipt_hashes(self, hashes: List[str]) -> List[str]:
        """Check which hashes are NOT in the database yet"""
        session = self._get_session()
        try:
            existing = session.query(PantryParagon.hash_identyfikacyjny).filter(
                PantryParagon.hash_identyfikacyjny.in_(hashes)
            ).all()
            existing_hashes = [r[0] for r in existing]
            return [h for h in hashes if h not in existing_hashes]
        finally:
            session.close()

    def save_transaction(self, shop_name: str, transaction_date: datetime.date, 
                         total_sum: float, receipt_hash: str, source_file: str, items_data: List[Dict]):
        session = self._get_session()
        try:
            paragon = PantryParagon(
                data_zakupow=transaction_date,
                nazwa_sklepu=shop_name,
                suma_calkowita=total_sum,
                hash_identyfikacyjny=receipt_hash,
                plik_zrodlowy=source_file
            )
            session.add(paragon)
            session.flush()

            for item in items_data:
                # Get or create product
                p_name = item.get('nazwa', 'Unknown Item')
                p_cat = item.get('kategoria', 'Inne')
                # Use a separate session logic or careful flushing
                # Since we are in the same repo, let's keep it simple
                produkt = session.query(PantryProdukt).filter(func.lower(PantryProdukt.nazwa) == p_name.lower()).first()
                if not produkt:
                    produkt = PantryProdukt(nazwa=p_name, kategoria=p_cat, jednostka_miary=item.get('jednostka', 'szt'))
                    session.add(produkt)
                    session.flush()
                
                pozycja = PantryPozycjaParagonu(
                    paragon_id=paragon.id,
                    produkt_id=produkt.id,
                    ilosc=item.get('ilosc', 1.0),
                    cena_jednostkowa=item.get('cena', 0.0),
                    cena_calkowita=item.get('suma', 0.0)
                )
                session.add(pozycja)
            
            session.commit()
            logger.info("pantry_receipt_saved", hash=receipt_hash, items=len(items_data))
        except Exception as e:
            logger.error("save_transaction_failed", error=str(e))
            session.rollback()
            raise
        finally:
            session.close()

    def adjust_stock(self, product_id: int, new_stock: float, reason: str = "Korekta") -> bool:
        """Adjusts stock by creating a balancing transaction"""
        session = self._get_session()
        try:
            p = session.query(PantryProdukt).filter_by(id=product_id).first()
            if not p: return False
            
            # Current stock calculation
            zakupiono = session.query(func.sum(PantryPozycjaParagonu.ilosc)).filter(PantryPozycjaParagonu.produkt_id == product_id).scalar() or 0
            zuzyto = session.query(func.sum(PantryPosilek.ilosc)).filter(PantryPosilek.produkt_id == product_id).scalar() or 0
            current_stock = float(zakupiono) - float(zuzyto)
            difference = new_stock - current_stock

            if abs(difference) < 0.001: return True

            today = datetime.now().date()
            if difference > 0:
                # Add "fake" purchase
                receipt_hash = f"ADJUST-{today}-{product_id}-{datetime.now().timestamp()}"
                paragon = PantryParagon(data_zakupow=today, nazwa_sklepu=reason, suma_calkowita=0.0, 
                                        hash_identyfikacyjny=receipt_hash, plik_zrodlowy="Stock Adjust")
                session.add(paragon)
                session.flush()
                pozycja = PantryPozycjaParagonu(paragon_id=paragon.id, produkt_id=product_id, ilosc=difference, 
                                               cena_jednostkowa=0.0, cena_calkowita=0.0)
                session.add(pozycja)
            else:
                # Add consumption
                posilek = PantryPosilek(produkt_id=product_id, ilosc=abs(difference), jednostka_miary=p.jednostka_miary, data=today)
                session.add(posilek)

            session.commit()
            logger.info("stock_adjusted", product=p.nazwa, diff=difference)
            return True
        except Exception as e:
            session.rollback()
            logger.error("stock_adjust_error", error=str(e))
            return False
        finally:
            session.close()
