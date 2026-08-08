import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. Konfigurasi Kredensial dan Koneksi ke Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDS_FILE = "credentials.json"

try:
  creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
  client = gspread.authorize(creds)

  # Buka Google Sheet 'Master_Penjualan_Kue'
  spreadsheet = client.open("Master_Penjualan_Kue")
  sheet_input = spreadsheet.worksheet("Input_Penjualan")
  data_input = sheet_input.get_all_records()

  # Konversi ke DataFrame Pandas untuk analisis
  df = pd.DataFrame(data_input)
  print("--- DATA MASTER PENJUALAN KUE BERHASIL DIMUAT ---")
  print(df.head())

  # Hitung Ringkasan KPI Utama
  if not df.empty and "Total Omzet Jual (Rp)" in df.columns:
    grand_omzet = df["Total Omzet Jual (Rp)"].sum()
    grand_setoran = df["Total Setoran Penitip (Rp)"].sum()
    grand_margin = df["Total Margin / Untung (Rp)"].sum()
    grand_terjual = df["Terjual"].sum()

    print(f"\nTotal Omzet Jual        : Rp {grand_omzet:,.0f}")
    print(f"Total Setoran Penitip   : Rp {grand_setoran:,.0f}")
    print(f"Total Margin Keuntungan : Rp {grand_margin:,.0f}")
    print(f"Total Kue Terjual       : {grand_terjual} pcs")

    # Update Dashboard di Google Sheets secara otomatis
    sheet_dash = spreadsheet.worksheet("Dashboard_Rekap")
    sheet_dash.update("A4", [["RINGKASAN KPI UTAMA (REALTIME)"]])
    sheet_dash.update(
        "A5:D5",
        [[
            f"Omzet: Rp {grand_omzet:,.0f}",
            f"Setoran: Rp {grand_setoran:,.0f}",
            f"Margin: Rp {grand_margin:,.0f}",
            f"Terjual: {grand_terjual} Pcs",
        ]],
    )
    print(
        "\n[SUKSES] Dashboard Rekap di Google Sheets berhasil diperbarui secara"
        " realtime!"
    )
  else:
    print(
        "[INFO] Data masih kosong atau format kolom belum sesuai, silakan isi"
        " data di Input_Penjualan."
    )

except Exception as e:
  print(f"[TERJADI KESALAHAN]: {e}")
