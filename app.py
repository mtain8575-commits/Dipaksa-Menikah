import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman Streamlit agar lebar (wide mode)
st.set_page_config(page_title="Dashboard Monitoring Produksi", layout="wide")

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

excel_file = 'Database_Jadwal_Produksi.xlsx'

def load_schedule_data(sheet_name):
    # Membaca data langsung dari file Excel
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=3)
    return df

def save_status_to_excel(sheet_name, df_full):
    # Menyimpan kembali perubahan status ke file Excel agar sinkron untuk semua perangkat
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_full.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

# Dropdown pilihan hari syuting atau master schedule
pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule", 
    ["Day 1", "Day 2", "Day 3", "Master Schedule"]
)

try:
    # Load data mentah lengkap dengan baris kategorinya
    df_raw = pd.read_excel(excel_file, sheet_name=pilihan_menu, header=None)
    
    # Load dataframe dengan header di baris ke-4 (indeks 3) untuk dibaca aplikasinya
    df_hari = load_schedule_data(pilihan_menu)
    df_hari = df_hari.dropna(how='all')
    
    # Pastikan kolom 'Status' / 'Take' ada di dataframe, jika belum buat kolomnya
    status_col_idx = None
    for idx, col_name in enumerate(df_hari.columns):
        if str(col_name).strip().upper() in ['STATUS', 'TAKE', 'CHECK']:
            status_col_idx = col_name
            break
            
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
    
    # Hitung jumlah yang sudah dichecklist berdasarkan data di Excel
    completed_count = 0
    if 'Status_Take' in df_scenes.columns:
        completed_count = int(df_scenes['Status_Take'].fillna(False).sum())
    else:
        # Buat kolom Status_Take jika belum ada di dataframe
        df_scenes['Status_Take'] = False

    remaining_count = total_scenes - completed_count
    
    # 📊 TAMPILAN REKAP / METRICS PROGRESS (Akurat & Sinkron)
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Scene", total_scenes)
    col_m2.metric("Sudah Take (Selesai)", completed_count)
    col_m3.metric("Sisa Belum Take", remaining_count)
    
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
    
    # Form untuk menangani interaksi checklist secara real-time
    with st.form(key=f"form_checklist_{pilihan_menu}"):
        checkbox_states = {}
        
        for cat in unique_categories:
            st.markdown(f"#### 📍 {cat}")
            df_cat_scenes = df_scenes[df_scenes['Active_Category'] == cat]
            
            for idx, row in df_cat_scenes.iterrows():
                col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.5, 1, 1, 1, 3, 2, 3])
                
                # Ambil status dari dataframe
                current_status = False
                if 'Status_Take' in row and pd.notna(row['Status_Take']):
                    current_status = bool(row['Status_Take'])
                
                with col_chk:
                    is_checked = st.checkbox("", value=current_status, key=f"chk_{pilihan_menu}_{idx}")
                    checkbox_states[idx] = is_checked
                    
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
            
        submit_button = st.form_submit_button(label="💾 Simpan Perubahan Status (Update ke Semua Perangkat)")
        
        if submit_button:
            # Update status ke dataframe utama
            for idx, val in checkbox_states.items():
                df_hari.loc[idx, 'Status_Take'] = val
            
            # Simpan perubahan ke file Excel fisik di server
            save_status_to_excel(pilihan_menu, df_hari)
            st.success("✅ Status berhasil diperbarui dan disinkronkan ke seluruh perangkat!")
            st.rerun()

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")