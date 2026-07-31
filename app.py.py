import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set Page Config
st.set_page_config(
    page_title="Dashboard Produksi Film - Dipaksa Menikah",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for Professional Dark/Clean Film Production Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to parse page fractions (e.g., '1 2/8', '4/8', '1', '1 1/2') into float
def parse_pages(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    total = 0.0
    parts = val_str.split()
    for p in parts:
        if '/' in p:
            try:
                num, den = p.split('/')
                total += float(num) / float(den)
            except:
                pass
        else:
            try:
                total += float(p)
            except:
                pass
    return total

# Load Data Function
@st.cache_data
def load_data():
    # Membaca file master schedule atau breakdown produksi
    # Sesuaikan nama file excel Anda di sini
    file_name = 'Master_Schedule_Dipaksa_Menikah.xlsx'
    try:
        df = pd.read_excel(file_name, sheet_name='Master Schedule DPM')
    except:
        # Fallback jika sheet berbeda
        xls = pd.ExcelFile(file_name)
        df = pd.read_excel(file_name, sheet_name=xls.sheet_names[0])
    
    # Membersihkan baris header atau section yang tidak diperlukan
    if 'PLAN SCHEDULE' in str(df.iloc[0, 0]) or 'No' in str(df.iloc[1, 0]):
        df.columns = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)
    
    # Menghapus baris section header (misal baris yang bertuliskan nama set kategori)
    if 'No' in df.columns:
        df = df[df['No'].notna() & (df['No'] != 'SECTION')].reset_index(drop=True)
    
    # Standardisasi nama kolom sesuai permintaan user
    # Kolom yang diharapkan: Scene, INT/EXT, Lokasi, DAY/NIGHT, Karakter, Properti Utama, Estimasi Durasi (Page(s))
    column_mapping = {}
    for col in df.columns:
        col_str = str(col).strip().upper()
        if 'SCENE' in col_str:
            column_mapping[col] = 'Scene'
        elif 'I/E' in col_str or 'INT' in col_str:
            column_mapping[col] = 'INT/EXT'
        elif 'LOKASI' in col_str or 'SET' in col_str:
            column_mapping[col] = 'Lokasi'
        elif 'N/D' in col_str or 'DAY' in col_str or 'NIGHT' in col_str:
            column_mapping[col] = 'DAY/NIGHT'
        elif 'CAST' in col_str or 'KARAKTER' in col_str:
            column_mapping[col] = 'Karakter'
        elif 'PROP' in col_str:
            column_mapping[col] = 'Properti Utama'
        elif 'PAGE' in col_str or 'DURASI' in col_str:
            column_mapping[col] = 'Estimasi Durasi'
            
    df = df.rename(columns=column_mapping)
    
    # Pastikan kolom wajib ada
    required_cols = ['Scene', 'INT/EXT', 'Lokasi', 'DAY/NIGHT', 'Karakter', 'Properti Utama', 'Estimasi Durasi']
    for rc in required_cols:
        if rc not in df.columns:
            df[rc] = 'N/A'
            
    # Parsing durasi halaman ke float
    df['Durasi_Float'] = df['Estimasi Durasi'].apply(parse_pages)
    
    # Standardisasi INT/EXT dan DAY/NIGHT
    df['INT/EXT'] = df['INT/EXT'].astype(str).str.upper().str.strip()
    df['DAY/NIGHT'] = df['DAY/NIGHT'].astype(str).str.upper().str.strip()
    
    return df

# Load Data
df = load_data()

# --- SIDEBAR: FILTER INTERAKTIF ---
st.sidebar.header("🎬 Filter Produksi")

# Filter Lokasi
all_lokasi = sorted(df['Lokasi'].dropna().unique().tolist())
selected_lokasi = st.sidebar.multiselect("Pilih Lokasi / Set:", options=all_lokasi, default=[])

# Filter Karakter
# Ekstrak semua nama karakter unik (karena dalam 1 baris bisa ada beberapa karakter dipisah koma)
all_chars_raw = df['Karakter'].dropna().astype(str).str.split(',').tolist()
all_chars = sorted(list(set([c.strip() for sublist in all_chars_raw for c in sublist if c.strip() and c.strip().upper() != 'TIDAK ADA'])))
selected_karakter = st.sidebar.multiselect("Pilih Karakter / Cast:", options=all_chars, default=[])

# Apply Filter to DataFrame
filtered_df = df.copy()
if selected_lokasi:
    filtered_df = filtered_df[filtered_df['Lokasi'].isin(selected_lokasi)]
if selected_karakter:
    # Filter baris yang mengandung karakter terpilih
    filtered_df = filtered_df[filtered_df['Karakter'].apply(lambda x: any(char in str(x) for char in selected_karakter))]

# --- MAIN DASHBOARD HEADER ---
st.title("📊 Production Dashboard & Script Breakdown")
st.markdown("Analisis durasi, sebaran lokasi, dan rasio scene harian/interior untuk persiapan *Master Schedule* produksi film.")

# --- METRIC 1: TOTAL DURASI KESELURUHAN ---
total_pages = filtered_df['Durasi_Float'].sum()
total_scenes = len(filtered_df)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Durasi Keseluruhan", value=f"{total_pages:.2f} Halaman", delta=f"{total_scenes} Scene")
with col2:
    st.metric(label="Jumlah Lokasi Aktif", value=f"{filtered_df['Lokasi'].nunique()} Lokasi")
with col3:
    st.metric(label="Total Karakter Terlibat", value=f"{len(all_chars)} Pemeran")

st.markdown("---")

# --- VISUALIZATION 2 & 3: CHARTS ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📍 Total Scene berdasarkan Lokasi")
    if not filtered_df.empty:
        loc_counts = filtered_df['Lokasi'].value_counts().reset_index()
        loc_counts.columns = ['Lokasi', 'Jumlah Scene']
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=loc_counts.head(10), x='Jumlah Scene', y='Lokasi', palette='Blues_r', ax=ax)
        ax.set_title("Top 10 Lokasi Paling Sering Digunakan", fontsize=12, fontweight='bold', color='white')
        ax.set_xlabel("Jumlah Scene", color='white')
        ax.set_ylabel("Lokasi", color='white')
        ax.tick_params(colors='white')
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#1f2937')
        st.pyplot(fig)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

with col_chart2:
    st.subheader("⚖️ Perbandingan INT vs EXT & DAY vs NIGHT")
    if not filtered_df.empty:
        # Group sebaran INT/EXT dan DAY/NIGHT
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        
        ie_counts = filtered_df['INT/EXT'].value_counts()
        ax1.pie(ie_counts, labels=ie_counts.index, autopct='%1.1f%%', colors=['#3b82f6', '#10b981', '#f59e0b'], startangle=90, textprops={'color':'white'})
        ax1.set_title("Rasio INT vs EXT", fontsize=11, fontweight='bold', color='white')
        
        dn_counts = filtered_df['DAY/NIGHT'].value_counts()
        ax2.pie(dn_counts, labels=dn_counts.index, autopct='%1.1f%%', colors=['#8b5cf6', '#ec4899', '#6366f1'], startangle=90, textprops={'color':'white'})
        ax2.set_title("Rasio DAY vs NIGHT", fontsize=11, fontweight='bold', color='white')
        
        fig.patch.set_facecolor('#0e1117')
        st.pyplot(fig)
    else:
        st.info("Tidak ada data untuk filter yang dipilih.")

st.markdown("---")

# --- DATA TABLE PREVIEW ---
st.subheader("📋 Tabel Detail Breakdown Skenario")
st.dataframe(filtered_df[['Scene', 'INT/EXT', 'Lokasi', 'DAY/NIGHT', 'Karakter', 'Properti Utama', 'Estimasi Durasi']], use_container_width=True)