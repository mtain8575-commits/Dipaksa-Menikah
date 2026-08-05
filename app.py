import streamlit as st
import pandas as pd

st.markdown("### 📋 Rincian Jadwal Syuting & Checklist")
st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")

# Pastikan variabel dataframe Anda bernama 'df' atau sesuaikan dengan kode asli Anda
if 'Set Lokasi' in df.columns:
    unique_sets = df['Set Lokasi'].unique()
    
    for set_lokasi in unique_sets:
        st.markdown(f"#### 📍 SET LOKASI: {set_lokasi}")
        df_set_group = df[df['Set Lokasi'] == set_lokasi]
        
        for idx, row in df_set_group.iterrows():
            col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.6, 1, 1, 1, 3, 2, 3])
            
            with col_chk:
                st.checkbox("", value=bool(row.get("Status", False)), key=f"chk_{idx}")
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
                
        st.markdown("---")
else:
    st.error("Kolom 'Set Lokasi' tidak ditemukan di dalam dataframe.")
