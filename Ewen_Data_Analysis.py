import streamlit as st
import seaborn as sns
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import pydeck as pdk

path = "C:/Users/ebern/Desktop/GitHub/Data_Visualisation/Extracted_Google_Maps_Data"

year = {"2015" : None, "2016" : None, "2017" : None, "2018" : None, "2019" : None, "2020" : None, "2021" : None}
month = {"JANUARY" : [], "FEBRUARY" : [], "MARCH" : [], "APRIL" : [], "MAY" : [], "JUNE" : [], "JULY" : [], "AUGUST" : [], "SEPTEMBER" : [], "OCTOBER" : [], "NOVEMBER" : [], "DECEMBER" : []}
year_range = []
year_list = []

for folder in os.listdir(path):
    month = {"JANUARY" : [], "FEBRUARY" : [], "MARCH" : [], "APRIL" : [], "MAY" : [], "JUNE" : [], "JULY" : [], "AUGUST" : [], "SEPTEMBER" : [], "OCTOBER" : [], "NOVEMBER" : [], "DECEMBER" : []}
    temp = []
    for file in os.listdir(path + "/" + folder):
        for key in month:
            if key in file:
                month[key] = pd.read_csv(path + "/" + folder + "/" + file)
                temp.append(pd.read_csv(path + "/" + folder + "/" + file))
    year[folder] = month
    year_list.append(temp)

def data_bar_plot():
    cols = st.columns(3)
    i = 1
    for key_year, val_year in year.items():
        fig, axs = plt.subplots()
        month_sum = {"JANUARY" : [], "FEBRUARY" : [], "MARCH" : [], "APRIL" : [], "MAY" : [], "JUNE" : [], "JULY" : [], "AUGUST" : [], "SEPTEMBER" : [], "OCTOBER" : [], "NOVEMBER" : [], "DECEMBER" : []}
        i = i % 3
        for key, value in val_year.items():
            val_sum = 0
            val_sum += len(value)
            month_sum[key] = val_sum
        dict = {key_year : list(month_sum.keys()), 'Number of trips': list(month_sum.values())}
        fig = px.bar(dict, x=key_year, y= 'Number of trips')
        cols[i - 1].plotly_chart(fig, use_container_width=True)
        i += 1

def convert_loc_data(data):
    return data / (pow(10, 7))

def get_month_loc_data(df):
    dict = {"lon" : [], "lat" : []}
    for index, row in df.iterrows():
        if not pd.isna(row["StartLocationLat"]):
            dict["lat"].extend([convert_loc_data(row["StartLocationLat"]), convert_loc_data(row["EndLocationLat"])])
            dict["lon"].extend([convert_loc_data(row["StartLocationLon"]), convert_loc_data(row["EndLocationLon"])])
    return dict

def get_year_loc_data(year_selection, key_month=None, separate_month=False):
    dict = {"lon": [], "lat": []}
    #print(year[year_selection].items())
    if separate_month is True:
        for value in key_month:
            if value in list(year[year_selection].keys()):
                month_dict = get_month_loc_data(year[year_selection][value])
                dict["lon"] += month_dict["lon"]
                dict["lat"] += month_dict["lat"]
    else:
        for key, value in year[year_selection].items():
            if type(value) is not list:
                month_dict = get_month_loc_data(value)
                dict["lon"] += month_dict["lon"]
                dict["lat"] += month_dict["lat"]
    return pd.DataFrame.from_dict(dict)

def draw_map(df):
    st.write(df)
    st.pydeck_chart(pdk.Deck(
        map_style = 'mapbox://styles/mapbox/light-v9',
        initial_view_state = pdk.ViewState(
            latitude = 48.75,
            longitude = 2.26,
            zoom = 13,
            pitch = 50,
        ),
        layers = [
            pdk.Layer('HexagonLayer',
                data = df,
                get_position = '[lon, lat]',
                radius = 200,
                elevation_scale = 4,
                elevation_range = [0, 1000],
                pickable = True,
                extruded = True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data = df,
                get_position = '[lon, lat]',
                get_color = '[200, 30, 0, 160]',
                get_radius = 200,
            ),
        ],
    ))


year_range.append(list(year.keys())[0])
year_range.append(list(year.keys())[len(list(year.keys())) - 1])

st.set_page_config(layout="wide")
st.title('Ewen life from {0} to {1}'.format(year_range[0], year_range[1]))
st.text("The purpose of this presentation is to show how we can know many facets of a person's life just by analyzing their personal data.\n"
        "For this we will process and analyze my personal data. We will use google location data.")
data_bar_plot()
draw_map(get_year_loc_data("2020", key_month=["NOVEMBER"], separate_month=True))
#st.write(get_year_loc_data("2020", key_month=["SEPTEMBER"], separate_month=False))

