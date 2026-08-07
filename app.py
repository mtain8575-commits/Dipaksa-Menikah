import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman Streamlit agar lebar (wide mode)
st.set_page_config(page_title="Dashboard Monitoring Produksi", layout="wide")

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

excel_file = 'Database_Jadwal_Produksi.xlsx'

@st.cache_data
def load_schedule_data(sheet_name):
    st.cache_data.clear()
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
        
        if pd.isna(scene_val) or str(scene_val).strip() == "":
            if "SET CATEGORY" in no_val.upper():
                current_category = no_val
            categories_list.append(None)
        else:
            categories_list.append(current_category)
            
    df_hari['Active_Category'] = categories_list
    df_scenes = df_hari[df_hari['Scene'].notna() & (df_hari['Scene'] != '')].copy()
    total_scenes = len(df_scenes)
    
    # Inisialisasi session state untuk checklist status per menu
    state_key = f'status_{pilihan_menu}'
    if state_key not in st.session_state:
        st.session_state[state_key] = {idx: False for idx in df_scenes.index}
    
    # Pastikan semua indeks scene ada di session state
    for idx in df_scenes.index:
        if idx not in st.session_state[state_key]:
            st.session_state[state_key][idx] = False
            
    st.markdown("---")

    # ==========================================
    # 🖨️ PANEL CETAK / CALL SHEET FORMAT A4
    # ==========================================
    with st.expander("🖨️ Buka Panel Cetak (Format Call Sheet A4 Landscape)", expanded=False):
        loc_mapping = {
            "Day 1": "MAHARAJA DEPOK",
            "Day 2": "RUMAH SAKIT VIP / LORONG",
            "Day 3": "RUMAH INTAN & MASJID",
            "Master Schedule" : "ALL LOCATIONS"
        }
        lokasi_terkini = loc_mapping.get(pilihan_menu, "JAKARTA & SEKITARNYA")
        tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")

        st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>SCHEDULE SERIES</h3>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: red; margin-top: 0px;'>\"DIPAKSA MENIKAH\"</h2>", unsafe_allow_html=True)
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"""
            * **PRODUCTION** : MD Entertainment
            * **DIRECTOR** : ANTO AGAM
            * **DOP** : FENDI
            * **ART DIRECTOR** : RIZAL
            * **PIMPRO** : LENA
            """)
        with col_info2:
            st.markdown(f"""
            * **SHOOTING** : **{pilihan_menu.upper()}**
            * **DATE** : {tanggal_hari_ini}
            * **CREW CALL** : 06.00 WIB
            * **LOCATION** : {lokasi_terkini}
            * **ON CAM** : 08.00 WIB
            """)
            
        st.markdown("---")
        st.markdown("#### Tabel Rincian Adegan (Call Sheet)")
        
        df_print = df_scenes[['No', 'Scene', 'I/E', 'SET', 'PROPERTY', 'CAST', 'REMARK']].copy()
        df_print.columns = ['NO', 'SCENE', 'I/E', 'SET', 'PROPERTY', 'CAST', 'REMARK']
        st.dataframe(df_print, use_container_width=True, hide_index=True)
        st.info("💡 Tip: Tekan `Ctrl + P` pada keyboard Anda untuk mencetak halaman ini dalam ukuran A4 Landscape.")

    st.markdown("---")
    st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")
    
    unique_categories = df_scenes['Active_Category'].dropna().unique()
    
    # Render daftar kategori dan checklist adegan secara interaktif
    for cat in unique_categories:
        st.markdown(f"#### 📍 {cat}")
        df_cat_scenes = df_scenes[df_scenes['Active_Category'] == cat]
        
        for idx, row in df_cat_scenes.iterrows():
            col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.5, 1, 1, 1, 3, 2, 3])
            
            with col_chk:
                current_val = st.session_state[state_key].get(idx, False)
                # Menggunakan on_change agar langsung merespon saat diklik
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

    # Hitung jumlah yang sudah dichecklist secara real-time dari session state
    completed_count = sum(1 for idx in df_scenes.index if st.session_state[state_key].get(idx, False))
    remaining_count = total_scenes - completed_count

    # Tampilkan Metrics / Rekap di bagian paling bawah atau kita tempatkan di atas via placeholder
    # Agar metrik berada di atas, kita buat ulang di awal atau gunakan container.
    # Mari kita tempatkan rekap di bagian bawah agar angkuhnya selalu sinkron sempurna dengan checkbox.

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")