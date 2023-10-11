# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency
sns.set(style='dark')

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Bike Sharing Dasboard",
        page_icon="🚲",
    )

    # Membuka file all_df dan membaginya per tahun
    all_df = pd.read_csv("all_data.csv")
    all_df_2011 = all_df.loc[all_df['yr'] == 0]
    all_df_2012 = all_df.loc[all_df['yr'] == 1]

    # Fungsi menampilkan total peminjaman sepeda pada hari tertentu
    def create_daily_orders_df(df):
        daily_orders_df = df.resample(rule='D, on='dteday').agg({
            "instant": "nunique",
            "cnt": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        # daily_orders_df.rename(columns={
        #     "total_price": "revenue"
        # }, inplace=True)
        
        return daily_orders_df

    #Fungsi menampilkan perbandingan antara pelanggan tipe casual dan registered
    def create_daily_comparation_df(df):
        daily_comparation_df = df.resample(rule='D', on='dteday').agg({
            "instant": "nunique",
            "casual": "sum",
            "registered": "sum",
            "cnt" : "sum"
        })
        daily_comparation_df = daily_comparation_df.reset_index()
        daily_comparation_df.rename(columns={
            "casual": "Casual",
            "registered": "Registered",
            "cnt" : "Count"
        }, inplace=True)
        return daily_comparation_df

    def create_daily_weather_df(df):
        weather_dict = {1:'Clear', 
                        2:"Mist + Cloudy", 
                        3:"Light Snow, Light Rain", 
                        4:"Heavy Rain, Snow"}
        byweather_df = df.groupby(by='weathersit', as_index=False).cnt.sum()
        byweather_df = byweather_df.replace({"weathersit":weather_dict})
        return byweather_df

    #Mengubah kolom dteday menjadi tipe data datetime
    all_df['dteday'] = pd.to_datetime(all_df['dteday'])
    min_date = all_df["dteday"].min()
    max_date = all_df["dteday"].max()

    #membuat side bar dengan isi logo perusahaan dan rentang waktu yang dipilih
    with st.sidebar:
        # Menambahkan logo perusahaan
        st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
        
        # Mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label='Rentang Waktu',min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

        st.text("Dwi Aji Prasetyo")
        st.text("Dicoding Id : dwiaji_prstyo")

    #data baru yang berada pada rentang waktu dipilih
    main_df = all_df[(all_df["dteday"] >= str(start_date)) &
                    (all_df["dteday"] <= str(end_date))]


    daily_orders_df = create_daily_orders_df(main_df)
    daily_comparation_df = create_daily_comparation_df(main_df)
    byweather_df = create_daily_weather_df(main_df)

    st.title('Bike Sharing Dashboard')

    st.subheader('Peminjaman Sepeda pada Rentang Waktu Tertentu')
    col1, col2 = st.columns(2)

    with col1:
        total_peminjam = daily_orders_df.cnt.sum()
        st.metric("Total Peminjaman Sepeda", value=total_peminjam,delta=int(daily_orders_df.cnt.values[-1]-daily_orders_df.cnt.values[-2]))

    with col2:
        rentang_waktu = daily_orders_df.instant.sum()
        st.metric("Rentang Waktu", value=str(rentang_waktu)+' Hari')

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["dteday"],
        daily_orders_df["cnt"],
        marker='o',
        linewidth=2,
        color="green"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col2:
        casual_cust = daily_comparation_df.Casual.sum()
        st.metric("Peminjam Casual", value=casual_cust)

    with col1:
        registered_cust = daily_comparation_df.Registered.sum()
        st.metric("Peminjam Registered", value=registered_cust)



    fig, ax = plt.subplots(figsize=(10, 10))
    explode = (0,0.1)
    ax.pie([casual_cust,registered_cust],
          explode=explode,
            labels=["Casual","Registered"],
          autopct='%1.1f%%',
          textprops={'fontsize': 30},
          )
    plt.title("Perbandingan Peminjam Tipe Registered vs Casual",fontsize=30)
    st.pyplot(fig)

    #Horizontal Bar Chart
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#90CAF9"]
    colors[len(byweather_df["weathersit"])-1]="#90CAF9"
    sns.barplot(
        x="cnt",
        y="weathersit",
        data=byweather_df.sort_values(by="cnt", ascending=False),
        #palette= colors,
        ax=ax
    )
    ax.bar_label(ax.containers[0])
    ax.set_title("Peminjam sepeda berdasarkan cuaca yang sedang berlangsung", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

    tab1, tab2 = st.tabs(["Tahun 2011", "Tahun 2012"])
    with tab1:
        st.subheader("Persebaran Jenis Pelanggan pada tahun 2011")
        
        musim = ('springer', 'summer', 'fall','winter')
        Casual_season_2011 = all_df_2011.groupby(by="season").casual.sum()
        Registered_season_2011 = all_df_2011.groupby(by="season").registered.sum()
        col1, col2 = st.columns(2)
        with col1:
        #st.text("Persebaran jenis pelanggan per musim pada tahun 2011")
            fig, ax = plt.subplots()
            X1_axis = np.arange(len(musim))

            ax.bar(X1_axis+0.2, Casual_season_2011, 0.5, label = 'Casual')
            ax.bar(X1_axis-0.2, Registered_season_2011,0.5, label = 'Registered')

            ax.set_xticks(X1_axis, musim)
            ax.set_xlabel("Musim")
            ax.set_ylabel("Banyak Sepeda Dipinjam")
            ax.legend()
            st.pyplot(fig)
        
        #st.subheader("Perkembangan Pelanggan per bulan pada tahun 2011")
        bulan = ('Januari', 'Februari', 'Maret','April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember')
        Casual_month_2011 = all_df_2011.groupby(by="mnth").casual.sum()
        Registered_month_2011 = all_df_2011.groupby(by="mnth").registered.sum()
        Count_month_2011 = all_df_2011.groupby(by="mnth").cnt.sum()
        
        with col2:
            fig, ax = plt.subplots()
            X2_axis = np.arange(len(bulan))
            ax.plot(X2_axis, Casual_month_2011, marker='o', linewidth=2, label = 'casual')
            ax.plot(X2_axis, Registered_month_2011, marker='o', linewidth=2, label = 'registered')
            ax.plot(X2_axis, Count_month_2011, marker='o', linewidth=2, label = 'Total')

            ax.grid()
            ax.set_xticks(X2_axis, bulan, rotation=45)
            ax.set_xlabel("Bulan")
            ax.set_ylabel("Banyak Sepeda Dipinjam")
            #plt.title("Perkembangan jenis pelanggan per bulan pada tahun 2011")
            plt.legend()
            st.pyplot(fig)

    with tab2:
        st.subheader("Persebaran Jenis Pelanggan pada tahun 2012")
        
        musim = ('springer', 'summer', 'fall','winter')
        Casual_season_2012 = all_df_2012.groupby(by="season").casual.sum()
        Registered_season_2012 = all_df_2012.groupby(by="season").registered.sum()
        col1a, col2a = st.columns(2)
        with col1a:
            fig, ax = plt.subplots()
            X1_axis = np.arange(len(musim))

            ax.bar(X1_axis+0.2, Casual_season_2012, 0.5, label = 'Casual')
            ax.bar(X1_axis-0.2, Registered_season_2012,0.5, label = 'Registered')

            ax.set_xticks(X1_axis, musim)
            ax.set_xlabel("Musim")
            ax.set_ylabel("Banyak Sepeda Dipinjam")
            ax.legend()
            st.pyplot(fig)
        
        #st.subheader("Perkembangan Pelanggan per bulan pada tahun 2012")
        bulan = ('Januari', 'Februari', 'Maret','April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember')
        Casual_month_2012 = all_df_2012.groupby(by="mnth").casual.sum()
        Registered_month_2012 = all_df_2012.groupby(by="mnth").registered.sum()
        Count_month_2012 = all_df_2012.groupby(by="mnth").cnt.sum()
        
        with col2a:
            fig, ax = plt.subplots()
            X2_axis = np.arange(len(bulan))
            ax.plot(X2_axis, Casual_month_2012, marker='o', linewidth=2, label = 'casual')
            ax.plot(X2_axis, Registered_month_2012, marker='o', linewidth=2, label = 'registered')
            ax.plot(X2_axis, Count_month_2012, marker='o', linewidth=2, label = 'Total')

            ax.grid()
            ax.set_xticks(X2_axis, bulan, rotation=45)
            ax.set_xlabel("Bulan")
            ax.set_ylabel("Banyak Sepeda Dipinjam")
            #plt.title("Perkembangan jenis pelanggan per bulan pada tahun 2011")
            plt.legend()
            st.pyplot(fig)

    st.caption('Dwi Aji Prasetyo | Dicoding Id : dwiaji_prstyo')

if __name__ == "__main__":
    run()
