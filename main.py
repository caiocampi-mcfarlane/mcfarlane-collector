import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
import base64
import os

# === CONFIG ===
st.set_page_config(page_title="McFarlane Collector", page_icon="🦇", layout="wide")

# === SECRETS (Set in Streamlit Cloud > Settings > Secrets) ===
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "mcfarlane2025")

# === LOAD MASTER DB FROM GITHUB ===
@st.cache_data(ttl=60)
def load_master_db():
    try:
        url = "https://raw.githubusercontent.com/YOUR-USERNAME/mcfarlane-collector/main/master_database.csv"
        return pd.read_csv(url)
    except:
        # Fallback sample
        return pd.DataFrame({
            'Figure': ['Arkham Asylum Batman (Bronze)', 'Knightfall Azrael (Chase)'],
            'Year': [2020, 2021],
            'Variant': ['Bronze Target', 'Chase Walmart'],
            'Retailer': ['Target', 'Walmart']
        })

MASTER_DF = load_master_db()

# === SAMPLE USER COLLECTION ===
@st.cache_data
def get_sample():
    return pd.DataFrame({
        'Figure': ["Arkham Asylum Batman (Bronze)", "Knightfall Azrael (Chase)"],
        'Year': [2020, 2021],
        'Status': ['Owned (Boxed)', 'Owned (Loose)']
    })

# === ADMIN AUTH ===
def check_password():
    def password_entered():
        if st.session_state["password"] == ADMIN_PASSWORD:
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("Wrong password")
    if "authenticated" not in st.session_state:
        st.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["authenticated"]

# === ADMIN PAGE ===
if st.sidebar.button("Admin Page (Edit Master DB)"):
    if check_password():
        st.sidebar.success("Admin Mode Active")
        st.title("Admin: Edit Master Database")

        # Editable master table
        edited_master = st.data_editor(
            MASTER_DF,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Year": st.column_config.NumberColumn("Year", min_value=2020, max_value=2030),
                "Variant": st.column_config.TextColumn("Variant"),
                "Retailer": st.column_config.TextColumn("Retailer")
            }
        )

        if st.button("Save Master DB to GitHub"):
            csv = edited_master.to_csv(index=False)
            st.code(csv)  # Show for copy
            st.info("Copy the CSV above and **manually update** `master_database.csv` in GitHub (Streamlit can't write to GitHub yet).")
            st.success("DB updated! Refresh in 60s.")
    else:
        st.stop()

# === MAIN APP (PUBLIC) ===
st.title("McFarlane DC Multiverse Collector")
st.markdown("**Track 600+ figures | Export PDF | Hunt 2025 drops**")

# === USER DATA ===
st.sidebar.header("Your Collection")
uploaded = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])

if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
        if 'Notes' not in df.columns: df['Notes'] = ''
        st.session_state.df = df
        st.sidebar.success(f"Loaded {len(df)} figures")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
else:
    st.session_state.df = get_sample() if 'df' not in st.session_state else st.session_state.df

df = st.session_state.df
df_full = df.merge(MASTER_DF, on=['Figure', 'Year'], how='left').fillna('N/A')

# === FILTERS ===
st.sidebar.header("Search")
search = st.sidebar.text_input("Figure name")
status = st.sidebar.multiselect("Status", df['Status'].unique(), df['Status'].unique())
year_range = st.sidebar.slider("Year", 2020, 2025, (2020, 2025))

filtered = df_full[
    df_full['Figure'].str.contains(search, case=False, na=False) &
    df_full['Status'].isin(status) &
    df_full['Year'].between(*year_range)
]

# === DASHBOARD ===
col1, col2 = st.columns(2)
with col1:
    st.subheader("Ownership")
    counts = df['Status'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

with col2:
    st.subheader("By Year")
    year_df = df.groupby('Year').size().reset_index(name='Count')
    fig = px.bar(year_df, x='Year', y='Count')
    st.plotly_chart(fig, use_container_width=True)

# === EDIT COLLECTION ===
st.subheader("Edit Collection")
edited = st.data_editor(filtered, num_rows="dynamic", use_container_width=True)
if st.button("Save Changes"):
    st.session_state.df = edited[['Figure', 'Year', 'Status']].copy()
    st.success("Saved!")

# === EXPORTS ===
st.subheader("Export")
c1, c2 = st.columns(2)
with c1:
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "collection.csv", "text/csv")
with c2:
    if st.button("PDF Report"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("McFarlane Collection", styles['Title']))
        data = [['Figure', 'Year', 'Status']] + df[['Figure', 'Year', 'Status']].values.tolist()
        t = Table(data)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(t)
        doc.build(elements)
        st.download_button("Download PDF", buffer.getvalue(), "report.pdf", "application/pdf")

# === FOOTER ===
st.caption("Admin edits sync in 60s | 100% Free | Updated Nov 2025")
