import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Dashboard Produksi - Dipaksa Menikah",
    page_icon="🎬",
    layout="wide"
)

# Judul Utama Dashboard
st.title("🎬 Dashboard Produksi: Dipaksa Menikah")
st.markdown("---")
st.markdown("Dashboard interaktif untuk memonitor breakdown skenario, jadwal, dan kebutuhan kru produksi.")

# Load Data Excel
@st.cache_data
def load_data():
    file_name = "Master_Schedule_Dipaksa_Menikah.xlsx"
    try:
        df = pd.read_excel(file_name)
        return df
    except Exception as e:
        st.error(f"Gagal memuat file Excel: {e}")
        return None

df = load_data()

if df is not None:
    # Sidebar untuk Filter
    st.sidebar.header("🔍 Filter Data Produksi")
    
    # Filter berdasarkan kolom jika tersedia (misal: Lokasi/Status/Kategori)
    columns = df.columns.tolist()
    
    # Menampilkan ringkasan metrik utama di bagian atas
    st.subheader("📊 Ringkasan Statistik")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Baris Data / Scene", value=len(df))
    with col2:
        if len(columns) > 0:
            st.metric(label="Kolom Utama", value=columns[0])
    with col3:
        st.metric(label="Status Server", value="Online 🚀")
        
    st.markdown("---")
    
    # Tabel Data Utama dengan fitur pencarian interaktif
    st.subheader("📋 Tabel Master Schedule & Breakdown")
    search_query = st.text_input("Cari data (ketik kata kunci scene, karakter, atau lokasi):", "")
    
    if search_query:
        # Filter dataframe berdasarkan pencarian teks
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]
    else:
        filtered_df = df
        
    st.dataframe(filtered_df, use_container_width=True)
    
    # Unduh Data
    st.markdown("---")
    st.subheader("📥 Unduh Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data sebagai CSV",
        data=csv,
        file_name='breakdown_dipaksa_menikah.csv',
        mime='text/csv',
    )
else:
    st.warning("⚠️ File Excel `Master_Schedule_Dipaksa_Menikah.xlsx` belum terbaca atau belum berada di folder yang sama dengan `app.py`.")