import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime

sns.set(style='dark')

@st.cache_data
def load_data():
    day_df = pd.read_csv('dashboard/day_data.csv')
    hour_df = pd.read_csv('dashboard/hour_data.csv')
    return day_df, hour_df

day_df, hour_df = load_data()

# Konversi kolom tanggal menjadi datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

st.title("Dashboard Peminjaman Sepeda")

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Pilih rentang tanggal
    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    start_date, end_date = st.date_input(
        "Pilih Rentang Tanggal",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # Filter data berdasarkan rentang tanggal
    filtered_day_df = day_df[(day_df['dteday'].dt.date >= start_date) & (day_df['dteday'].dt.date <= end_date)]
    filtered_hour_df = hour_df[(hour_df['dteday'].dt.date >= start_date) & (hour_df['dteday'].dt.date <= end_date)]

tab1, tab2 = st.tabs(["Registered dan Tidak", "Cuaca dan Waktu"])

FIGSIZE = (10, 6)

# Tab 1: Analisis Hari Kerja
with tab1:
    st.header("Perbedaan Peminjam Terdaftar dan Tidak Terdaftar di Hari Kerja")
    st.write("Pada hari kerja, lebih banyak orang yang meminjam sepeda sudah terdaftar dibandingkan dengan yang belum terdaftar. Hal ini menunjukkan bahwa pengguna yang rutin menggunakan layanan sepeda cenderung memiliki akun terdaftar.")

    working_days = filtered_day_df[filtered_day_df['workingday'] == 1]
    
    if not working_days.empty:
        total_registered = working_days['registered'].sum()
        total_casual = working_days['casual'].sum()

        # Pie Chart
        labels = ['Registered', 'Casual']
        sizes = [total_registered, total_casual]
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(
            sizes,
            labels=[f"{label} ({size / sum(sizes) * 100:.2f}%)" for label, size in zip(labels, sizes)],
            startangle=140,
            colors=['lightblue', 'orange'],
            wedgeprops={'width': 0.4}
        )
        ax1.set_title('Perbandingan Peminjam Sepeda (Hari Kerja)')
        st.pyplot(fig1)

        # Grafik Tren Peminjaman
        st.header("Tren Peminjaman Sepeda di Hari Kerja")
        fig2, ax2 = plt.subplots(figsize=(14, 7))
        for col, color, label in zip(["registered", "casual"], ["blue", "orange"], ["Registered", "Casual"]):
            sns.lineplot(
                x=working_days['dteday'],
                y=working_days[col],
                label=label,
                color=color,
                marker='o',
                linestyle='-',
                ax=ax2
            )

        ax2.set_title("Tren Peminjam Sepeda (Hari Kerja)")
        ax2.set_xlabel("Tanggal")
        ax2.set_ylabel("Jumlah Peminjam")
        ax2.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax2.grid(True, linestyle="--", alpha=0.7)
        st.pyplot(fig2)
    else:
        st.warning("Tidak ada data peminjaman untuk rentang tanggal yang dipilih.")

# Tab 2: Analisis Cuaca dan Waktu
with tab2:
    st.header("Perbandingan Waktu Matahari Terbit/Terbenam dengan Peminjaman")
    st.write("Pada perbandingan waktu matahari terbit dan terbenam, terlihat bahwa lebih banyak orang meminjam sepeda pada sore hari dibandingkan waktu lainnya. Hal ini menunjukkan bahwa sore hari merupakan waktu favorit bagi pengguna sepeda.")


    # Menentukan Cluster Waktu
    def get_time_cluster(hr):
        return (
            "Sunrise" if 5 <= hr <= 7 else
            "Daytime" if 8 <= hr <= 15 else
            "Sunset" if 16 <= hr <= 19 else
            "Night"
        )

    if not filtered_hour_df.empty:
        filtered_hour_df["time_cluster"] = filtered_hour_df["hr"].apply(get_time_cluster)
        time_cluster_analysis = filtered_hour_df.groupby("time_cluster")["cnt"].mean().reset_index()

        order = ["Night", "Sunrise", "Daytime", "Sunset"]
        time_cluster_analysis["time_cluster"] = pd.Categorical(time_cluster_analysis["time_cluster"], categories=order, ordered=True)
        time_cluster_analysis = time_cluster_analysis.sort_values("time_cluster")

        # Bar Chart
        fig3, ax3 = plt.subplots(figsize=FIGSIZE)
        sns.barplot(
            x="time_cluster", y="cnt", data=time_cluster_analysis,
            palette="viridis", ax=ax3
        )
        ax3.set_title("Rata-rata Peminjaman Sepeda Berdasarkan Waktu")
        ax3.set_xlabel("Cluster Waktu")
        ax3.set_ylabel("Rata-rata Peminjaman")
        st.pyplot(fig3)

        # Line Chart
        fig4, ax4 = plt.subplots(figsize=FIGSIZE)
        sns.lineplot(
            x="time_cluster", y="cnt", data=time_cluster_analysis,
            marker="o", color="b", ax=ax4
        )
        ax4.set_title("Perbandingan Peminjaman Sepeda Berdasarkan Waktu")
        ax4.set_xlabel("Waktu")
        ax4.set_ylabel("Rata-rata Peminjaman")
        ax4.grid(True)
        st.pyplot(fig4)

        st.title("Pengaruh Kondisi Cuaca terhadap Peminjaman Sepeda")
        st.write("Kondisi cuaca sangat berpengaruh terhadap jumlah peminjaman sepeda. Orang sangat jarang meminjam sepeda saat hujan dibandingkan saat cuaca cerah.")

        weather_labels = {1: "Cerah", 2: "Mendung", 3: "Hujan Ringan", 4: "Hujan Lebat"}
        filtered_day_df["weather_label"] = filtered_day_df["weathersit"].map(weather_labels)

        # Scatter Plot
        fig5, ax5 = plt.subplots(figsize=FIGSIZE)
        ax5.scatter(filtered_day_df["weathersit"], filtered_day_df["cnt"], alpha=0.5, color="#FFA726")
        ax5.set_xticks([1, 2, 3, 4])
        ax5.set_xticklabels(["Cerah", "Mendung", "Hujan Ringan", "Hujan Lebat"])
        ax5.set_xlabel("Kondisi Cuaca")
        ax5.set_ylabel("Jumlah Peminjaman Sepeda")
        ax5.set_title("Scatter Plot: Kondisi Cuaca vs. Peminjaman Sepeda")
        st.pyplot(fig5)

        fig6, ax6 = plt.subplots(figsize=FIGSIZE)
        sns.lineplot(
            x=filtered_day_df["temp"], y=filtered_day_df["cnt"],
            hue=filtered_day_df["weather_label"],
            palette="coolwarm", linewidth=2, ax=ax6
        )
        ax6.set_xlabel("Suhu")
        ax6.set_ylabel("Jumlah Peminjaman Sepeda")
        ax6.set_title("Tren Peminjaman Sepeda Berdasarkan Suhu dan Cuaca")
        ax6.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig6)
    else:
        st.warning("Tidak ada data cuaca atau waktu untuk rentang tanggal yang dipilih.")
