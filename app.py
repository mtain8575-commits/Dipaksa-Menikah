import streamlit as st
import pandas as pd

# Membaca file excel database Anda
excel_file = 'Database_Jadwal_Produksi.xlsx' 
df = pd.read_excel(excel_file, sheet_name=0)

st.markdown("### 🔍 Pemeriksaan Kolom DataFrame")
st.write("Daftar kolom yang terbaca di file Excel Anda:")
st.write(df.columns.tolist())