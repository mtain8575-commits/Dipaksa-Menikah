import pandas as pd
import streamlit as st

# Konfigurasi halaman Streamlit agar lebar (wide mode)
st.set_page_config(
    page_title="Dashboard Monitoring Produksi", layout="wide"
)

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

# Dropdown pilihan hari syuting atau master schedule
pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule",
    ["Day 1", "Day 2", "Day 3", "Master Schedule"],
)

# -------------------------------------------------------------
# MASUKKAN LINK CSV GOOGLE SHEETS ANDA DI BAWAH INI:
# -------------------------------------------------------------
SHEET_URLS = {
    "Master Schedule": "LINK_CSV_MASTER_SCHEDULE_ANDA",
    "Day 1": "LINK_CSV_LINK_ANDA_DISINI",
    "Day 2": "LINK_CSV_DAY_2_ANDA",
    "Day 3": "LINK_CSV_DAY_3_ANDA",
}


# Fungsi untuk mengambil data dari Google Sheets secara otomatis
@st.cache_data(ttl=10)
def load_data(url):
  try:
    df = pd.read_csv(url)
    return df
  except Exception as e:
    return None


# Ambil URL sesuai menu yang dipilih
selected_url = SHEET_URLS.get(pilihan_menu)

if "LINK_CSV" in selected_url:
  st.warning(
      "⚠️ Silakan masukkan link CSV Google Sheets yang valid untuk tab ini"
      " pada bagian konfigurasi kode di atas."
  )
else:
  df = load_data(selected_url)

  if df is not None and not df.empty:
    # Bersihkan nama kolom dari spasi berlebih jika ada
    df.columns = df.columns.str.strip()

    # Pastikan kolom Status ada
    if "Status" not in df.columns:
      df["Status"] = "Belum Take"

    st.markdown("---")

    # Hitung Statistik Ringkasan
    total_scene = len(df)
    sudah_take = len(df[df["Status"].astype(str).str.contains("Sudah", na=False)])
    belum_take = total_scene - sudah_take

    col1, col2, col3 = st.columns(3)
    col1.metric("🎥 Total Scene", total_scene)
    col2.metric("✅ Sudah Take (Selesai)", sudah_take)
    col3.metric("⏳ Sisa Belum Take", belum_take)

    st.markdown("---")
    st.subheader(f"📍 Rincian Jadwal: {pilihan_menu}")

    # Tampilkan data interaktif dengan opsi checklist
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
        "❌ Gagal memuat data. Pastikan link Google Sheets sudah di-publish ke"
        " web berformat CSV."
    )
