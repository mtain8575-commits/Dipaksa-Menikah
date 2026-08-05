import streamlit as st
import pandas as pd

# Asumsi df_hari adalah dataframe rincian jadwal untuk hari yang sedang dipilih (Misal: Day 1)
# Kolom dataframe: Status, Scene, N/D, Page(s), Set Lokasi, Cast, Remark

st.markdown("### 📋 Rincian Jadwal Syuting & Checklist")
st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")

# Ambil daftar unik Set Lokasi sesuai urutan di data
unique_sets = df_hari['Set Lokasi'].unique()

# Loop untuk setiap Set Lokasi sebagai Heading
for set_lokasi in unique_sets:
    # 📌 Membuat Heading Sub-Pengelompokan Set Lokasi
    st.markdown(f"#### 📍 SET LOKASI: {set_lokasi}")
    
    # Filter dataframe khusus untuk set lokasi tersebut
    df_set_group = df_hari[df_hari['Set Lokasi'] == set_lokasi]
    
    # Tampilkan tabel/baris untuk scene-scene dalam set tersebut
    # Anda bisa menggunakan st.dataframe atau custom loop dengan checkbox
    for idx, row in df_set_group.iterrows():
        col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.6, 1, 1, 1, 3, 2, 3])
        
        with col_chk:
            # Checkbox status selesai/belum
            status_val = st.checkbox("", value=bool(row.get("Status", False)), key=f"chk_{idx}")
        with col_scene:
            st.text(str(row.get("Scene", "")))
        with col_nd:
            st.text(str(row.get("N/D", "")))
        with col_page:
            st.text(str(row.get("Page(s)", "")))
        with col_set:
            st.text(str(row.get("Set Lokasi", "")))
        with col_cast:
            st.text(str(row.get("Cast", "")))
        with col_remark:
            st.text(str(row.get("Remark", "")))
            
    # Garis pemisah antar set lokasi
    st.markdown("---")