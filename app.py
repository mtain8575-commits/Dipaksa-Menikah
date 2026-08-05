import streamlit as st
import pandas as pd

excel_file = 'Database_Jadwal_Produksi.xlsx' 

@st.cache_data
def load_data():
    # Coba baca dengan header berada di baris ke-1 (indeks 1) atau sesuaikan jika baris header Anda di bawahnya
    df_load = pd.read_excel(excel_file, sheet_name=0, header=1)
    # Hapus baris yang seluruh kolomnya kosong
    df_load = df_load.dropna(how='all')
    return df_load

df = load_data()

st.markdown("### 📋 Rincian Jadwal Syuting & Checklist")
st.markdown("Centang kotak pada kolom **Status** jika adegan sudah selesai direkam:")

# Cari kolom yang mirip dengan 'Set Lokasi' atau 'Lokasi'
lokasi_col = None
for col in df.columns:
    if 'lokasi' in str(col).lower() or 'set' in str(col).lower():
        lokasi_col = col
        break

if lokasi_col:
    unique_sets = df[lokasi_col].dropna().unique()
    
    for set_lokasi in unique_sets:
        st.markdown(f"#### 📍 SET LOKASI: {set_lokasi}")
        df_set_group = df[df[lokasi_col] == set_lokasi]
        
        for idx, row in df_set_group.iterrows():
            col_chk, col_scene, col_nd, col_page, col_set, col_cast, col_remark = st.columns([0.6, 1, 1, 1, 3, 2, 3])
            
            with col_chk:
                st.checkbox("", value=False, key=f"chk_{idx}")
            with col_scene:
                st.text(str(row.iloc[1] if len(row) > 1 else ""))
            with col_nd:
                st.text(str(row.iloc[2] if len(row) > 2 else ""))
            with col_page:
                st.text(str(row.iloc[3] if len(row) > 3 else ""))
            with col_set:
                st.text(str(row[lokasi_col]))
            with col_cast:
                st.text(str(row.iloc[5] if len(row) > 5 else ""))
            with col_remark:
                st.text(str(row.iloc[6] if len(row) > 6 else ""))
                
        st.markdown("---")
else:
    st.error("Kolom yang mengandung kata 'Lokasi' atau 'Set' tidak ditemukan dalam tabel.")
    st.write("Kolom yang tersedia:", df.columns.tolist())