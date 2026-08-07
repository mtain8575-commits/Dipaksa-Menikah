import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Jadwal Dashboard & Breakdown Produksi", layout="wide"
)

# Inisialisasi session_state agar status centang tersimpan permanen saat refresh
if "saved_status" not in st.session_state:
  st.session_state.saved_status = {}

st.markdown("### 🎬 Jadwal Dashboard & Breakdown Produksi")
st.markdown("**Serial: Dipaksa Menikah (Episode 1 - Rencana Jadwal 3 Hari)**")

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

    df = df.reset_index(drop=True)
    return df
  except Exception as e:
    return None


df = load_data(pilihan_menu)

if df is not None and not df.empty:
  # Terapkan status dari session_state agar tidak hilang saat refresh
  for idx, row in df.iterrows():
    unique_key = f"{pilihan_menu}_row_{idx}"
    if unique_key in st.session_state.saved_status:
      df.loc[idx, "Status"] = st.session_state.saved_status[unique_key]
    else:
      val = row.get("Status", False)
      is_checked = (
          True
          if str(val).lower().strip() in ["true", "1", "sudah", "yes"]
          else False
      )
      df.loc[idx, "Status"] = is_checked
      st.session_state.saved_status[unique_key] = is_checked

  # Hitung statistik adegan valid
  scene_mask = (
      df["No"].notna()
      & ~df["No"].astype(str).str.contains("SET CATEGORY|SET CA|📌", na=False)
      & (df["No"].astype(str).str.strip() != "")
  )
  scene_df = df[scene_mask]

  total_scene = len(scene_df)
  sudah_take = len(scene_df[scene_df["Status"] == True])
  belum_take = total_scene - sudah_take

  st.markdown("---")

  # Metrik Atas
  col1, col2, col3 = st.columns(3)
  col1.metric(f"Keseluruhan Adegan ({pilihan_menu.upper()})", total_scene)
  col2.metric("Scene Sudah Take", sudah_take, delta=f"{sudah_take} Selesai")
  col3.metric("Sisa Belum Take", belum_take, delta=f"-{belum_take}", delta_color="inverse")

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

  st.markdown(
      f"#### 📋 Rincian Jadwal Syuting & Checklist - {pilihan_menu.upper()}"
  )
  st.caption("Centang kotak pada kolom Status jika adegan sudah selesai direkam:")

  # Render baris per kategori set dan checklist lengkap dengan kolom Cast
  for idx, row in df.iterrows():
    val_no = str(row.get("No", ""))
    if "SET CATEGORY" in val_no or "SET CA" in val_no:
      cat_text = next(
          (str(val) for val in row.values if pd.notna(val) and str(val).strip() != ""),
          "SET CATEGORY",
      )
      st.markdown(
          f"""
            <div style="background-color: #1e293b; padding: 10px 15px; border-radius: 6px; border-left: 5px solid #3b82f6; margin-top: 15px; margin-bottom: 8px; font-weight: bold; color: #ffffff;">
                📁 {cat_text}
            </div>
            """,
          unsafe_allow_html=True,
      )
    elif val_no.strip() != "":
      sc_no = row.get("Scene", "")
      nd = row.get("N/D", "")
      page = row.get("Page(s)", "")
      set_lok = row.get("SET", "")
      cast = row.get("CAST", "")
      property_val = row.get("PROPERTY", "")

      # Proporsi kolom disesuaikan agar kolom Cast (paling kanan) tampil pas
      cols = st.columns([0.5, 0.8, 0.8, 0.8, 1.2, 2.2, 1.8, 1.8])
      with cols[0]:
        unique_key = f"{pilihan_menu}_row_{idx}"
        current_val = bool(st.session_state.saved_status.get(unique_key, False))
        checked = st.checkbox("", value=current_val, key=f"widget_{unique_key}")

        if checked != current_val:
          st.session_state.saved_status[unique_key] = checked
          df.loc[idx, "Status"] = checked
          st.rerun()

      with cols[1]:
        st.write(f"**{row.get('No', '')}**")
      with cols[2]:
        st.write(str(sc_no))
      with cols[3]:
        st.write(str(nd))
      with cols[4]:
        st.write(str(page))
      with cols[5]:
        st.write(str(set_lok))
      with cols[6]:
        st.write(str(property_val))
      with cols[7]:
        st.write(str(cast))  # Kolom Cast yang diminta

      st.markdown(
          "<hr style='margin: 4px 0px; border-color: #334155;'>",
          unsafe_allow_html=True,
      )
else:
  st.error("❌ Gagal memuat data dari file Excel.")
