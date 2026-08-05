import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi halaman Streamlit agar lebar (wide mode)
st.set_page_config(page_title="Dashboard Monitoring Produksi", layout="wide")

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

excel_file = 'Database_Jadwal_Produksi.xlsx'

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
    
    state_key = f'status_{pilihan_menu}'
    if state_key not in st.session_state:
        st.session_state[state_key] = {idx: False for idx in df_scenes.index}
        
    completed_count = sum(st.session_state[state_key].values())
    remaining_count = total_scenes - completed_count
    
    # 📊 TAMPILAN REKAP / METRICS PROGRESS
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Scene", total_scenes)
    col_m2.metric("Sudah Take (Selesai)", completed_count)
    col_m3.metric("Sisa Belum Take", remaining_count)
    
    st.markdown("---")

    # ==========================================
    # 🖨️ FITUR PANEL CETAK (A4 LANDSCAPE VIEW)
    # ==========================================
    with st.expander("🖨️ Buka Panel Cetak (Format Call Sheet A4 Landscape)", expanded=False):
        st.markdown("""
        <style>
            .print-container {
                background-color: white;
                color: black;
                padding: 30px;
                font-family: Arial, sans-serif;
                width: 100%;
                max-width: 1120px;
                margin: auto;
                border: 1px solid #ccc;
            }
            .print-header {
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
            }
            .print-title {
                text-align: center;
                color: red;
                font-weight: bold;
                font-size: 22px;
                margin-bottom: 25px;
            }
            .info-table {
                width: 100%;
                margin-bottom: 20px;
                font-size: 14px;
            }
            .info-table td {
                padding: 4px 8px;
                vertical-align: top;
            }
            .schedule-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 12px;
            }
            .schedule-table th, .schedule-table td {
                border: 1px solid #333;
                padding: 6px 8px;
                text-align: left;
            }
            .schedule-table th {
                background-color: #f2f2f2;
            }
            @media print {
                body { visibility: hidden; }
                .print-container { visibility: visible; position: absolute; left: 0; top: 0; width: 100%; border: none; }
            }
        </style>
        """, unsafe_allow_html=True)

        # Logika otomatis pengisian data kuning berdasarkan pilihan menu
        loc_mapping = {
            "Day 1": "MAHARAJA DEPOK",
            "Day 2": "RUMAH SAKIT VIP / LORONG",
            "Day 3": "RUMAH INTAN & MASJID",
            "Master Schedule" : "ALL LOCATIONS"
        }
        lokasi_terkini = loc_mapping.get(pilihan_menu, "JAKARTA & SEKITARNYA")
        tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")

        st.markdown(f"""
        <div class="print-container">
            <div class="print-header">SCHEDULE SERIES</div>
            <div class="print-title">"DIPAKSA MENIKAH"</div>
            
            <table class="info-table">
                <tr>
                    <td style="width: 15%;"><b>PRODUCTION</b></td>
                    <td style="width: 35%;">: MD Entertainment</td>
                    <td style="width: 15%;"><b>SHOOTING</b></td>
                    <td style="width: 35%;">: <b>{pilihan_menu.upper()}</b></td>
                </tr>
                <tr>
                    <td><b>DIRECTOR</b></td>
                    <td>: <span style="background-color: yellow;">ANTO AGAM</span></td>
                    <td><b>DATE</b></td>
                    <td>: <span style="background-color: yellow;">{tanggal_hari_ini}</span></td>
                </tr>
                <tr>
                    <td><b>DOP</b></td>
                    <td>: <span style="background-color: yellow;">FENDI</span></td>
                    <td><b>CREW CALL</b></td>
                    <td>: 06.00 WIB</td>
                </tr>
                <tr>
                    <td><b>ART DIRECTOR</b></td>
                    <td>: <span style="background-color: yellow;">RIZAL</span></td>
                    <td><b>LOCATION</b></td>
                    <td>: <span style="background-color: yellow;">{lokasi_terkini}</span></td>
                </tr>
                <tr>
                    <td><b>PIMPRO</b></td>
                    <td>: <span style="background-color: yellow;">LENA</span></td>
                    <td><b>ON CAM</b></td>
                    <td>: 08.00 WIB</td>
                </tr>
            </table>

            <hr style="border: 1px solid black; margin-bottom: 15px;">
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">NO</th>
                        <th style="width: 8%;">SCENE</th>
                        <th style="width: 6%;">I/E</th>
                        <th style="width: 25%;">SET</th>
                        <th style="width: 20%;">PROPERTY</th>
                        <th style="width: 16%;">CAST</th>
                        <th style="width: 20%;">REMARK</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)

        # Render baris tabel otomatis untuk cetak
        for idx, row in df_scenes.iterrows():
            st.markdown(f"""
                    <tr>
                        <td>{row.get('No', '')}</td>
                        <td><b>{row.get('Scene', '')}</b></td>
                        <td>{row.get('I/E', '')}</td>
                        <td>{row.get('SET', '')}</td>
                        <td>{row.get('PROPERTY', '')}</td>
                        <td>{row.get('CAST', '')}</td>
                        <td>{row.get('REMARK', '')}</td>
                    </tr>
            """, unsafe_allow_html=True)

        st.markdown("""
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 Tip: Anda bisa menekan tombol `Ctrl + P` di keyboard Anda atau klik kanan lalu pilih 'Print' setelah panel ini dibuka untuk mencetak dokumen dalam ukuran A4 Landscape.")

    st.markdown("---")
    st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")
    
    unique_categories = df_scenes['Active_Category'].dropna().unique()
    
    for cat in unique_categories:
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