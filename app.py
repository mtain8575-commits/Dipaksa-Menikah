import pandas as pd
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Breakdown Produksi", layout="wide"
)

# 1. JUDUL & SUBTITLE UTAMA
st.markdown(
    "### 🎬 Jadwal Dashboard & Breakdown Produksi"
)  # Menggunakan markdown biasa agar bersih
st.markdown("**Serial: Dipaksa Menikah (Episode 1 - Rencana Jadwal 3 Hari)**")

# Dropdown pilihan hari syuting
pilihan_menu = st.selectbox(
    "Pilih Hari Syuting / Master Schedule",
    ["Master Schedule", "Day 1", "Day 2", "Day 3"],
)


@st.cache_data(ttl=10)
def load_data(sheet_name):
  try:
    raw_df = pd.read_excel(
        "Database_Jadwal_Produksi.xlsx", sheet_name=sheet_name, header=None
    )

    header_row_index = None
    for idx, row in raw_df.iterrows():
      row_str = row.astype(str).values
      if any("Scene" in str(val) for val in row_str) or any(
          "No" in str(val) for val in row_str
      ):
        header_row_index = idx
        break

    if header_row_index is not None:
      cols = raw_df.iloc[header_row_index].astype(str).str.strip().values
      raw_df.columns = cols
      df = raw_df.iloc[header_row_index + 1 :].copy()
    else:
      df = raw_df

    df = df.loc[:, df.columns.notna()]
    df.columns = [str(c).strip() for c in df.columns]

    if "Status" not in df.columns:
      df["Status"] = False
    else:
      df["Status"] = df["Status"].apply(
          lambda x: True
          if str(x).lower().strip() in ["sudah take", "true", "1", "sudah"]
          else False
      )

    df = df.reset_index(drop=True)
    return df
  except Exception as e:
    return None


df = load_data(pilihan_menu)

if df is not None and not df.empty:
  # Identifikasi baris scene valid (bukan baris kategori set)
  scene_mask = (
      df["No"].notna()
      & ~df["No"].astype(str).str.contains("SET CATEGORY|SET CA|📌", na=False)
      & (df["No"].astype(str).str.strip() != "")
  )
  scene_df = df[scene_mask]

  total_scene = len(scene_df)
  sudah_take = (
      len(scene_df[scene_df["Status"] == True])
      if "Status" in scene_df.columns
      else 0
  )
  belum_take = total_scene - sudah_take

  st.markdown("---")

  # 2. Kotak Metrik Atas
  col1, col2, col3 = st.columns(3)
  col1.metric(f"Keseluruhan Adegan ({pilihan_menu.upper()})", total_scene)
  col2.metric("Scene Sudah Take", sudah_take, delta="0%")
  col3.metric("Sisa Belum Take", belum_take, delta=f"-{belum_take}", delta_color="inverse")

  # 3. Kotak Informasi Status Pimpinan Produksi (Pimpro)
  if sudah_take == 0:
    st.info(
        "ℹ️ Status Pimpinan Produksi (Pimpro): Belum ada adegan yang dicentang"
        " selesai (Take). Silakan pantau eksekusi di set."
    )
  else:
    st.success(
        f"✅ Status Pimpinan Produksi (Pimpro): Sebanyak {sudah_take} scene"
        " telah selesai direkam."
    )

  st.markdown("---")

  # 4. Pilihan Cetak & Ekspor Laporan
  st.markdown("#### 🖨️ Pilihan Cetak & Ekspor Laporan")
  bcol1, bcol2, bcol3 = st.columns(3)
  with bcol1:
    if not scene_df.empty:
      csv_data = scene_df.to_csv(index=False).encode("utf-8")
      st.download_button(
          label=f"📥 Download {pilihan_menu} (CSV)",
          data=csv_data,
          file_name=f"Jadwal_{pilihan_menu}.csv",
          mime="text/csv",
      )
  with bcol2:
    st.button("📥 Download Master Excel (3 Hari)")
  with bcol3:
    st.button("🖨️ Cetak / Print Halaman (PDF)")

  st.markdown("---")

  # 5. Rincian Jadwal Syuting & Checklist
  st.markdown(f"#### 📋 Rincian Jadwal Syuting & Checklist - {pilihan_menu.upper()}")
  st.caption("Centang kotak pada kolom Status jika adegan sudah selesai direkam:")

  # Pindahkan kolom Status ke paling depan agar menjadi kotak centang utama
  other_cols = [c for c in df.columns if c != "Status"]
  df_display = df[["Status"] + other_cols]

  # Tampilkan tabel interaktif dengan Checkbox
  edited_df = st.data_editor(
      df_display,
      use_container_width=True,
      hide_index=True,
      column_config={
          "Status": st.column_config.CheckboxColumn(
              "Status",
              help="Centang jika scene ini sudah selesai direkam",
              default=False,
          )
      },
  )
else:
  st.error("❌ Gagal memuat data dari file Excel.")
