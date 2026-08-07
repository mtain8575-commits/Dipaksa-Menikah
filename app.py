import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Monitoring Produksi", layout="wide"
)

st.markdown("### 📋 Dashboard Monitoring Produksi - Rincian Jadwal & Checklist")

pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule",
    ["Master Schedule", "Day 1", "Day 2", "Day 3"],
)


@st.cache_data(ttl=10)
def load_data(sheet_name):
  try:
    # Baca file excel mentah dulu tanpa header otomatis
    raw_df = pd.read_excel(
        "Database_Jadwal_Produksi.xlsx", sheet_name=sheet_name, header=None
    )

    # Cari baris yang berisi kata 'Scene' atau 'No' untuk dijadikan header yang benar
    header_row_index = None
    for idx, row in raw_df.iterrows():
      row_str = row.astype(str).values
      if any("Scene" in str(val) for val in row_str) or any(
          "No" in str(val) for val in row_str
      ):
        header_row_index = idx
        break

    if header_row_index is not None:
      # Jadikan baris tersebut sebagai header
      raw_df.columns = raw_df.iloc[header_row_index]
      df = raw_df.iloc[header_row_index + 1 :].copy()
    else:
      df = raw_df

    # Bersihkan nama kolom dari NaN atau None / spasi
    df = df.loc[:, df.columns.notna()]
    df.columns = [str(c).strip() for c in df.columns]

    # Hapus baris yang seluruh isinya kosong/None/NaN
    df = df.dropna(how="all")

    # Filter hanya baris yang kolom 'No' atau 'Scene' nya berisi angka/data valid
    if "No" in df.columns:
      # Buang baris kategori set atau baris kosong
      df = df[df["No"].notna()]
      df = df[~df["No"].astype(str).str.contains("SET CATEGORY", na=False)]

    df = df.reset_index(drop=True)
    return df
  except Exception as e:
    return None


df = load_data(pilihan_menu)

if df is not None and not df.empty:
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
  st.error("❌ Gagal memuat data atau format sheet tidak dikenali.")
