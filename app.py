import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

excel_file = 'Database_Jadwal_Produksi.xlsx'

@st.cache_data
def load_schedule_data(sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=3)
    return df

# Dropdown pilihan hari syuting atau master schedule
pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule", 
    ["Day 1", "Day 2", "Day 3", "Master Schedule"]
)

try:
    df_hari = load_schedule_data(pilihan_menu)
    df_hari = df_hari.dropna(how='all')
    
    # Berikan label kategori yang persisten ke setiap baris adegan
    current_category = "LAINNYA"
    categories_list = []
    
    for idx, row in df_hari.iterrows():
        scene_val = row.get("Scene", None)
        no_val = str(row.get("No", ""))
        
        # Jika baris adalah baris kategori
        if pd.isna(scene_val) or str(scene_val).strip() == "":
            if "SET CATEGORY" in no_val.upper():
                current_category = no_val
            categories_list.append(None) # Baris kategori ditandai None untuk dilewati saat render tabel
        else:
            categories_list.append(current_category)
            
    df_hari['Active_Category'] = categories_list
    
    # Ambil hanya baris adegan valid
    df_scenes = df_hari[df_hari['Scene'].notna() & (df_hari['Scene'] != '')].copy()
    total_scenes = len(df_scenes)
    
    # Inisialisasi session state untuk checklist status
    state_key = f'status_{pilihan_menu}'
    if state_key not in st.session_state:
        st.session_state[state_key] = {idx: False for idx in df_scenes.index}
        
    # Hitung jumlah rekap progress
    completed_count = sum(st.session_state[state_key].values())
    remaining_count = total_scenes - completed_count
    
    # 📊 TAMPILAN REKAP / METRICS PROGRESS
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Scene", total_scenes)
    col_m2.metric("Sudah Take (Selesai)", completed_count)
    col_m3.metric("Sisa Belum Take", remaining_count)
    
    st.markdown("---")
    st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")
    
    # Ambil daftar kategori unik yang ada di sheet ini
    unique_categories = df_scenes['Active_Category'].dropna().unique()
    
    for cat in unique_categories:
        # 📌 Heading Kategori Utama (Hanya Tampil 1 Kali per Kategori)
        st.markdown(f"#### 📍 {cat}")
        
        df_cat_scenes = df_scenes[df_scenes['Active_Category'] == cat]
        
        for idx, row in df_cat_scenes.iterrows():
            col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.5, 1, 1, 1, 3, 2, 3])
            
            with col_chk:
                current_val = st.session_state[state_key].get(idx, False)
                is_checked = st.checkbox("", value=current_val, key=f"chk_{pilihan_menu}_{idx}")
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