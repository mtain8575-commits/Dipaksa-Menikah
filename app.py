import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

excel_file = 'Database_Jadwal_Produksi.xlsx'

@st.cache_data
def load_schedule_data(sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=3)
    return df

# Pilihan hari syuting
hari_pilihan = st.selectbox("Pilih Hari Syuting", ["Day 1", "Day 2", "Day 3"])

try:
    df_hari = load_schedule_data(hari_pilihan)
    df_hari = df_hari.dropna(how='all')
    
    # Ambil baris yang benar-benar merupakan scene (bukan baris kategori kosong)
    df_scenes = df_hari[df_hari['Scene'].notna() & (df_hari['Scene'] != '')].copy()
    total_scenes = len(df_scenes)
    
    # Inisialisasi session state untuk menyimpan status checklist per hari
    state_key = f'status_{hari_pilihan}'
    if state_key not in st.session_state:
        st.session_state[state_key] = {idx: False for idx in df_scenes.index}
        
    # Hitung jumlah yang sudah dichecklist (sudah take) vs sisa
    completed_count = sum(st.session_state[state_key].values())
    remaining_count = total_scenes - completed_count
    
    # 📊 TAMPILAN REKAP / METRICS PROGRESS
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Scene Harian", total_scenes)
    col_m2.metric("Sudah Take (Selesai)", completed_count)
    col_m3.metric("Sisa Belum Take", remaining_count)
    
    st.markdown("---")
    st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")
    
    current_category = ""
    
    # Iterasi baris untuk menampilkan heading kategori set dan tabel adegan
    for idx, row in df_hari.iterrows():
        scene_val = row.get("Scene", None)
        
        # Cek baris Kategori Set / Heading Lokasi
        if pd.isna(scene_val) or str(scene_val).strip() == "":
            cat_text = str(row.get("No", ""))
            if "SET CATEGORY" in cat_text.upper():
                current_category = cat_text
                st.markdown(f"#### 📍 {current_category}")
            continue
            
        # Baris Scene Normal dengan Checklist Interaktif
        col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.5, 1, 1, 1, 3, 2, 3])
        
        with col_chk:
            current_val = st.session_state[state_key].get(idx, False)
            is_checked = st.checkbox("", value=current_val, key=f"chk_{hari_pilihan}_{idx}")
            st.session_state[state_key][idx] = is_checked
            
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
    st.error(f"Terjadi kesalahan saat memuat data: {e}")