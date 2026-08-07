import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Produksi", layout="wide"
)

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

# Dropdown pilihan hari syuting atau master schedule
pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule",
    ["Master Schedule", "Day 1", "Day 2", "Day 3"],
)


# Fungsi membaca file Excel langsung dari repository GitHub Anda
@st.cache_data(ttl=10)
def load_data(sheet_name):
  try:
    # Membaca file excel yang sudah ada di folder GitHub
    df = pd.read_excel("Database_Jadwal_Produksi.xlsx", sheet_name=sheet_name)
    return df
  except Exception as e:
    return None


df = load_data(pilihan_menu)

if df is not None and not df.empty:
  df.columns = df.columns.str.strip()

  if "Status" not in df.columns:
    df["Status"] = "Belum Take"

  st.markdown("---")

  total_scene = len(df)
  sudah_take = len(
      df[df["Status"].astype(str).str.lower().str.contains("sudah", na=False)]
  )
  belum_take = total_scene - sudah_take

  col1, col2, col3 = st.columns(3)
  col1.metric("🎥 Total Scene", total_scene)
  col2.metric("✅ Sudah Take (Selesai)", sudah_take)
  col3.metric("⏳ Sisa Belum Take", belum_take)

  st.markdown("---")
  st.subheader(f"📍 Rincian Jadwal: {pilihan_menu}")

  edited_df = st.data_editor(
      df,
      use_container_width=True,
      hide_index=True,
      column_config={
          "Status": st.column_config.SelectboxColumn(
              "Status Take",
              help="Pilih status pengambilan gambar",
              options=["Belum Take", "Sudah Take"],
              required=True,
          )
      },
  )
else:
  st.error(
      "❌ Gagal memuat data dari file Excel. Pastikan nama sheet di file Excel"
      " sesuai dengan pilihan menu (Master Schedule, Day 1, Day 2, Day 3)."
  )
