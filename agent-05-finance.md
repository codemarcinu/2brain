# Agent 5: Finance Service

## 🎭 Rola
**Full-Stack Developer (Python + Web UI)**

## 🎯 Cel
Aplikacja webowa do weryfikacji i zatwierdzania paragonów przez człowieka

## 📖 Kontekst

Automatyczne wrzucanie paragonów do bazy jest ryzykowne (błędy OCR, źle odczytane ceny). Finance Service wprowadza **Human-in-the-loop**:

1. Upload paragonu → OCR → AI parsing
2. **Człowiek weryfikuje** dane w UI (poprawia błędy)
3. Zatwierdza → Zapis do PostgreSQL
4. (Opcjonalnie) Dodanie do notatki wydatków w Obsidian

### Przepływ:
```
Paragon (zdjęcie) → OCR → DeepSeek Parsing → Streamlit UI → PostgreSQL
                                                ↓
                                          Obsidian note (summary)
```

## ✅ Zadania

### 1. Struktura Projektu

```
modules/finance/
├── Dockerfile
├── requirements.txt
├── app.py                    # Streamlit app (main UI)
├── config.py                 # Konfiguracja
├── services/
│   ├── __init__.py
│   ├── ocr_engine.py         # Tesseract/PaddleOCR
│   ├── llm_parser.py         # DeepSeek dla structured data
│   └── db_manager.py         # SQLAlchemy ORM
├── models/
│   ├── __init__.py
│   └── expense.py            # SQLAlchemy models
├── utils/
│   ├── __init__.py
│   └── image_processor.py    # Preprocessing obrazów
└── scripts/
    ├── init_db.py            # Inicjalizacja bazy
    └── export_csv.py         # Export do CSV/Excel
```

### 2. Dockerfile

```dockerfile
FROM python:3.10-slim

LABEL maintainer="your@email.com"
LABEL description="Finance service with Streamlit UI"

# Zainstaluj Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-pol \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e /shared

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.headless", "true"]
```

### 3. requirements.txt

```txt
# Streamlit
streamlit>=1.30.0

# OCR
pytesseract>=0.3.10
pillow>=10.0.0
opencv-python-headless>=4.8.0

# Alternative OCR (optional)
# paddleocr>=2.7.0

# LLM for parsing
openai>=1.10.0  # For DeepSeek API

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
alembic>=1.13.0

# Utilities
pandas>=2.1.0
plotly>=5.18.0  # For charts in UI
```

### 4. config.py

```python
"""
Konfiguracja Finance Service
"""
from pathlib import Path
from shared.config import get_settings as get_base_settings


class FinanceConfig:
    """Rozszerzona konfiguracja dla Finance"""
    
    def __init__(self):
        self.base = get_base_settings()
        
        # Paths
        self.receipts_folder = Path("/inbox/receipts")  # Mounted volume
        self.temp_uploads = Path("/tmp/finance_uploads")
        
        # LLM Settings (OpenAI Nano lub DeepSeek)
        self.ai_provider = self.base.ai_provider # "openai" lub "ollama"
        self.llm_model = self.base.openai_model # np. "gpt-5-nano"
        self.llm_api_key = self.base.openai_api_key
        
        # OCR Settings
        self.ocr_provider = self.base.ocr_provider # "google_vision" lub "tesseract"
        self.ocr_language = "pol+eng"  # Tesseract language
        
        # Database
        self.database_url = self.base.postgres_url
        
        # Obsidian integration (optional)
        self.vault_path = Path(self.base.obsidian_vault_path)
        self.expenses_note_path = self.vault_path / "Finance" / "Monthly Expenses"
        
        # UI Settings
        self.page_title = "Obsidian Brain - Finance Manager"
        self.page_icon = "💰"
        
        # Ensure paths exist
        self.receipts_folder.mkdir(parents=True, exist_ok=True)
        self.temp_uploads.mkdir(parents=True, exist_ok=True)
        self.expenses_note_path.parent.mkdir(parents=True, exist_ok=True)


config = FinanceConfig()
```

### 5. models/expense.py

```python
"""
SQLAlchemy models dla wydatków
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Expense(Base):
    """Model wydatku"""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    
    # Receipt info
    image_path = Column(String(500), nullable=False)
    image_hash = Column(String(64))  # MD5 dla deduplikacji
    
    # Parsed data
    shop_name = Column(String(200))
    purchase_date = Column(DateTime)
    total_amount = Column(Float, nullable=False)
    tax_number = Column(String(50))  # NIP
    
    # Items (JSON array)
    items = Column(JSON)  # [{"name": "...", "price": ..., "quantity": ...}]
    
    # OCR raw data (backup)
    ocr_raw_text = Column(String)
    
    # Metadata
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(String(100))  # User ID/name (future)
    
    # Categories
    category = Column(String(100))  # "Groceries", "Transport", etc.
    tags = Column(JSON)  # Additional tags
    
    # Notes
    notes = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dict for JSON serialization"""
        return {
            'id': self.id,
            'shop_name': self.shop_name,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'total_amount': self.total_amount,
            'items': self.items,
            'category': self.category,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
        }
```

### 6. services/ocr_engine.py

```python
"""
OCR Engine using Google Vision API (primary) or Tesseract (fallback)
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from pathlib import Path
from shared.logging import get_logger

logger = get_logger(__name__)


class OCREngine:
    """Wrapper dla Tesseract OCR"""
    
    def __init__(self, language: str = "pol+eng", dpi: int = 300):
        self.language = language
        self.dpi = dpi
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocessing obrazu dla lepszego OCR
        - Grayscale
        - Contrast enhancement
        - Denoising
        - Thresholding
        """
        # Convert PIL to OpenCV
        img_array = np.array(image)
        
        # Grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Adaptive threshold (lepiej radzi sobie z nierónym oświetleniem)
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Convert back to PIL
        return Image.fromarray(thresh)
    
    def extract_text(self, image_path: Path) -> str:
        """
        Wyciągnij tekst z obrazu
        
        Args:
            image_path: Ścieżka do zdjęcia paragonu
        
        Returns:
            Surowy tekst z OCR
        """
        try:
            logger.info("ocr_started", image=image_path.name)
            
            # Load image
            image = Image.open(image_path)
            
            # Preprocessing
            processed = self.preprocess_image(image)
            
            # OCR
            custom_config = f'--oem 3 --psm 6 -l {self.language}'
            text = pytesseract.image_to_string(
                processed,
                config=custom_config
            )
            
            logger.info(
                "ocr_completed",
                image=image_path.name,
                text_length=len(text)
            )
            
            return text
            
        except Exception as e:
            logger.error("ocr_failed", image=image_path.name, error=str(e))
            return ""
```

### 7. services/llm_parser.py

```python
"""
LLM Parser do wyciągania strukturalnych danych z OCR
"""
import json
from typing import Optional, Dict
from openai import OpenAI
from shared.logging import get_logger
from config import config

logger = get_logger(__name__)


class ReceiptParser:
    """Parser paragonów używający DeepSeek/GPT"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url
        )
        self.model = config.llm_model
    
    def parse_receipt(self, ocr_text: str) -> Optional[Dict]:
        """
        Parse OCR text do strukturalnego JSON
        
        Args:
            ocr_text: Surowy tekst z OCR
        
        Returns:
            Dict z shop, date, items, total
        """
        prompt = f"""You are a receipt parser. Extract structured data from this OCR text.

OCR Text:
{ocr_text}

Extract the following information:
1. Shop name
2. Purchase date (format: YYYY-MM-DD)
3. Items list (name, price, quantity)
4. Total amount
5. Tax number (NIP) if present

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "shop_name": "...",
  "purchase_date": "YYYY-MM-DD",
  "total_amount": 123.45,
  "tax_number": "...",
  "items": [
    {{"name": "...", "price": 12.34, "quantity": 2}},
    ...
  ]
}}

If you cannot extract certain fields, use null. Be precise with numbers.
"""
        
        try:
            logger.info("llm_parsing_started")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Deterministyczne dla danych liczbowych
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            # Remove markdown if present
            cleaned = content.strip()
            if cleaned.startswith('```'):
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                cleaned = cleaned[start:end]
            
            result = json.loads(cleaned)
            
            logger.info(
                "llm_parsing_success",
                shop=result.get('shop_name'),
                total=result.get('total_amount')
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error("llm_json_parse_failed", error=str(e))
            return None
        except Exception as e:
            logger.error("llm_parsing_failed", error=str(e))
            return None
```

### 8. services/db_manager.py

```python
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
        logger.info("database_initialized", url=self.database_url)
    
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
```

### 9. app.py (Streamlit UI)

```python
"""
Streamlit UI dla Finance Manager
"""
import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd
from PIL import Image
from services.ocr_engine import OCREngine
from services.llm_parser import ReceiptParser
from services.db_manager import DatabaseManager
from shared.logging import setup_logging, get_logger
from config import config

# Setup
setup_logging(level="INFO", format="console", service_name="finance-ui")
logger = get_logger(__name__)

st.set_page_config(
    page_title=config.page_title,
    page_icon=config.page_icon,
    layout="wide"
)


# Initialize services (cache)
@st.cache_resource
def get_services():
    return {
        'ocr': OCREngine(language=config.ocr_language),
        'parser': ReceiptParser(),
        'db': DatabaseManager()
    }


services = get_services()


# === MAIN UI ===
st.title("💰 Finance Manager - Receipt Processor")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose page:",
        ["📤 Upload & Verify", "📊 Expenses Dashboard", "⚙️ Settings"]
    )


# === PAGE 1: Upload & Verify ===
if page == "📤 Upload & Verify":
    st.header("Upload Receipt")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose receipt image",
        type=["jpg", "jpeg", "png", "pdf"],
        help="Upload a photo of your receipt"
    )
    
    if uploaded_file:
        # Show image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Receipt Image")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("Extracted Data")
            
            if st.button("🔍 Process Receipt", type="primary"):
                with st.spinner("Processing..."):
                    # Save temp file
                    temp_path = config.temp_uploads / uploaded_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # OCR
                    with st.status("Running OCR..."):
                        ocr_text = services['ocr'].extract_text(temp_path)
                        if ocr_text:
                            with st.expander("📄 Raw OCR Text"):
                                st.text(ocr_text)
                    
                    # Parse with LLM
                    with st.status("Parsing with AI..."):
                        parsed_data = services['parser'].parse_receipt(ocr_text)
                    
                    if parsed_data:
                        st.success("✅ Receipt processed successfully!")
                        
                        # Store in session state for editing
                        st.session_state.parsed_data = parsed_data
                        st.session_state.image_path = str(temp_path)
                        st.session_state.ocr_text = ocr_text
                    else:
                        st.error("❌ Failed to parse receipt. Please enter manually.")
        
        # Edit form
        if 'parsed_data' in st.session_state:
            st.divider()
            st.subheader("Verify & Edit")
            
            data = st.session_state.parsed_data
            
            with st.form("receipt_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    shop_name = st.text_input(
                        "Shop Name*",
                        value=data.get('shop_name', '')
                    )
                    purchase_date = st.date_input(
                        "Purchase Date*",
                        value=datetime.fromisoformat(data.get('purchase_date', datetime.now().isoformat())[:10])
                    )
                    category = st.selectbox(
                        "Category",
                        ["Groceries", "Transport", "Healthcare", "Entertainment", "Other"]
                    )
                
                with col2:
                    total_amount = st.number_input(
                        "Total Amount (PLN)*",
                        value=float(data.get('total_amount', 0)),
                        min_value=0.0,
                        step=0.01
                    )
                    tax_number = st.text_input(
                        "Tax Number (NIP)",
                        value=data.get('tax_number', '')
                    )
                    notes = st.text_area("Notes", "")
                
                # Items table
                st.subheader("Items")
                items = data.get('items', [])
                
                if items:
                    items_df = pd.DataFrame(items)
                    edited_items = st.data_editor(
                        items_df,
                        num_rows="dynamic",
                        use_container_width=True
                    )
                else:
                    st.info("No items detected. Add manually if needed.")
                    edited_items = pd.DataFrame(columns=['name', 'price', 'quantity'])
                
                # Submit buttons
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    submit = st.form_submit_button(
                        "✅ Save to Database",
                        type="primary",
                        use_container_width=True
                    )
                
                with col2:
                    reject = st.form_submit_button(
                        "❌ Reject",
                        use_container_width=True
                    )
                
                if submit:
                    # Save to database
                    expense_data = {
                        'image_path': st.session_state.image_path,
                        'shop_name': shop_name,
                        'purchase_date': datetime.combine(purchase_date, datetime.min.time()),
                        'total_amount': total_amount,
                        'tax_number': tax_number or None,
                        'items': edited_items.to_dict('records'),
                        'ocr_raw_text': st.session_state.ocr_text,
                        'category': category,
                        'notes': notes,
                        'verified': True,
                        'verified_at': datetime.utcnow(),
                    }
                    
                    try:
                        expense = services['db'].add_expense(expense_data)
                        st.success(f"✅ Expense #{expense.id} saved successfully!")
                        
                        # Clear session
                        del st.session_state.parsed_data
                        del st.session_state.image_path
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error saving: {str(e)}")
                
                if reject:
                    del st.session_state.parsed_data
                    st.warning("Receipt rejected.")
                    st.rerun()


# === PAGE 2: Dashboard ===
elif page == "📊 Expenses Dashboard":
    st.header("Expenses Overview")
    
    # Load expenses
    expenses = services['db'].get_all_expenses(limit=100)
    
    if not expenses:
        st.info("No expenses yet. Upload your first receipt!")
    else:
        # Convert to DataFrame
        expenses_data = []
        for exp in expenses:
            expenses_data.append({
                'ID': exp.id,
                'Date': exp.purchase_date,
                'Shop': exp.shop_name,
                'Amount (PLN)': exp.total_amount,
                'Category': exp.category,
                'Verified': '✅' if exp.verified else '❌',
            })
        
        df = pd.DataFrame(expenses_data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Expenses", f"{df['Amount (PLN)'].sum():.2f} PLN")
        with col2:
            st.metric("Count", len(df))
        with col3:
            st.metric("Verified", df['Verified'].value_counts().get('✅', 0))
        with col4:
            st.metric("Pending", df['Verified'].value_counts().get('❌', 0))
        
        # Expenses table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export
        if st.button("💾 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "expenses.csv",
                "text/csv"
            )


# === PAGE 3: Settings ===
elif page == "⚙️ Settings":
    st.header("Settings")
    
    st.info("Configuration loaded from environment variables.")
    
    st.subheader("Current Settings")
    st.json({
        'OCR Language': config.ocr_language,
        'LLM Model': config.llm_model,
        'Database': config.database_url.split('@')[-1],  # Hide password
        'Vault Path': str(config.vault_path),
    })
```

### 10. Aktualizacja docker-compose.yml

```yaml
finance:
  build:
    context: ./modules/finance
    dockerfile: Dockerfile
  container_name: brain-finance
  ports:
    - "8501:8501"
  volumes:
    - ${INBOX_PATH}/receipts:/inbox/receipts
    - ./shared:/shared:ro
  environment:
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - POSTGRES_DB=${POSTGRES_DB}
    - POSTGRES_HOST=postgres
    - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - brain-network
  restart: unless-stopped
```

## 🎯 Kryteria Sukcesu

```bash
# 1. Build
docker compose build finance

# 2. Start
docker compose up -d finance

# 3. Open UI
open http://localhost:8501

# 4. Test workflow:
# - Upload receipt image
# - Verify OCR results
# - Edit if needed
# - Save to database

# 5. Check database
docker exec -it brain-postgres psql -U brain -d obsidian_brain -c "SELECT * FROM expenses;"
```

### Checklist:
- [x] Streamlit UI działa na localhost:8501
- [x] OCR wyciąga tekst z paragonu
- [x] LLM parsuje do struktury JSON
- [x] Edycja pozycji w tabeli działa
- [x] Zapis do PostgreSQL działa
- [x] Dashboard pokazuje wydatki

## 📦 Pliki Wyjściowe

Kompletny mikroserwis `modules/finance/` z UI.

## 🔗 Zależności

**Wymaga:**
- ✅ Agent 1 (PostgreSQL)
- ✅ Agent 2 (Shared Library)

---

**Status:** ✅ Zaimplementowany
**Czas:** ~60 minut
