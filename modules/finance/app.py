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
st.title("Finance Manager - Receipt Processor")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose page:",
        ["Upload & Verify", "Expenses Dashboard", "Settings"]
    )


# === PAGE 1: Upload & Verify ===
if page == "Upload & Verify":
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

            if st.button("Process Receipt", type="primary"):
                with st.spinner("Processing..."):
                    # Save temp file
                    temp_path = config.temp_uploads / uploaded_file.name
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())

                    # OCR
                    with st.status("Running OCR..."):
                        ocr_text = services['ocr'].extract_text(temp_path)
                        if ocr_text:
                            with st.expander("Raw OCR Text"):
                                st.text(ocr_text)

                    # Parse with LLM
                    with st.status("Parsing with AI..."):
                        parsed_data = services['parser'].parse_receipt(ocr_text)

                    if parsed_data:
                        st.success("Receipt processed successfully!")

                        # Store in session state for editing
                        st.session_state.parsed_data = parsed_data
                        st.session_state.image_path = str(temp_path)
                        st.session_state.ocr_text = ocr_text
                    else:
                        st.error("Failed to parse receipt. Please enter manually.")

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

                    # Parse date safely
                    default_date = datetime.now().date()
                    if data.get('purchase_date'):
                        try:
                            default_date = datetime.fromisoformat(data.get('purchase_date')[:10]).date()
                        except (ValueError, TypeError):
                            pass

                    purchase_date = st.date_input(
                        "Purchase Date*",
                        value=default_date
                    )
                    category = st.selectbox(
                        "Category",
                        ["Groceries", "Transport", "Healthcare", "Entertainment", "Other"]
                    )

                with col2:
                    total_amount = st.number_input(
                        "Total Amount (PLN)*",
                        value=float(data.get('total_amount', 0) or 0),
                        min_value=0.0,
                        step=0.01
                    )
                    tax_number = st.text_input(
                        "Tax Number (NIP)",
                        value=data.get('tax_number', '') or ''
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
                        "Save to Database",
                        type="primary",
                        use_container_width=True
                    )

                with col2:
                    reject = st.form_submit_button(
                        "Reject",
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
                        st.success(f"Expense #{expense.id} saved successfully!")

                        # Clear session
                        del st.session_state.parsed_data
                        del st.session_state.image_path
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error saving: {str(e)}")

                if reject:
                    del st.session_state.parsed_data
                    st.warning("Receipt rejected.")
                    st.rerun()


# === PAGE 2: Dashboard ===
elif page == "Expenses Dashboard":
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
                'Verified': 'Yes' if exp.verified else 'No',
            })

        df = pd.DataFrame(expenses_data)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Expenses", f"{df['Amount (PLN)'].sum():.2f} PLN")
        with col2:
            st.metric("Count", len(df))
        with col3:
            st.metric("Verified", df['Verified'].value_counts().get('Yes', 0))
        with col4:
            st.metric("Pending", df['Verified'].value_counts().get('No', 0))

        # Expenses table
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "expenses.csv",
                "text/csv"
            )


# === PAGE 3: Settings ===
elif page == "Settings":
    st.header("Settings")

    st.info("Configuration loaded from environment variables.")

    st.subheader("Current Settings")
    st.json({
        'OCR Language': config.ocr_language,
        'LLM Model': config.llm_model,
        'Database': config.database_url.split('@')[-1],  # Hide password
        'Vault Path': str(config.vault_path),
    })
