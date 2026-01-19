"""
Database Manager using SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime
from models.expense import Base, Expense
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)


class DatabaseManager:
    """Manager dla bazy wydatków"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or config.database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info("database_initialized", url=self.database_url.split('@')[-1])

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def add_expense(self, expense_data: dict) -> Expense:
        """
        Dodaj nowy wydatek

        Args:
            expense_data: Dict z danymi wydatku

        Returns:
            Expense object
        """
        session = self.get_session()

        try:
            expense = Expense(**expense_data)
            session.add(expense)
            session.commit()
            session.refresh(expense)

            logger.info("expense_added", expense_id=expense.id, shop=expense.shop_name)
            return expense

        except Exception as e:
            session.rollback()
            logger.error("expense_add_failed", error=str(e))
            raise
        finally:
            session.close()

    def get_all_expenses(self, limit: int = 100) -> List[Expense]:
        """Pobierz ostatnie wydatki"""
        session = self.get_session()
        try:
            return session.query(Expense).order_by(
                Expense.created_at.desc()
            ).limit(limit).all()
        finally:
            session.close()

    def get_pending_expenses(self) -> List[Expense]:
        """Pobierz wydatki oczekujące na weryfikację"""
        session = self.get_session()
        try:
            return session.query(Expense).filter(
                Expense.verified == False
            ).order_by(Expense.created_at.desc()).all()
        finally:
            session.close()

    def verify_expense(self, expense_id: int, verified_by: str = "user") -> bool:
        """Oznacz wydatek jako zweryfikowany"""
        session = self.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                expense.verified = True
                expense.verified_at = datetime.utcnow()
                expense.verified_by = verified_by
                session.commit()
                logger.info("expense_verified", expense_id=expense_id)
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error("expense_verify_failed", expense_id=expense_id, error=str(e))
            return False
        finally:
            session.close()

    def update_expense(self, expense_id: int, expense_data: dict) -> Optional[Expense]:
        """Update istniejącego wydatku"""
        session = self.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                for key, value in expense_data.items():
                    if hasattr(expense, key):
                        setattr(expense, key, value)
                session.commit()
                session.refresh(expense)
                logger.info("expense_updated", expense_id=expense_id)
                return expense
            return None
        except Exception as e:
            session.rollback()
            logger.error("expense_update_failed", expense_id=expense_id, error=str(e))
            raise
        finally:
            session.close()

    def delete_expense(self, expense_id: int) -> bool:
        """Usuń wydatek"""
        session = self.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                session.delete(expense)
                session.commit()
                logger.info("expense_deleted", expense_id=expense_id)
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error("expense_delete_failed", expense_id=expense_id, error=str(e))
            return False
        finally:
            session.close()
