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

excel_file = "Database_Schedule_Produksi.xlsx"

# Fungsi otomatis mendeteksi letak kolom Scene di setiap sheet
def load_sheets_data(file_path):
    xls = pd.ExcelFile(file_path)
    data_dict = {}
    for sheet in xls.sheet_names:
        df_raw = pd.read_excel(file_path, sheet_name=sheet)
        header_row = 0
        for i, row in df_raw.iterrows():
            if 'Scene' in row.values:
                header_row = i
                break
        
        df = pd.read_excel(file_path, sheet_name=sheet, skiprows=header_row)
        df = df.dropna(how='all')
        
        if 'Status' not in df.columns:
            df['Status'] = False
        
        df['Status'] = df['Status'].fillna(False).astype(bool)
        data_dict[sheet] = df
    return data_dict

try:
    sheets_data = load_sheets_data(excel_file)

    # Sidebar Navigasi & Kontrol
    st.sidebar.header("⚙️ Navigasi & Kontrol")
    selected_day = st.sidebar.selectbox("Pilih Hari Syuting", list(sheets_data.keys()))
    
    st.sidebar.markdown("---")
    mobile_mode = st.sidebar.checkbox("📱 Tampilan Ringkas (Fokus HP / Pimpro)", value=False, help="Centang ini jika dibuka via HP agar tampilan ringkas fokus pada monitor progress.")
    
    df_selected = sheets_data[selected_day].copy()
    
    if 'Scene' in df_selected.columns:
        df_scenes = df_selected.dropna(subset=['Scene'])
    else:
        df_scenes = pd.DataFrame()

    total_scenes = len(df_scenes)
    taken_count = int(df_scenes['Status'].sum()) if 'Status' in df_scenes.columns and not df_scenes.empty else 0
    remaining_count = total_scenes - taken_count
    completion_pct = int((taken_count / total_scenes) * 100) if total_scenes > 0 else 0
    untaken_pct = 100 - completion_pct

    current_hour = datetime.datetime.now().hour
    current_minute = datetime.datetime.now().minute
    current_time_val = current_hour + (current_minute / 60.0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"Keseluruhan Adegan ({selected_day})", value=total_scenes)
    with col2:
        st.metric(label="Scene Sudah Take", value=taken_count, delta=f"{completion_pct}%")
    with col3:
        st.metric(label="Sisa Belum Take", value=remaining_count, delta=f"-{remaining_count}" if remaining_count > 0 else "Selesai!", delta_color="inverse")
        
    st.markdown("---")
    if taken_count == 0:
        st.info("ℹ️ **Status Pimpinan Produksi (Pimpro):** Belum ada adegan yang dicentang selesai (Take). Silakan pantau eksekusi di set.")
    else:
        is_after_ishoma_1 = current_time_val >= 13.0
        if is_after_ishoma_1 and remaining_count > (total_scenes * 0.5):
            st.warning(f"⚠️ **PERHATIAN PIMPRO (Post-Ishoma 1):** Sisa scene yang **belum di-take masih {remaining_count} adegan ({untaken_pct}%)**. Mohon segera cek kendala di lapangan!")
        elif remaining_count == 0:
            st.success("🎉 **Luar Biasa!** Seluruh target scene hari ini tuntas sepenuhnya.")
        else:
            st.info(f"📊 **Monitor Waktu & Target:** Progress berjalan {completion_pct}%. Sisa adegan belum take: **{remaining_count} scene ({untaken_pct}%)**.")

    st.markdown("---")
    
    def update_excel_status(sheet_name, scene_val, new_status):
        xls = pd.ExcelFile(excel_file)
        writer_dfs = {}
        for s in xls.sheet_names:
            df_raw = pd.read_excel(excel_file, sheet_name=s)
            header_row = 0
            for i, row in df_raw.iterrows():
                if 'Scene' in row.values:
                    header_row = i
                    break
            temp_df = pd.read_excel(excel_file, sheet_name=s, skiprows=header_row)
            if 'Status' not in temp_df.columns:
                temp_df['Status'] = False
            writer_dfs[s] = temp_df, header_row
            
        df_to_up, h_row = writer_dfs[sheet_name]
        mask = df_to_up['Scene'].astype(str) == str(scene_val)
        df_to_up.loc[mask, 'Status'] = new_status
        writer_dfs[sheet_name] = (df_to_up, h_row)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            for s, (df_to_write, h_r) in writer_dfs.items():
                df_to_write.to_excel(writer, sheet_name=s, index=False, startrow=h_r)

    if mobile_mode:
        st.info("📱 **Mode Ringkas HP Aktif:** Setiap centang akan langsung tersinkronisasi ke file master.")
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
                nd_val = row['N/D'] if 'N/D' in row and pd.notna(row['N/D']) else ""
                set_val = row['SET'] if 'SET' in row and pd.notna(row['SET']) else ""
                st.write(f"**Sc. {sc_val}** | {nd_val} | *{set_val}*")
            st.divider()
            
    else:
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
            file_name="Database_Schedule_Produksi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        if c_btn3.button("🖨️ Cetak / Print Halaman (PDF)", use_container_width=True):
            st.info("💡 Tip Cetak: Tekan **Ctrl + P** di keyboard Anda untuk mencetak atau menyimpan halaman ini sebagai PDF.")

        st.markdown("---")
        st.markdown(f"### 📋 Rincian Jadwal Syuting & Checklist - {selected_day}")
        
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
            sc_val = row['Scene'] if 'Scene' in row else None
            if pd.isna(sc_val):
                continue
                
            sc_key = str(sc_val)
            is_taken = bool(row['Status'])
            
            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 1, 1, 1.2, 3, 2.5, 3])
            with c1:
                new_val = st.checkbox("Take", value=is_taken, key=f"chk_{selected_day}_{sc_key}", label_visibility="collapsed")
                if new_val != is_taken:
                    update_excel_status(selected_day, sc_val, new_val)
                    st.rerun()
            with c2:
                st.write(str(row.get('Scene', '')))
            with c3:
                st.write(str(row.get('N/D', '')))
            with c4:
                st.write(str(row.get('Page(s)', '')))
            with c5:
                st.write(str(row.get('SET', '')))
            with c6:
                st.write(str(row.get('CAST', '')))
            with c7:
                st.write(str(row.get('REMARK', '')))
            
except Exception as e:
    st.error(f"Error memuat dashboard: {e}")