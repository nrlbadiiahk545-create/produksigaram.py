import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Dashboard Produksi Garam Indonesia",
    page_icon="🧂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS MODERN OCEAN PURPLE
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght=300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #071021;
        color: white;
    }

    .main {
        background: linear-gradient(180deg, #071021 0%, #0f172a 100%);
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    /* METRIC CARD */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #16213e, #1b1f4b);
        border: 1px solid #7c3aed;
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(124,58,237,0.25);
    }

    [data-testid="stMetricValue"] {
        color: #c084fc;
        font-size: 28px;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #ffffff;
        font-weight: 600;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#0f172a,#111827);
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1e1b4b;
        border-radius: 10px 10px 0px 0px;
        padding: 12px 20px;
        color: white;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #7c3aed !important;
        border-bottom: 4px solid #c084fc !important;
    }

    /* TABLE */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("garam.csv")

    # Pastikan kolom tahun bertipe integer awal sebelum manipulasi lanjutan
    df['tahun'] = df['tahun'].astype(int)
    
    # Bersihkan data teks
    df['provinsi'] = df['provinsi'].str.title()
    df['kabupaten_kota'] = df['kabupaten_kota'].str.title()

    # Hitung produktivitas
    df['produktivitas_ton_per_ha'] = (
        df['volume'] / df['luas_lahan_ha']
    ).fillna(0) # Mengatasi pembagian dengan nol jika luas lahan 0.0

    return df

df = load_data()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("""
<h2 style='text-align: center;
color: #c084fc;
font-weight: 700;'>
🦈 Marine Salt Analytics
</h2>
""", unsafe_allow_html=True)

    st.title("🧂 Dashboard Garam")
    st.markdown("Analisis Produksi Garam Nasional Indonesia")

    st.divider()

    # FILTER TAHUN
    tahun_filter = st.multiselect(
        "📅 Pilih Tahun",
        options=sorted(df['tahun'].unique()),
        default=sorted(df['tahun'].unique())
    )

    # FILTER PROVINSI
    provinsi_filter = st.multiselect(
        "🌏 Pilih Provinsi",
        options=sorted(df['provinsi'].unique()),
        default=sorted(df['provinsi'].unique())
    )

    # FILTER KABUPATEN
    kabupaten_filter = st.multiselect(
        "🏙️ Pilih Kabupaten/Kota",
        options=sorted(df['kabupaten_kota'].unique()),
        default=sorted(df['kabupaten_kota'].unique())
    )

    st.divider()

    produktif_only = st.toggle(
        "Tampilkan Produktivitas Tinggi Saja",
        value=False
    )

# =========================================================
# FILTER DATA
# =========================================================
filtered_df = df[
    (df['tahun'].isin(tahun_filter)) &
    (df['provinsi'].isin(provinsi_filter)) &
    (df['kabupaten_kota'].isin(kabupaten_filter))
]

if produktif_only:
    filtered_df = filtered_df[
        filtered_df['produktivitas_ton_per_ha'] >=
        filtered_df['produktivitas_ton_per_ha'].mean()
    ]

# =========================================================
# HEADER
# =========================================================
st.title("🌊 Dashboard Produksi Garam Indonesia")
st.markdown("""
Dashboard interaktif untuk menganalisis produksi garam nasional berdasarkan
provinsi, kabupaten/kota, luas lahan, volume produksi, dan produktivitas lahan.
""")

st.divider()

# =========================================================
# VALIDASI DATA KOSONG
# =========================================================
if filtered_df.empty:
    st.warning("⚠️ Data tidak ditemukan. Silakan ubah filter.")
else:

    # =====================================================
    # KPI CARDS
    # =====================================================
    total_produksi = filtered_df['volume'].sum()
    total_lahan = filtered_df['luas_lahan_ha'].sum()
    rata_prod = filtered_df['produktivitas_ton_per_ha'].mean()
    total_daerah = filtered_df['kabupaten_kota'].nunique()

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "🧂 Total Produksi Garam",
            f"{total_produksi:,.2f} Ton"
        )

    with k2:
        st.metric(
            "🌊 Total Luas Lahan",
            f"{total_lahan:,.2f} Ha"
        )

    with k3:
        st.metric(
            "📈 Produktivitas Rata-rata",
            f"{rata_prod:,.2f} Ton/Ha"
        )

    with k4:
        st.metric(
            "🏙️ Jumlah Kabupaten",
            f"{total_daerah}"
        )

    st.write("")

    # =====================================================
    # TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs([
        "📊 Analisis Produksi",
        "🧂 Produktivitas Lahan",
        "📋 Eksplorasi Dataset"
    ])

    # =====================================================
    # TAB 1
    # =====================================================
    with tab1:

        c1, c2 = st.columns(2)

        # BAR PROVINSI
        with c1:

            st.markdown("### 🌏 Produksi Garam per Provinsi")

            prov_df = (
                filtered_df
                .groupby('provinsi')['volume']
                .sum()
                .reset_index()
                .sort_values(by='volume', ascending=False)
            )

            fig_prov = px.bar(
                prov_df,
                x='volume',
                y='provinsi',
                orientation='h',
                color='volume',
                color_continuous_scale='purples'
            )

            fig_prov.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )

            st.plotly_chart(fig_prov, use_container_width=True)

        # PIE CHART
        with c2:

            st.markdown("### 🧂 Distribusi Produksi Nasional")

            pie_df = (
                filtered_df
                .groupby('provinsi')['volume']
                .sum()
                .reset_index()
            )

            fig_pie = px.pie(
                pie_df,
                values='volume',
                names='provinsi',
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )

            fig_pie.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )

            st.plotly_chart(fig_pie, use_container_width=True)

        st.write("---")

        # TREND PRODUKSI
        st.markdown("### 📈 Tren Produksi Garam Nasional")

        trend_df = (
            filtered_df
            .groupby('tahun')['volume']
            .sum()
            .reset_index()
        )

        fig_line = px.line(
            trend_df,
            x='tahun',
            y='volume',
            markers=True,
            color_discrete_sequence=['#c084fc']
        )

        # 🔧 PERBAIKAN SUMBU X DI SINI (Menghilangkan desimal seperti 2,024.5 dan koma ribuan)
        fig_line.update_xaxes(
            tickformat="d",  # Format "d" merepresentasikan integer murni tanpa koma/titik ribuan
            dtick=1          # Jarak interval sumbu X dibuat per 1 tahun penuh
        )

        fig_line.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig_line, use_container_width=True)

    # =====================================================
    # TAB 2
    # =====================================================
    with tab2:

        colA, colB = st.columns(2)

        # SCATTER
        with colA:

            st.markdown("### 🌊 Hubungan Luas Lahan dan Produksi")

            fig_scatter = px.scatter(
                filtered_df,
                x='luas_lahan_ha',
                y='volume',
                size='produktivitas_ton_per_ha',
                color='provinsi',
                hover_name='kabupaten_kota',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            fig_scatter.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

        # TOP PRODUKTIVITAS
        with colB:

            st.markdown("### 🚀 Top Produktivitas Kabupaten")

            produktif_df = (
                filtered_df
                .sort_values(
                    by='produktivitas_ton_per_ha',
                    ascending=False
                )
                .head(10)
            )

            fig_top = px.bar(
                produktif_df,
                x='produktivitas_ton_per_ha',
                y='kabupaten_kota',
                orientation='h',
                color='produktivitas_ton_per_ha',
                color_continuous_scale='magma'
            )

            fig_top.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )

            st.plotly_chart(fig_top, use_container_width=True)

        st.write("---")

        # HEATMAP
        st.markdown("### 🔥 Heatmap Produksi Garam")

        pivot_df = filtered_df.pivot_table(
            index='provinsi',
            columns='tahun',
            values='volume',
            aggfunc='sum'
        )

        fig_heat = px.imshow(
            pivot_df,
            text_auto=True,
            aspect='auto',
            color_continuous_scale='purples'
        )

        # 🔧 PERBAIKAN SUMBU X PADA HEATMAP (Menghilangkan desimal/koma jika kolom pivot bertipe numerik)
        fig_heat.update_xaxes(
            tickformat="d",
            dtick=1
        )

        fig_heat.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600
        )

        st.plotly_chart(fig_heat, use_container_width=True)

    # =====================================================
    # TAB 3
    # =====================================================
    with tab3:

        st.markdown("### 📋 Dataset Produksi Garam Lengkap")

        display_cols = [
            'tahun',
            'provinsi',
            'kabupaten_kota',
            'luas_lahan_ha',
            'volume',
            'produktivitas_ton_per_ha'
        ]

        st.dataframe(
            filtered_df[display_cols],
            column_config={
                # 🔧 PERBAIKAN FORMAT TABEL DI SINI (Mengubah format tahun dari 2,025 menjadi 2025)
                "tahun": st.column_config.NumberColumn(
                    "Tahun",
                    format="d" 
                ),
                "provinsi": st.column_config.TextColumn(
                    "Provinsi"
                ),
                "kabupaten_kota": st.column_config.TextColumn(
                    "Kabupaten/Kota"
                ),
                "luas_lahan_ha": st.column_config.NumberColumn(
                    "Luas Lahan (Ha)",
                    format="%.2f"
                ),
                "volume": st.column_config.NumberColumn(
                    "Produksi Garam (Ton)",
                    format="%.2f"
                ),
                "produktivitas_ton_per_ha": st.column_config.NumberColumn(
                    "Produktivitas",
                    format="%.2f"
                )
            },
            use_container_width=True,
            hide_index=True
        )

        # DOWNLOAD CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Dataset CSV",
            data=csv,
            file_name="hasil_produksi_garam.csv",
            mime="text/csv"
        )

# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption("""
Dashboard Produksi Garam Indonesia 
Menggunakan Python, Streamlit, dan Plotly Interactive Visualization by Kelompok 16
""")