import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="Dashboard Produksi - Dipaksa Menikah",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Jadwal Dashboard & Breakdown Produksi")
st.subheader("Serial: Dipaksa Menikah (Episode 1 - Rencana Jadwal 3 Hari)")

excel_file = "Plan_Schedule_Dipaksa_Menikah_3_Days.xlsx"

@st.cache_data
def load_data(file_path):
    xls = pd.ExcelFile(file_path)
    data_dict = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, skiprows=2)
        data_dict[sheet] = df
    return data_dict

try:
    sheets_data = load_data(excel_file)
    
    # Sidebar Navigasi & Kontrol
    st.sidebar.header("⚙️ Navigasi & Kontrol")
    selected_day = st.sidebar.selectbox("Pilih Hari Syuting", list(sheets_data.keys()))
    
    # Opsi Tampilan Khusus HP / Mobile Mode di Sidebar
    st.sidebar.markdown("---")
    mobile_mode = st.sidebar.checkbox("📱 Tampilan Ringkas (Fokus HP / Pimpro)", value=False, help="Centang ini jika dibuka via HP agar tampilan ringkas fokus pada monitor progress.")
    
    df_selected = sheets_data[selected_day].copy()
    df_scenes = df_selected.dropna(subset=['Scene'])
    
    # Inisialisasi Session State untuk checkbox
    if 'taken_status' not in st.session_state:
        st.session_state.taken_status = {}
        
    for sheet in sheets_data.keys():
        if sheet not in st.session_state.taken_status:
            sub_df = sheets_data[sheet].dropna(subset=['Scene'])
            st.session_state.taken_status[sheet] = {str(row['Scene']): False for _, row in sub_df.iterrows()}

    # Hitung Statistik Monitor
    total_scenes = len(df_scenes)
    taken_count = sum(1 for sc in df_scenes['Scene'] if st.session_state.taken_status[selected_day].get(str(sc), False))
    remaining_count = total_scenes - taken_count
    completion_pct = int((taken_count / total_scenes) * 100) if total_scenes > 0 else 0
    untaken_pct = 100 - completion_pct

    # --- LOGIKA ACUAN WAKTU & TARGET PIMPRO ---
    # Asumsi Acuan Waktu Operasional Syuting per Hari:
    # Sesi 1: 08.00 - 12.00 (On Cam Pagi)
    # Ishoma 1: 12.00 - 13.00
    # Sesi 2: 13.01 - 18.00 (Siang - Sore)
    # Ishoma 2: 18.00 - 19.00 (atau menyesuaikan MTM/Rehat)
    # Sesi 3/Malam: 19.01 - 24.00 (Batas Maksimal Syuting Jam 24.00)
    
    current_hour = datetime.datetime.now().hour
    current_minute = datetime.datetime.now().minute
    current_time_val = current_hour + (current_minute / 60.0)
    
    # 3 Kolom KPI Monitor Utama (Tampil di Laptop & HP)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"Keseluruhan Adegan ({selected_day})", value=total_scenes)
    with col2:
        st.metric(label="Scene Sudah Take", value=taken_count, delta=f"{completion_pct}%")
    with col3:
        st.metric(label="Sisa Belum Take", value=remaining_count, delta=f"-{remaining_count}" if remaining_count > 0 else "Selesai!", delta_color="inverse")
        
    # --- PENGINGAT / PERHATIAN OTOMATIS UNTUK PIMPRO ---
    # Akan muncul langsung secara dinamis begitu ada adegan yang di-take, 
    # dan memberikan perhatian khusus setelah Ishoma pertama (> jam 13.00) jika masih banyak yang belum take.
    st.markdown("---")
    if taken_count == 0:
        st.info("ℹ️ **Status Pimpinan Produksi (Pimpro):** Belum ada adegan yang dicentang selesai (Take). Silakan pantau eksekusi di set.")
    else:
        # Cek apakah sudah lewat Ishoma pertama (>= jam 13:00)
        is_after_ishoma_1 = current_time_val >= 13.0
        
        if is_after_ishoma_1 and remaining_count > (total_scenes * 0.5):
            st.warning(f"⚠️ **PERHATIAN PIMPRO (Post-Ishoma 1):** Waktu telah melewati jam 13.00. Sisa scene yang **belum di-take masih {remaining_count} adegan ({untaken_pct}%)**. Mohon segera cek kendala di lapangan agar target selesai maksimal jam 24.00 tercapai!")
        elif remaining_count == 0:
            st.success("🎉 **Luar Biasa!** Seluruh target scene hari ini tuntas sepenuhnya.")
        else:
            st.info(f"📊 **Monitor Waktu & Target:** Progress berjalan {completion_pct}%. Sisa adegan belum take: **{remaining_count} scene ({untaken_pct}%)**.")

    st.markdown("---")
    
    # JIKA MODE HP / RINGKAS DICENTANG DI SIDEBAR
    if mobile_mode:
        st.info("📱 **Mode Ringkas HP Aktif:** Daftar scene vertikal untuk memudahkan Pimpro memantau langsung setiap 1 centang *take*.")
        
        for idx, row in df_scenes.iterrows():
            sc_key = str(row['Scene'])
            is_taken = st.session_state.taken_status[selected_day].get(sc_key, False)
            
            c_m1, c_m2 = st.columns([1, 4])
            with c_m1:
                new_chk = st.checkbox("Take", value=is_taken, key=f"mob_chk_{selected_day}_{sc_key}")
                if new_chk != is_taken:
                    st.session_state.taken_status[selected_day][sc_key] = new_chk
                    st.rerun()
            with c_m2:
                st.write(f"**Sc. {row['Scene']}** | {row['N/D']} | *{row['SET']}*")
            st.divider()
            
    else:
        # TAMPILAN NORMAL (UNTUK LAPTOPS / KOMPUTER)
        st.markdown("### 🖨️ Pilihan Cetak & Ekspor Laporan")
        c_btn1, c_btn2, c_btn3 = st.columns(3)
        
        csv_data = df_scenes.to_csv(index=False).encode('utf-8')
        c_btn1.download_button(
            label=f"📥 Download {selected_day} (CSV)",
            data=csv_data,
            file_name=f"Jadwal_{selected_day}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        with open(excel_file, "rb") as f:
            excel_bytes = f.read()
        c_btn2.download_button(
            label="📥 Download Master Excel (3 Hari)",
            data=excel_bytes,
            file_name="Plan_Schedule_Dipaksa_Menikah_3_Days.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        if c_btn3.button("🖨️ Cetak / Print Halaman (PDF)", use_container_width=True):
            st.info("💡 Tip Cetak: Tekan **Ctrl + P** di keyboard Anda untuk mencetak atau menyimpan halaman ini sebagai PDF.")

        st.markdown("---")
        st.markdown(f"### 📋 Rincian Jadwal Syuting & Checklist - {selected_day}")
        st.write("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")
        
        h1, h2, h3, h4, h5, h6, h7 = st.columns([0.8, 1, 1, 1.2, 3, 2.5, 3])
        h1.markdown("**Status**")
        h2.markdown("**Scene**")
        h3.markdown("**N/D**")
        h4.markdown("**Page(s)**")
        h5.markdown("**Set Lokasi**")
        h6.markdown("**Cast**")
        h7.markdown("**Remark**")
        st.markdown("---")
        
        for idx, row in df_selected.iterrows():
            if pd.isna(row['Scene']):
                section_title = row['No'] if not pd.isna(row['No']) else "KLASTER LOKASI"
                st.markdown(f"<div style='background-color: #D9E1F2; color: #1F3864; padding: 8px; font-weight: bold; border-radius: 4px; margin-top: 10px;'>📁 {section_title}</div>", unsafe_allow_html=True)
                continue
                
            sc_key = str(row['Scene'])
            is_taken = st.session_state.taken_status[selected_day].get(sc_key, False)
            
            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 1, 1, 1.2, 3, 2.5, 3])
            with c1:
                new_val = st.checkbox("Take", value=is_taken, key=f"chk_{selected_day}_{sc_key}", label_visibility="collapsed")
                if new_val != is_taken:
                    st.session_state.taken_status[selected_day][sc_key] = new_val
                    st.rerun()
            with c2:
                st.write(str(row['Scene']))
            with c3:
                st.write(str(row['N/D']))
            with c4:
                st.write(str(row['Page(s)']))
            with c5:
                st.write(str(row['SET']))
            with c6:
                st.write(str(row['CAST']))
            with c7:
                st.write(str(row['REMARK']))
            
except Exception as e:
    st.error(f"Error memuat dashboard: {e}")