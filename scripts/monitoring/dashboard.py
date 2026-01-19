"""
Monitoring Dashboard - Streamlit
"""
import streamlit as st
import redis
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from shared.config import get_settings
import psycopg2.extras
import json
import os
import sys
from pathlib import Path

# Add project root to path for module imports
sys.path.append(str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Obsidian Brain - Monitor", page_icon="📊", layout="wide")

settings = get_settings()


# Redis client
@st.cache_resource
def get_redis():
    return redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


# Postgres connection
@st.cache_resource
def get_db():
    return psycopg2.connect(
        host=settings.postgres_host,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db
    )


st.title("📊 Obsidian Brain - System Monitor")

# Refresh button
if st.button("🔄 Refresh"):
    st.cache_resource.clear()
    st.rerun()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "📋 Queues", "💰 Expenses", "👨‍💻 Human In The Loop", "📦 Pantry"])


# === TAB 1: Overview ===
with tab1:
    st.header("System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Redis status
    with col1:
        try:
            r = get_redis()
            r.ping()
            st.metric("Redis", "✅ Healthy", delta="Online")
        except:
            st.metric("Redis", "❌ Down", delta="Offline")
    
    # Postgres status
    with col2:
        try:
            db = get_db()
            st.metric("PostgreSQL", "✅ Healthy", delta="Online")
        except:
            st.metric("PostgreSQL", "❌ Down", delta="Offline")
    
    # Queue stats
    with col3:
        try:
            r = get_redis()
            total_tasks = (
                r.llen("queue:collector") +
                r.llen("queue:refinery") +
                r.llen("queue:finance")
            )
            st.metric("Pending Tasks", total_tasks)
        except:
            st.metric("Pending Tasks", "N/A")
    
    # Expenses today
    with col4:
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM expenses 
                WHERE created_at >= CURRENT_DATE
            """)
            count = cursor.fetchone()[0]
            st.metric("Expenses Today", count)
        except:
            st.metric("Expenses Today", "N/A")


# === TAB 2: Queues ===
with tab2:
    st.header("Redis Queues")
    
    try:
        r = get_redis()
        
        queues = {
            "queue:collector": r.llen("queue:collector"),
            "queue:refinery": r.llen("queue:refinery"),
            "queue:finance": r.llen("queue:finance"),
        }
        
        # Bar chart
        df = pd.DataFrame([
            {"Queue": k.split(':')[1].title(), "Tasks": v}
            for k, v in queues.items()
        ])
        
        fig = px.bar(df, x="Queue", y="Tasks", title="Queue Depths")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Failed to load queues: {e}")



# === TAB 3: Expenses ===
with tab3:
    st.header("Expenses Analytics")
    
    try:
        db = get_db()
        
        # Last 30 days
        query = """
        SELECT 
            DATE(purchase_date) as date,
            SUM(total_amount) as total
        FROM expenses
        WHERE purchase_date >= CURRENT_DATE - INTERVAL '30 days' AND verified = TRUE
        GROUP BY DATE(purchase_date)
        ORDER BY date DESC
        """
        
        df = pd.read_sql(query, db)
        
        if not df.empty:
            # Line chart
            fig = px.line(df, x='date', y='total', title="Daily Expenses (Verified) - Last 30 Days")
            st.plotly_chart(fig, use_container_width=True)
            
            # Since we don't have a category column in the current schema yet, 
            # let's just show the raw data for now or a simple summary.
            # (The schema I created has shop_name, total_amount, etc but not 'category' explicitly, 
            # though it might be inside the JSON items).
            
            st.subheader("Recent Verified Expenses")
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT shop_name, total_amount, purchase_date FROM expenses WHERE verified = TRUE ORDER BY purchase_date DESC LIMIT 10")
            recent = cursor.fetchall()
            if recent:
                st.table(recent)
        else:
            st.info("No verified expenses in last 30 days")
            
    except Exception as e:
        st.error(f"Failed to load expenses: {e}")


# === TAB 4: Human In The Loop ===
with tab4:
    st.header("Verify & Approve Expenses")
    st.write("Review and edit auto-extracted data before finalizing.")

    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 1. Fetch unverified
        cursor.execute("SELECT * FROM expenses WHERE verified = FALSE ORDER BY created_at DESC")
        unverified = cursor.fetchall()

        if not unverified:
            st.success("All expenses are verified! 🎉")
        else:
            for exp in unverified:
                with st.expander(f"🛒 {exp['shop_name']} - {exp['total_amount']} PLN ({exp['created_at'].strftime('%Y-%m-%d %H:%M')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_shop = st.text_input("Shop Name", exp['shop_name'], key=f"shop_{exp['id']}")
                        new_total = st.number_input("Total Amount", value=float(exp['total_amount']), key=f"total_{exp['id']}")
                        new_date = st.date_input("Purchase Date", value=exp['purchase_date'].date() if exp['purchase_date'] else datetime.now().date(), key=f"date_{exp['id']}")
                    
                    with col2:
                        # Items editor (simplified)
                        st.write("**Items extracted:**")
                        items_json = json.dumps(exp['items'], indent=2, ensure_ascii=False)
                        new_items_str = st.text_area("Items (JSON)", value=items_json, height=150, key=f"items_{exp['id']}")
                        
                        try:
                            new_items = json.loads(new_items_str)
                        except:
                            st.error("Invalid JSON in items")
                            new_items = exp['items']

                    if st.button("✅ Approve & Save", key=f"approve_{exp['id']}"):
                        try:
                            update_cursor = db.cursor()
                            update_cursor.execute("""
                                UPDATE expenses 
                                SET shop_name = %s, total_amount = %s, purchase_date = %s, items = %s, verified = TRUE, updated_at = NOW()
                                WHERE id = %s
                            """, (new_shop, new_total, datetime.combine(new_date, datetime.min.time()), psycopg2.extras.Json(new_items), exp['id']))
                            db.commit()
                            
                            # --- AGENT 09: Pantry Integration ---
                            try:
                                from modules.pantry.core.services.pantry_service import PantryService
                                pantry = PantryService()
                                pantry.process_receipt({
                                    "shop_name": new_shop,
                                    "total_amount": new_total,
                                    "date": new_date.strftime("%Y-%m-%d"),
                                    "items": new_items,
                                    "source_file": exp.get('source_file', 'dashboard_hitl')
                                })
                                st.success("Pantry successfully updated!")
                            except Exception as pe:
                                st.warning(f"Pantry update warning: {pe}")
                            # ------------------------------------

                            st.success(f"Approved expense {exp['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Approval failed: {e}")
                    
                    if st.button("🗑️ Delete", key=f"delete_{exp['id']}"):
                        try:
                            delete_cursor = db.cursor()
                            delete_cursor.execute("DELETE FROM expenses WHERE id = %s", (exp['id'],))
                            db.commit()
                            st.warning(f"Deleted expense {exp['id']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Deletion failed: {e}")

    except Exception as e:
        st.error(f"Failed to load HITL interface: {e}")


# === TAB 5: Pantry ===
with tab5:
    st.header("Home Pantry Status")
    
    try:
        from modules.pantry.core.services.pantry_service import PantryService
        pantry = PantryService()
        pantry_data = pantry.repo.get_pantry_state()
        
        if not pantry_data:
            st.info("Pantry is empty. Approve some receipts to fill it!")
        else:
            # Stats row
            c1, c2, c3 = st.columns(3)
            in_stock = sum(1 for i in pantry_data if i['stan'] > 0)
            low_stock = sum(1 for i in pantry_data if 0 < i['stan'] < i['minimum_ilosc'])
            out_of_stock = sum(1 for i in pantry_data if i['stan'] <= 0)
            
            c1.metric("Items In Stock", in_stock)
            c2.metric("Low Stock Alerts", low_stock, delta=f"{low_stock} items", delta_color="inverse")
            c3.metric("Out of Stock", out_of_stock, delta=f"{out_of_stock} items", delta_color="inverse")
            
            # DataFrame for display
            df_pantry = pd.DataFrame(pantry_data)
            df_pantry = df_pantry[['kategoria', 'nazwa', 'stan', 'minimum_ilosc', 'jednostka_miary']]
            
            # Display sorted by category
            st.dataframe(
                df_pantry.sort_values(['kategoria', 'nazwa']),
                use_container_width=True,
                hide_index=True
            )
            
            if st.button("🔄 Force Refresh Obsidian Views"):
                pantry.refresh_views()
                st.toast("Obsidian views updated!", icon="✅")

    except Exception as e:
        st.error(f"Failed to load Pantry data: {e}")
        st.info("Make sure Agent 09 modules are correctly implemented.")
