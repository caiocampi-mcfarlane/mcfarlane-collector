# --------------------------------------------------------------
# McFARLANE DC MULTIVERSE COLLECTOR – GOTHAM EDITION (PRETTY)
# --------------------------------------------------------------
import streamlit as st
import pandas as pd
import os, uuid, base64
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------- CONFIG --------------------------
DB_FILE = "test-heroes.xlsx"
IMG_FOLDER = "collector_images"
os.makedirs(IMG_FOLDER, exist_ok=True)

# -------------------------- DARK THEME --------------------------
st.set_page_config(
    page_title="McFarlane DC Collector",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS – GOTHAM STYLE
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background-color: #0e1117;
    }
    .css-1d391kg {
        background-color: #1a1c23;
    }
    .stSidebar {
        background-color: #1a1c23;
    }
    h1, h2, h3 {
        color: #ff6b6b !important;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 0 0 10px #ff6b6b;
    }
    .stButton>button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
    }
    .stTextInput>div>input {
        background-color: #2a2d36;
        color: #fafafa;
        border: 1px solid #ff6b6b;
        border-radius: 8px;
    }
    .stSelectbox>div>div {
        background-color: #2a2d36;
        color: #fafafa;
    }
    .stDataFrame {
        border: 1px solid #ff6b6b;
        border-radius: 10px;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- HEADER --------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://i.imgur.com/8z3iQ2T.png", width=120)  # Batman Logo
st.markdown("<h1 style='text-align: center;'>McFARLANE DC MULTIVERSE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Your Collection. Your Legacy.</p>", unsafe_allow_html=True)

# -------------------------- DATA --------------------------
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE, dtype=str).fillna("")
    else:
        st.warning("No test-heroes.xlsx found! Place it in the same folder.")
        return pd.DataFrame()

def save_data(df):
    df.to_excel(DB_FILE, index=False)

def add_image(fig_id, uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    path = f"{IMG_FOLDER}/{fig_id}_{uuid.uuid4().hex[:6]}.{ext}"
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def delete_images(fig_id):
    for f in os.listdir(IMG_FOLDER):
        if f.startswith(fig_id + "_"):
            os.remove(os.path.join(IMG_FOLDER, f))

df = load_data()
if not df.empty:
    df["#"] = df["#"].astype(str)

# -------------------------- SIDEBAR --------------------------
st.sidebar.image("https://i.imgur.com/8z3iQ2T.png", width=80)
st.sidebar.markdown("### 🦸‍♂️ **COLLECTOR HQ**")
page = st.sidebar.radio("Navigate", [
    "🔍 Browse & Search",
    "➕ Add New Figure",
    "📊 Reports",
    "🖼️ Photo Gallery"
])

# ==============================================================
# 1. BROWSE & SEARCH
# ==============================================================
if page == "🔍 Browse & Search":
    if df.empty:
        st.info("Upload your Excel file to begin.")
    else:
        st.markdown("### 🔎 **Search Your Collection**")
        col1, col2 = st.columns(2)
        with col1:
            year = st.multiselect("Year", ["All"] + sorted(df["Year"].unique().tolist()))
            series = st.multiselect("Series", ["All"] + sorted(df["Series"].unique().tolist()))
        with col2:
            wave = st.multiselect("Wave", ["All"] + sorted(df["Wave"].unique().tolist()))
            search = st.text_input("Quick Search (Name, UPC, etc.)")

        mask = pd.Series([True] * len(df))
        if year and "All" not in year: mask &= df["Year"].isin(year)
        if series and "All" not in series: mask &= df["Series"].isin(series)
        if wave and "All" not in wave: mask &= df["Wave"].isin(wave)
        if search:
            mask &= df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)

        view = df[mask].copy()
        st.dataframe(view, use_container_width=True)

        if not view.empty:
            st.markdown("### ✏️ **Edit Figure**")
            selected_id = st.selectbox("Select #", view["#"])
            row = df[df["#"] == selected_id].iloc[0]

            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    year = st.text_input("Year", row["Year"])
                    series = st.text_input("Series", row["Series"])
                    wave = st.text_input("Wave", row["Wave"])
                    name = st.text_input("Figure Name", row["Figure Name"])
                with c2:
                    variant = st.text_input("Variant", row["Variant"])
                    msrp = st.text_input("MSRP", row["MSRP"])
                    upc = st.text_input("UPC-BARCODE", row["UPC-BARCODE"])
                    pc = st.text_input("PC AMOUNT", row["PC AMOUNT"])

                if st.form_submit_button("💾 Save Changes"):
                    df.loc[df["#"] == selected_id] = [selected_id, year, series, wave, name, variant, msrp, upc, row["SERIAL"], pc]
                    save_data(df)
                    st.success("Figure updated!")
                    st.balloons()
                    st.rerun()

            col_del, col_img = st.columns([1, 3])
            with col_del:
                if st.button("🗑️ Delete Figure"):
                    df = df[df["#"] != selected_id]
                    delete_images(selected_id)
                    save_data(df)
                    st.success("Deleted!")
                    st.rerun()
            with col_img:
                st.markdown("**Photos**")
                imgs = [f for f in os.listdir(IMG_FOLDER) if f.startswith(selected_id + "_")]
                for img in imgs:
                    st.image(f"{IMG_FOLDER}/{img}", width=180)

# ==============================================================
# 2. ADD NEW FIGURE
# ==============================================================
elif page == "➕ Add New Figure":
    st.markdown("### ➕ **Add to Your Collection**")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            year = st.text_input("Year *", placeholder="2025")
            series = st.text_input("Series *", placeholder="DC Multiverse")
            name = st.text_input("Figure Name *", placeholder="Batman")
        with c2:
            wave = st.text_input("Wave")
            variant = st.text_input("Variant")
            msrp = st.text_input("MSRP", placeholder="19.99")

        upc = st.text_input("UPC-BARCODE")
        pc = st.text_input("PC AMOUNT")
        photos = st.file_uploader("Upload Photos", accept_multiple_files=True, type=["png","jpg","jpeg"])

        if st.form_submit_button("➕ Add Figure"):
            if not (year and series and name):
                st.error("Year, Series, and Name required.")
            else:
                new_id = str(int(df["#"].max()) + 1) if not df.empty else "1"
                new_row = pd.DataFrame([{
                    "#": new_id, "Year": year, "Series": series, "Wave": wave,
                    "Figure Name": name, "Variant": variant, "MSRP": msrp,
                    "UPC-BARCODE": upc, "SERIAL": "", "PC AMOUNT": pc
                }])
                df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
                save_data(df)
                for ph in photos:
                    add_image(new_id, ph)
                st.success(f"Added #{new_id} – {name}")
                st.balloons()
                st.rerun()

# ==============================================================
# 3. REPORTS
# ==============================================================
elif page == "📊 Reports":
    st.markdown("### 📊 **Collector Reports**")
    rep = st.selectbox("Choose", [
        "Full Catalog (PDF)",
        "Price Trend Chart",
        "Missing UPC List"
    ])

    if rep == "Full Catalog (PDF)" and st.button("Generate PDF"):
        with st.spinner("Building PDF..."):
            doc = SimpleDocTemplate("catalog.pdf", pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph("McFarlane DC Multiverse – Full Catalog", styles['Title']))
            elements.append(Spacer(1, 0.2*inch))
            data = [df.columns.tolist()] + df.values.tolist()
            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkred),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ]))
            elements.append(t)
            doc.build(elements)
            with open("catalog.pdf", "rb") as f:
                st.download_button("⬇️ Download Catalog", f, "McFarlane_Catalog.pdf")

    elif rep == "Price Trend Chart":
        chart = df.copy()
        chart["MSRP"] = pd.to_numeric(chart["MSRP"], errors="coerce")
        chart = chart.groupby("Year")["MSRP"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(chart["Year"], chart["MSRP"], marker='o', color='#ff6b6b', linewidth=3)
        ax.set_facecolor('#1a1c23')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white')
        ax.set_title("Average MSRP by Year", color='white', fontsize=16)
        st.pyplot(fig)

    elif rep == "Missing UPC List":
        missing = df[df["UPC-BARCODE"] == ""][["#","Figure Name"]]
        csv = missing.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, "missing_upc.csv")

# ==============================================================
# 4. PHOTO GALLERY
# ==============================================================
elif page == "🖼️ Photo Gallery":
    st.markdown("### 🖼️ **Your Collection in Photos**")
    imgs = [f for f in os.listdir(IMG_FOLDER) if os.path.isfile(os.path.join(IMG_FOLDER, f))]
    if imgs:
        cols = st.columns(4)
        for i, img in enumerate(imgs):
            with cols[i % 4]:
                st.image(f"{IMG_FOLDER}/{img}", use_column_width=True)
                fig_id = img.split("_")[0]
                name = df[df["#"] == fig_id]["Figure Name"].iloc[0] if fig_id in df["#"].values else "Unknown"
                st.caption(f"**#{fig_id}** – {name}")
    else:
        st.info("No photos yet. Start adding!")

# -------------------------- FOOTER --------------------------
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🦇 McFarlane DC Collector • Total Figures: <strong>{}</strong> • Last Updated: {}</p>
</div>
""".format(len(df), datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)