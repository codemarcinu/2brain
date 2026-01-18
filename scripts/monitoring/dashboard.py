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
tab1, tab2, tab3 = st.tabs(["📈 Overview", "📋 Queues", "💰 Expenses"])


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
            category,
            SUM(total_amount) as total
        FROM expenses
        WHERE purchase_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(purchase_date), category
        ORDER BY date DESC
        """
        
        df = pd.read_sql(query, db)
        
        if not df.empty:
            # Line chart
            fig = px.line(df, x='date', y='total', color='category', title="Expenses Last 30 Days")
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary by category
            summary = df.groupby('category')['total'].sum().reset_index()
            summary.columns = ['Category', 'Total (PLN)']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("By Category")
                st.dataframe(summary, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("Distribution")
                fig_pie = px.pie(summary, names='Category', values='Total (PLN)')
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses in last 30 days")
            
    except Exception as e:
        st.error(f"Failed to load expenses: {e}")
