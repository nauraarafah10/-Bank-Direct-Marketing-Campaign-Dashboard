import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Bank Marketing Campaign Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS sederhana
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Judul Dashboard
st.title("🏦 Bank Direct Marketing Campaign Dashboard")
st.markdown("Dashboard analitis untuk mengevaluasi efektivitas kampanye pemasaran deposit berjangka (*term deposit*) dan demografi nasabah.")

# 3. Fungsi Load Data dengan penanganan delimiter ';'
@st.cache_data
def load_data():
    # Karena file bank marketing menggunakan pemisah koma (,), cukup gunakan read_csv standar
    df = pd.read_csv('bank-direct-marketing-campaigns.csv')
    return df

df_raw = load_data()

# 4. Filter di Sidebar
st.sidebar.header("🔍 Filter Analytics")

job_list = df_raw['job'].unique().tolist() if 'job' in df_raw.columns else []
selected_job = st.sidebar.multiselect("Pekerjaan Nasabah:", options=job_list, default=job_list)

marital_list = df_raw['marital'].unique().tolist() if 'marital' in df_raw.columns else []
selected_marital = st.sidebar.multiselect("Status Pernikahan:", options=marital_list, default=marital_list)

contact_list = df_raw['contact'].unique().tolist() if 'contact' in df_raw.columns else []
selected_contact = st.sidebar.multiselect("Metode Kontak:", options=contact_list, default=contact_list)

# Menerapkan Filter
df_filtered = df_raw.copy()
if 'job' in df_filtered.columns and selected_job:
    df_filtered = df_filtered[df_filtered['job'].isin(selected_job)]
if 'marital' in df_filtered.columns and selected_marital:
    df_filtered = df_filtered[df_filtered['marital'].isin(selected_marital)]
if 'contact' in df_filtered.columns and selected_contact:
    df_filtered = df_filtered[df_filtered['contact'].isin(selected_contact)]

# 5. KPI Cards Utama
st.subheader("📌 Key Performance Indicators (KPI)")
col1, col2, col3, col4 = st.columns(4)

total_clients = len(df_filtered)
# Menghitung data 'yes' dengan membersihkan spasi string jika ada
if 'y' in df_filtered.columns:
    total_subscribed = (df_filtered['y'].str.strip() == 'yes').sum()
else:
    total_subscribed = 0

conversion_rate = (total_subscribed / total_clients * 100) if total_clients > 0 else 0
avg_contacts = df_filtered['campaign'].mean() if 'campaign' in df_filtered.columns and total_clients > 0 else 0

col1.metric("👥 Total Nasabah Dikontak", f"{total_clients:,}")
col2.metric("✅ Berhasil Berlangganan (Yes)", f"{total_subscribed:,}")
col3.metric("🎯 Rate Konversi (Conversion Rate)", f"{conversion_rate:.2f}%")
col4.metric("📞 Rata-rata Kontak / Nasabah", f"{avg_contacts:.1f}x")

st.markdown("---")

# 6. Tab Visualisasi & Analisis
tab1, tab2, tab3 = st.tabs(["📊 Performa Kampanye", "👥 Analisis Demografi", "📈 Indikator Ekonomi & Data"])

with tab1:
    st.subheader("Analisis Hasil Kampanye Pemasaran")
    c1, c2 = st.columns(2)

    with c1:
        if 'job' in df_filtered.columns and 'y' in df_filtered.columns:
            temp_df = df_filtered.copy()
            temp_df['y_clean'] = temp_df['y'].str.strip()
            job_conv = temp_df.groupby('job')['y_clean'].apply(lambda x: (x == 'yes').mean() * 100).reset_index()
            job_conv.columns = ['Job', 'Conversion Rate (%)']
            job_conv = job_conv.sort_values('Conversion Rate (%)', ascending=True)
            
            fig_job = px.bar(
                job_conv, x='Conversion Rate (%)', y='Job', orientation='h',
                title="Tingkat Keberhasilan (%) Berdasarkan Pekerjaan",
                color='Conversion Rate (%)', color_continuous_scale='Blues',
                text_auto='.1f'
            )
            st.plotly_chart(fig_job, use_container_width=True)

    with c2:
        if 'month' in df_filtered.columns and 'y' in df_filtered.columns:
            month_order = ['mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            temp_df = df_filtered.copy()
            temp_df['y_clean'] = temp_df['y'].str.strip()
            month_conv = temp_df.groupby('month')['y_clean'].apply(lambda x: (x == 'yes').mean() * 100).reset_index()
            month_conv.columns = ['Month', 'Conversion Rate (%)']
            month_conv['Month'] = pd.Categorical(month_conv['Month'], categories=month_order, ordered=True)
            month_conv = month_conv.sort_values('Month')

            fig_month = px.line(
                month_conv, x='Month', y='Conversion Rate (%)',
                title="Tren Tingkat Konversi per Bulan Kampanye",
                markers=True, line_shape='spline'
            )
            st.plotly_chart(fig_month, use_container_width=True)

with tab2:
    st.subheader("Profil Demografi Nasabah")
    d1, d2 = st.columns(2)

    with d1:
        if 'y' in df_filtered.columns:
            temp_df = df_filtered.copy()
            temp_df['Subscribed'] = temp_df['y'].str.strip()
            y_counts = temp_df['Subscribed'].value_counts().reset_index()
            y_counts.columns = ['Subscribed', 'Count']
            
            fig_pie = px.pie(
                y_counts, values='Count', names='Subscribed',
                title="Proporsi Hasil Kampanye (Yes vs No)",
                hole=0.4, color='Subscribed',
                color_discrete_map={'yes': '#2ca02c', 'no': '#d62728'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with d2:
        if 'age' in df_filtered.columns and 'y' in df_filtered.columns:
            temp_df = df_filtered.copy()
            temp_df['y_clean'] = temp_df['y'].str.strip()
            fig_age = px.histogram(
                temp_df, x='age', color='y_clean',
                title="Distribusi Usia Nasabah berdasarkan Respon Kampanye",
                barmode='overlay', nbins=20,
                color_discrete_map={'yes': '#2ca02c', 'no': '#d62728'}
            )
            fig_age.update_layout(xaxis_title="Usia", yaxis_title="Jumlah Nasabah")
            st.plotly_chart(fig_age, use_container_width=True)

with tab3:
    st.subheader("💡 Analisis Pengaruh Ekonomi Makro")
    e1, e2 = st.columns(2)
    
    with e1:
        if 'euribor3m' in df_filtered.columns and 'y' in df_filtered.columns:
            temp_df = df_filtered.copy()
            temp_df['y_clean'] = temp_df['y'].str.strip()
            fig_euribor = px.box(
                temp_df, x='y_clean', y='euribor3m', color='y_clean',
                title="Pengaruh Suku Bunga (Euribor 3M) Terhadap Respon",
                labels={'euribor3m': 'Suku Bunga Euribor 3 Bulan', 'y_clean': 'Berlangganan?'},
                color_discrete_map={'yes': '#2ca02c', 'no': '#d62728'}
            )
            st.plotly_chart(fig_euribor, use_container_width=True)

    with e2:
        if 'cons.conf.idx' in df_filtered.columns and 'y' in df_filtered.columns:
            temp_df = df_filtered.copy()
            temp_df['y_clean'] = temp_df['y'].str.strip()
            fig_conf = px.box(
                temp_df, x='y_clean', y='cons.conf.idx', color='y_clean',
                title="Indeks Kepercayaan Konsumen vs Respon",
                labels={'cons.conf.idx': 'Indeks Kepercayaan Konsumen', 'y_clean': 'Berlangganan?'},
                color_discrete_map={'yes': '#2ca02c', 'no': '#d62728'}
            )
            st.plotly_chart(fig_conf, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Eksplorasi Data Terfilter")
    st.dataframe(df_filtered, use_container_width=True)

    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Terfilter (CSV)",
        data=csv_data,
        file_name="bank_marketing_filtered.csv",
        mime="text/csv"
    )