import streamlit as st
import pandas as pd
import datetime
import os

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
        # Pastikan ada kolom Status/Take untuk sinkronisasi
        if 'Status' not in df.columns:
            df['Status'] = False
        data_dict[sheet] = df
    return data_dict

try:
    # Load data
    xls = pd.ExcelFile(excel_file)
    sheets_data = {}
    for sheet in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=2)
        if 'Status' not in df.columns:
            df['Status'] = False
        # Ubah tipe data status ke boolean
        df['Status'] = df['Status'].fillna(False).astype(bool)
        sheets_data[sheet] = df

    # Sidebar Navigasi & Kontrol
    st.sidebar.header("⚙️ Navigasi & Kontrol")
    selected_day = st.sidebar.selectbox("Pilih Hari Syuting", list(sheets_data.keys()))
    
    # Opsi Tampilan Khusus HP / Mobile Mode di Sidebar
    st.sidebar.markdown("---")
    mobile_mode = st.sidebar.checkbox("📱 Tampilan Ringkas (Fokus HP / Pimpro)", value=False, help="Centang ini jika dibuka via HP agar tampilan ringkas fokus pada monitor progress.")
    
    df_selected = sheets_data[selected_day].copy()
    df_scenes = df_selected.dropna(subset=['Scene'])

    # Hitung Statistik Monitor Berdasarkan Data Excel
    total_scenes = len(df_scenes)
    taken_count = int(df_scenes['Status'].sum()) if 'Status' in df_scenes.columns else 0
    remaining_count = total_scenes - taken_count
    completion_pct = int((taken_count / total_scenes) * 100) if total_scenes > 0 else 0
    untaken_pct = 100 - completion_pct

    # Waktu Operasional untuk Pimpro
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
    st.markdown("---")
    if taken_count == 0:
        st.info("ℹ️ **Status Pimpinan Produksi (Pimpro):** Belum ada adegan yang dicentang selesai (Take). Silakan pantau eksekusi di set.")
    else:
        is_after_ishoma_1 = current_time_val >= 13.0
        
        if is_after_ishoma_1 and remaining_count > (total_scenes * 0.5):
            st.warning(f"⚠️ **PERHATIAN PIMPRO (Post-Ishoma 1):** Waktu telah melewati jam 13.00. Sisa scene yang **belum di-take masih {remaining_count} adegan ({untaken_pct}%)**. Mohon segera cek kendala di lapangan agar target selesai maksimal jam 24.00 tercapai!")
        elif remaining_count == 0:
            st.success("🎉 **Luar Biasa!** Seluruh target scene hari ini tuntas sepenuhnya.")
        else:
            st.info(f"📊 **Monitor Waktu & Target:** Progress berjalan {completion_pct}%. Sisa adegan belum take: **{remaining_count} scene ({untaken_pct}%)**.")

    st.markdown("---")
    
    # Fungsi pembantu untuk menyimpan perubahan ke file Excel master
    def update_excel_status(sheet_name, scene_val, new_status):
        # Baca ulang file master excel untuk menghindari konflik
        book = pd.ExcelFile(excel_file)
        writer_dfs = {}
        for s in book.sheet_names:
            temp_df = pd.read_excel(excel_file, sheet_name=s, skiprows=2)
            if 'Status' not in temp_df.columns:
                temp_df['Status'] = False
            writer_dfs[s] = temp_df
            
        # Update baris yang sesuai
        mask = writer_dfs[sheet_name]['Scene'].astype(str) == str(scene_val)
        writer_dfs[sheet_name].loc[mask, 'Status'] = new_status
        
        # Simpan kembali ke file Excel asli
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            for s, df_to_write in writer_dfs.items():
                # Tulis ulang dengan mempertahankan struktur baris awal (skiprows=2 ditangani saat baca, jadi kita tulis data mentahnya)
                # Untuk keamanan, kita tulis kembali dataframe lengkap ke sheet
                df_to_write.to_excel(writer, sheet_name=s, index=False, startrow=2)

    # JIKA MODE HP / RINGKAS DICENTANG DI SIDEBAR
    if mobile_mode:
        st.info("📱 **Mode Ringkas HP Aktif:** Setiap centang oleh Ast. Schedule/Pimpro akan langsung tersinkronisasi ke file master.")
        
        for idx, row in df_scenes.iterrows():
            sc_val = row['Scene']
            sc_key = str(sc_val)
            is_taken = bool(row['Status'])
            
            c_m1, c_m2 = st.columns([1, 4])
            with c_m1:
                new_chk = st.checkbox("Take", value=is_taken, key=f"mob_chk_{selected_day}_{sc_key}")
                if new_chk != is_taken:
                    update_excel_status(selected_day, sc_val, new_chk)
                    st.rerun()
            with c_m2:
                st.write(f"**Sc. {sc_val}** | {row['N/D']} | *{row['SET']}*")
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
                
            sc_val = row['Scene']
            sc_key = str(sc_val)
            is_taken = bool(row['Status'])
            
            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 1, 1, 1.2, 3, 2.5, 3])
            with c1:
                new_val = st.checkbox("Take", value=is_taken, key=f"chk_{selected_day}_{sc_key}", label_visibility="collapsed")
                if new_val != is_taken:
                    update_excel_status(selected_day, sc_val, new_val)
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