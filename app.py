import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.markdown("### 📋 Rincian Jadwal Syuting & Checklist")
st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")

excel_file = 'Database_Jadwal_Produksi.xlsx'

@st.cache_data
def load_schedule_data(sheet_name):
    # Membaca excel dengan header di baris ke-4 (indeks 3)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=3)
    return df

# Pilihan hari syuting di sidebar atau tabs (sesuaikan dengan kontrol Anda)
# Contoh jika menggunakan selectbox hari:
hari_pilihan = st.selectbox("Pilih Hari Syuting", ["Day 1", "Day 2", "Day 3"])

try:
    df_hari = load_schedule_data(hari_pilihan)
    
    # Bersihkan baris yang kosong total
    df_hari = df_hari.dropna(how='all')
    
    current_category = ""
    
    # Iterasi baris untuk mendeteksi kategori set dan menampilkan tabel per kelompok
    for idx, row in df_hari.iterrows():
        scene_val = row.get("Scene", None)
        
        # Cek apakah baris ini adalah baris Kategori Set (Scene bernilai NaN / kosong)
        if pd.isna(scene_val) or str(scene_val).strip() == "":
            cat_text = str(row.get("No", ""))
            if "SET CATEGORY" in cat_text.upper():
                current_category = cat_text
                st.markdown(f"#### 📍 {current_category}")
            continue
            
        # Jika baris data adegan normal
        col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.5, 1, 1, 1, 3, 2, 3])
        
        with col_chk:
            st.checkbox("", value=False, key=f"chk_{hari_pilihan}_{idx}")
        with col_scene:
            st.text(str(row.get("Scene", "")))
        with col_nd:
            st.text(str(row.get("N/D", "")))
        with col_page:
            st.text(str(row.get("Page(s)", "")))
        with col_set:
            st.text(str(row.get("SET", "")))
        with col_cast:
            st.text(str(row.get("CAST", "")))
        with col_remark:
            st.text(str(row.get("REMARK", "")))
            
    st.markdown("---")

except Exception as e:
    st.error(fTerjadi kesalahan saat memuat data: {e}")