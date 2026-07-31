import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Produksi Film - Dipaksa Menikah", page_icon="??", layout="wide")

def parse_pages(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    total = 0.0
    parts = val_str.split()
    for p in parts:
        if '/' in p:
            try:
                num, den = p.split('/')
                total += float(num) / float(den)
            except:
                pass
        else:
            try:
                total += float(p)
            except:
                pass
    return total

@st.cache_data
def load_data():
    file_name = 'Master_Schedule_Dipaksa_Menikah.xlsx'
    xls = pd.ExcelFile(file_name)
    
    all_data = []
    for s in xls.sheet_names:
        if 'DAY' in s.upper():
            df_raw = pd.read_excel(file_name, sheet_name=s)
            header_row_idx = None
            for idx in range(len(df_raw)):
                row_vals = df_raw.iloc[idx].values
                row_str = " ".join([str(v) for v in row_vals if pd.notna(v)]).upper()
                if 'SCENE' in row_str or 'SET' in row_str:
                    header_row_idx = idx
                    break
            
            if header_row_idx is not None:
                current_group = "MAIN SET"
                rows_list = []
                raw_headers = df_raw.iloc[header_row_idx].values
                
                # Make headers unique to avoid DataFrame duplication error
                seen = {}
                cols_header = []
                for h in raw_headers:
                    h_str = str(h).strip() if pd.notna(h) else "UNNAMED"
                    if h_str in seen:
                        seen[h_str] += 1
                        cols_header.append(f"{h_str}_{seen[h_str]}")
                    else:
                        seen[h_str] = 0
                        cols_header.append(h_str)
                
                for idx in range(header_row_idx + 1, len(df_raw)):
                    row_vals = df_raw.iloc[idx].values
                    if len(row_vals) == 0:
                        continue
                    col0_val = row_vals[0]
                    
                    if pd.notna(col0_val):
                        col0_str = str(col0_val).strip()
                        col0_upper = col0_str.upper()
                        if col0_upper.startswith('SET') or 'MEMORI' in col0_upper or 'RUMAH' in col0_upper or 'SEKOLAH' in col0_upper or 'KANTOR' in col0_upper or 'KLIMAKS' in col0_upper or 'JALANAN' in col0_upper:
                            current_group = col0_str
                            continue
                        if col0_upper == 'SECTION':
                            continue
                            
                    if pd.notna(col0_val):
                        row_dict = {}
                        for c_i, col_name in enumerate(cols_header):
                            if c_i < len(row_vals):
                                val = row_vals[c_i]
                                if not pd.isna(val):
                                    row_dict[col_name] = val
                        row_dict['Kategori_Set'] = current_group
                        row_dict['Hari Syuting'] = s
                        rows_list.append(row_dict)
                
                if rows_list:
                    df_s = pd.DataFrame(rows_list)
                    all_data.append(df_s)
                
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
    else:
        df = pd.read_excel(file_name, sheet_name='Master Schedule DPM')
        df['Hari Syuting'] = 'DAY 1'
        df['Kategori_Set'] = 'MAIN SET'
        
    column_mapping = {}
    for col in df.columns:
        col_str = str(col).strip().upper()
        if 'SCENE' in col_str and 'Scene' not in column_mapping.values():
            column_mapping[col] = 'Scene'
        elif ('I/E' in col_str or 'INT' in col_str) and 'INT/EXT' not in column_mapping.values():
            column_mapping[col] = 'INT/EXT'
        elif ('LOKASI' in col_str or col_str == 'SET') and 'Set' not in column_mapping.values():
            column_mapping[col] = 'Set'
        elif ('N/D' in col_str or 'DAY' in col_str or 'NIGHT' in col_str) and 'DAY/NIGHT' not in column_mapping.values():
            column_mapping[col] = 'DAY/NIGHT'
        elif ('CAST' in col_str or 'KARAKTER' in col_str) and 'Karakter' not in column_mapping.values():
            column_mapping[col] = 'Karakter'
        elif 'PROP' in col_str and 'Properti Utama' not in column_mapping.values():
            column_mapping[col] = 'Properti Utama'
        elif ('PAGE' in col_str or 'ESTIMATION' in col_str or 'DURASI' in col_str) and 'Estimasi Durasi' not in column_mapping.values():
            column_mapping[col] = 'Estimasi Durasi'
            
    df = df.rename(columns=column_mapping)
    
    # Ensure standard columns exist as Series
    for col_name in ['Scene', 'INT/EXT', 'Set', 'DAY/NIGHT', 'Karakter', 'Properti Utama', 'Estimasi Durasi', 'Hari Syuting', 'Kategori_Set']:
        if col_name not in df.columns:
            df[col_name] = 'N/A'
        else:
            # If accidentally duplicated as DataFrame, take the first column
            if isinstance(df[col_name], pd.DataFrame):
                df[col_name] = df[col_name].iloc[:, 0]
            df[col_name] = df[col_name].astype(str).str.strip()
            
    df = df[df['Scene'].notna() & (df['Scene'].str.upper() != 'SECTION')].reset_index(drop=True)
    df['Durasi_Float'] = df['Estimasi Durasi'].apply(parse_pages)
    df['INT/EXT'] = df['INT/EXT'].str.upper()
    df['DAY/NIGHT'] = df['DAY/NIGHT'].str.upper()
    return df

df = load_data()

st.sidebar.header("?? Filter Produksi")

all_hari = sorted(df['Hari Syuting'].unique().tolist())
selected_hari = st.sidebar.multiselect("Pilih Hari Syuting:", options=all_hari, default=[])

all_dn = sorted(df['DAY/NIGHT'].dropna().unique().tolist())
selected_dn = st.sidebar.multiselect("Pilih Day / Night:", options=all_dn, default=[])

all_set = sorted(df['Set'].dropna().unique().tolist())
selected_set = st.sidebar.multiselect("Pilih Lokasi / Set:", options=all_set, default=[])

all_chars_raw = df['Karakter'].dropna().astype(str).str.split(',').tolist()
all_chars = sorted(list(set([c.strip() for sublist in all_chars_raw for c in sublist if c.strip() and c.strip().upper() != 'TIDAK ADA'])))
selected_karakter = st.sidebar.multiselect("Pilih Karakter / Cast:", options=all_chars, default=[])

filtered_df = df.copy()
if selected_hari:
    filtered_df = filtered_df[filtered_df['Hari Syuting'].isin(selected_hari)]
if selected_dn:
    filtered_df = filtered_df[filtered_df['DAY/NIGHT'].isin(selected_dn)]
if selected_set:
    filtered_df = filtered_df[filtered_df['Set'].isin(selected_set)]
if selected_karakter:
    filtered_df = filtered_df[filtered_df['Karakter'].apply(lambda x: any(char in str(x) for char in selected_karakter))]

st.title("?? Production Dashboard & Script Breakdown")
st.markdown("Analisis durasi, sebaran set, dan rasio scene harian/interior untuk persiapan Master Schedule.")

total_scenes = len(filtered_df)
total_sets = filtered_df['Set'].nunique()
total_pages = filtered_df['Durasi_Float'].sum()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Scene", value=f"{total_scenes} Adegan", delta=f"Durasi: {total_pages:.2f} Hal")
with col2:
    st.metric(label="Jumlah Set", value=f"{total_sets} Set")
with col3:
    st.metric(label="Total Karakter Terlibat", value=f"{len(all_chars)} Pemeran")

st.markdown("---")
col_chart1, col_chart2 = st.columns(2)

hari_label = ", ".join(selected_hari) if selected_hari else "Semua Hari"

with col_chart1:
    st.subheader(f"Total Lokasi/Set {hari_label}")
    if not filtered_df.empty:
        set_counts = filtered_df['Set'].value_counts().reset_index()
        set_counts.columns = ['Set', 'Jumlah Scene']
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=set_counts.head(10), x='Jumlah Scene', y='Set', palette='Blues_r', ax=ax)
        ax.set_title(f"Top Set Paling Sering Digunakan ({hari_label})", fontsize=12, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#1f2937')
        st.pyplot(fig)

with col_chart2:
    st.subheader("Perbandingan INT vs EXT & DAY vs NIGHT")
    if not filtered_df.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        ie_counts = filtered_df['INT/EXT'].value_counts()
        ax1.pie(ie_counts, labels=ie_counts.index, autopct='%1.1f%%', colors=['#3b82f6', '#10b981', '#f59e0b'], startangle=90, textprops={'color':'white'})
        ax1.set_title("Rasio INT vs EXT", fontsize=11, fontweight='bold', color='white')
        dn_counts = filtered_df['DAY/NIGHT'].value_counts()
        ax2.pie(dn_counts, labels=dn_counts.index, autopct='%1.1f%%', colors=['#8b5cf6', '#ec4899', '#6366f1'], startangle=90, textprops={'color':'white'})
        ax2.set_title("Rasio DAY vs NIGHT", fontsize=11, fontweight='bold', color='white')
        fig.patch.set_facecolor('#0e1117')
        st.pyplot(fig)

st.markdown("---")

table_title = f"Schedule {hari_label}"
st.subheader(f"?? {table_title}")

display_df = filtered_df[['Kategori_Set', 'Hari Syuting', 'Scene', 'INT/EXT', 'Set', 'DAY/NIGHT', 'Karakter', 'Properti Utama', 'Estimasi Durasi']].copy()
st.dataframe(display_df, use_container_width=True)