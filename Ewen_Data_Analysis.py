import streamlit as st
import os
import pandas as pd
import plotly.express as px
import pydeck as pdk
import math

path = "C:/Users/ebern/Desktop/GitHub/Data_Visualisation/Extracted_Google_Maps_Data"
st.set_page_config(layout="wide")

year = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
year_sum = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
total_year_sum = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
month = {"JANUARY": [], "FEBRUARY": [], "MARCH": [], "APRIL": [], "MAY": [], "JUNE": [], "JULY": [], "AUGUST": [],
         "SEPTEMBER": [], "OCTOBER": [], "NOVEMBER": [], "DECEMBER": []}
year_range = []
total_data_sum = 0

for folder in os.listdir(path):
    temp_year_sum = 0
    temp_month = {"JANUARY": [], "FEBRUARY": [], "MARCH": [], "APRIL": [], "MAY": [], "JUNE": [], "JULY": [],
                  "AUGUST": [], "SEPTEMBER": [], "OCTOBER": [], "NOVEMBER": [], "DECEMBER": []}
    month_sum = {"JANUARY": [], "FEBRUARY": [], "MARCH": [], "APRIL": [], "MAY": [], "JUNE": [], "JULY": [],
                 "AUGUST": [], "SEPTEMBER": [], "OCTOBER": [], "NOVEMBER": [], "DECEMBER": []}
    for file in os.listdir(path + "/" + folder):
        for key in month:
            if key in file:
                read = pd.read_csv(path + "/" + folder + "/" + file)
                nb_data = len(read.axes[0]) * len(read.axes[1])
                total_data_sum += nb_data
                temp_year_sum += nb_data
                temp_month[key] = read
                month_sum[key] = len(read.index)
            if type(month_sum[key]) is list:
                month_sum[key] = 0
    total_year_sum[folder] = temp_year_sum
    year_sum[folder] = month_sum
    year[folder] = temp_month


def percentage(count_dict):
    return_dict = {"key": list(count_dict.keys()), "percentage": []}
    for value in list(count_dict.values()):
        return_dict['percentage'].append(value * 100 / sum(list(count_dict.values())))
    return return_dict


def columns_count(df, columns):
    count_dict = {"MOTORCYCLING": 0, "WALKING": 0, "IN_PASSENGER_VEHICLE": 0, "IN_BUS": 0, "RUNNING": 0, "CYCLING": 0,
                  "IN_TRAIN": 0, "IN_SUBWAY": 0}
    df_count = df[columns].value_counts()
    for key in list(count_dict.keys()):
        if key in df_count:
            count_dict[key] = df_count[key]
    return count_dict


def year_count(year_selection, key_month=None, separate_month=False):
    count_dict = {"MOTORCYCLING": 0, "WALKING": 0, "IN_PASSENGER_VEHICLE": 0, "IN_BUS": 0, "RUNNING": 0, "CYCLING": 0,
                  "IN_TRAIN": 0, "IN_SUBWAY": 0}
    month_dict = {}
    if separate_month is True:
        for value in key_month:
            if value in list(year[year_selection].keys()):
                month_dict = columns_count(year[year_selection][value], 'ActivityType')
                for dict_key in list(count_dict.keys()):
                    count_dict[dict_key] += month_dict[dict_key]
    else:
        for key, value in year[year_selection].items():
            if type(value) is not list:
                month_dict = columns_count(value, 'ActivityType')
                for dict_key in list(count_dict.keys()):
                    count_dict[dict_key] += month_dict[dict_key]
    return count_dict


def high_school_data_count():
    years = ['2015', '2016', '2017', '2018']
    count_dict = {"MOTORCYCLING": 0, "WALKING": 0, "IN_PASSENGER_VEHICLE": 0, "IN_BUS": 0, "RUNNING": 0, "CYCLING": 0,
                  "IN_TRAIN": 0, "IN_SUBWAY": 0}
    temp_dict = {}
    for value in years:
        if value == '2018':
            temp_dict = year_count('2018', key_month=['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY'],
                                   separate_month=True)
        else:
            temp_dict = year_count(value)
        for dict_key in list(count_dict.keys()):
            count_dict[dict_key] += temp_dict[dict_key]
    return count_dict


def university_data_count():
    years = ['2018', '2019']
    count_dict = {"MOTORCYCLING": 0, "WALKING": 0, "IN_PASSENGER_VEHICLE": 0, "IN_BUS": 0, "RUNNING": 0, "CYCLING": 0,
                  "IN_TRAIN": 0, "IN_SUBWAY": 0}
    temp_dict = {}
    for value in years:
        if value == '2018':
            temp_dict = year_count('2018', key_month=['SEPTEMBER', 'OCTOBER', 'DECEMBER'],
                                   separate_month=True)
        else:
            temp_dict = year_count(value)
        for dict_key in list(count_dict.keys()):
            count_dict[dict_key] += temp_dict[dict_key]
    return count_dict


def data_bar_plot(cols_nb, year, scale=180):
    if cols_nb > 3:
        cols_nb = 3
    cols = st.columns(cols_nb)
    i = 1
    for key_year in year:
        i = i % cols_nb
        dict = {key_year: list(year_sum[key_year].keys()), 'Number of trips': list(year_sum[key_year].values())}
        fig = px.bar(dict, x=key_year, y='Number of trips')
        fig.update_layout(yaxis_range=[0, scale])
        cols[i - 1].plotly_chart(fig, use_container_width=True)
        i += 1


def convert_loc_data(data):
    return data / (pow(10, 7))


def get_month_loc_data(df):
    dict = {"lon": [], "lat": []}
    for index, row in df.iterrows():
        if not pd.isna(row["StartLocationLat"]):
            dict["lat"].extend([convert_loc_data(row["StartLocationLat"]), convert_loc_data(row["EndLocationLat"])])
            dict["lon"].extend([convert_loc_data(row["StartLocationLon"]), convert_loc_data(row["EndLocationLon"])])
    return dict


def get_year_loc_data(year_selection, key_month=None, separate_month=False):
    loc_dict = {"lon": [], "lat": []}
    month_dict = {}
    if separate_month is True:
        for value in key_month:
            if value in list(year[year_selection].keys()):
                month_dict = get_month_loc_data(year[year_selection][value])
    else:
        for key, value in year[year_selection].items():
            if type(value) is not list:
                month_dict = get_month_loc_data(value)
    loc_dict["lon"] += month_dict["lon"]
    loc_dict["lat"] += month_dict["lat"]
    return loc_dict


def get_high_school_data():
    years = ['2015', '2016', '2017', '2018']
    loc_dict = {"lon": [], "lat": []}
    for value in years:
        if value == '2018':
            temp_dict = get_year_loc_data('2018',
                                          key_month=['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY'],
                                          separate_month=True)
        else:
            temp_dict = get_year_loc_data(value)
        loc_dict["lon"] += temp_dict["lon"]
        loc_dict["lat"] += temp_dict["lat"]
    return pd.DataFrame.from_dict(loc_dict)


def get_university_data():
    years = ['2018', '2019', '2020', '2021']
    loc_dict = {"lon": [], "lat": []}
    for value in years:
        temp_dict = get_year_loc_data(value)
        loc_dict["lon"] += temp_dict["lon"]
        loc_dict["lat"] += temp_dict["lat"]
    return pd.DataFrame.from_dict(loc_dict)


def draw_map(df):
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=48.75,
            longitude=2.26,
            zoom=13,
            pitch=50,
        ),
        layers=[
            pdk.Layer('HexagonLayer',
                      data=df,
                      get_position='[lon, lat]',
                      radius=200,
                      elevation_scale=4,
                      elevation_range=[0, 1000],
                      pickable=True,
                      extruded=True,
                      ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))


def distance_mean(years, month_list):
    temp = []
    if month_list == "all":
        month_list = list(year['2015'].keys())
    for value in years:
        if value == '2018' and month_list != "all":
            for month in month_list:
                if type(year['2018'][month]) is not list:
                    if not math.isnan(year['2018'][month]['Distance'].mean()):
                        temp.append(year['2018'][month]['Distance'].mean())
        else:
            for month in list(year[value].keys()):
                if type(year[value][month]) is not list:
                    if not math.isnan(year[value][month]['Distance'].mean()):
                        temp.append(year[value][month]['Distance'].mean())
    print(temp)
    return sum(temp) / len(temp)


def intro():
    year_range.append(list(year.keys())[0])
    year_range.append(list(year.keys())[len(list(year.keys())) - 1])

    st.title('Ewen life from {0} to {1}'.format(year_range[0], year_range[1]))
    st.write(
        "The purpose of this presentation is to show how we can know many facets of a person's life just by "
        "analyzing their personal data. For this purpose we will process and analyze my personal data, "
        "in this case my google locations datas.")
    st.write("This presentation has been designed to be dynamically updated if the data is updated.")
    st.write("Total number of location data : ", total_data_sum)
    sum_dict = {"Years": list(total_year_sum.keys()), 'Number of Datas': list(total_year_sum.values())}
    st.plotly_chart(px.bar(sum_dict, x="Years", y='Number of Datas'), use_container_width=True)


def high_school_part():
    st.title("High School years")
    st.write(
        "Data location has been collected since August 2015, date of purchase of a phone running recent version of "
        "android (android 5). Before December 2017 we notice that few data have been collected.This is explained by "
        "the fact that I had at the time a phone plan with little data package (50mo) forcing me to disable the "
        "location the vast majority of the time.")
    st.write(
        "From December 2017, all trips have been recorded, thanks to a new phone and a new phone plan, allowing "
        "me to keep the location active all time ")
    data_bar_plot(2, ["2015", "2016", "2017", "2018"])
    st.write(
        "We notice that the point on the map where I went the most during these years is obviously my house in Antony "
        "in the 92 department. The second most frequented point is my high school located in Chatenay-Malabry")
    st.write(
        "As I didn't have a driver's license yet, I mostly traveled on foot or by bike. It is noticeable that "
        "my trips remained within a rather small radius")
    draw_map(get_high_school_data())
    dict_temp = high_school_data_count()
    fig = px.pie(values=list(dict_temp.values()),
                 names=['MOTORCYCLING', 'WALKING', 'CAR', 'BUS', 'RUNNING', 'CYCLING', 'TRAIN', 'SUBWAY'],
                 title="Type of transportation used during my trips in 2015 / 2016 / 2017 / 2018 (in percent): ")
    st.write(
        "As I didn't have a driver's license yet, I did most of my travelling on foot or by bike. There are still a "
        "lot of car trips, my mother taking me every morning to school and doing supervized driving.")
    st.plotly_chart(fig, use_container_width=True)


def university_part():
    st.title("University Years")
    st.write(
        "In late 2018, I graduated from high school as well as my driver's license. I joined Efrei Paris which has "
        "deeply changed my habits.")
    st.write("I deliberately did not take the data of the years 2020 and 2021 in this section because of the Covid "
             "pandemic which drastically changed the habits of everyone. ")
    dict_temp = university_data_count()
    fig = px.pie(values=list(dict_temp.values()),
                 names=['MOTORCYCLING', 'WALKING', 'CAR', 'BUS', 'RUNNING', 'CYCLING', 'TRAIN', 'SUBWAY'],
                 title="Type of transportation used during my trips in late 2018 / 2019 (in percent): ")
    st.plotly_chart(fig, use_container_width=True)
    st.write(
        "Going to Efrei located in Villejuif, we notice a clear increase in public transport (bus, train and subway) "
        "as well as car journeys, having now the driving licence. There has also been a net decrease in the number of "
        "trips by bicycle and on foot. ")
    data_bar_plot(2, ["2018", "2019"], scale=380)
    st.write("Since my arrival at the university, there has been an increase in the number of trips. There is no data "
             "in August and little in September 2018, having broken my phone. ")
    draw_map(get_university_data())
    st.write("My places of travel remain however almost the same, my friends still living in the same places. You can "
             "see a line going from my house to the school. This line represents the trip by bus + rer B that I make "
             "every morning and every evening to go to school.")


intro()
high_school_part()
university_part()

st.write("Average distance travelled per trip in meters :      Before August 2018",
         int(distance_mean(['2017', '2018'], ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY'])),
         "After August 2018:", int(distance_mean(['2018', '2019'],
                                             ['AUGUST', "SEPTEMBER", "OCTOBER", 'NOVEMBER', 'DECEMBER'])))

#st.write(distance_mean(['2018', '2019'], ['AUGUST', "SEPTEMBER", "OCTOBER", 'NOVEMBER', 'DECEMBER']))
#st.write(year['2020']['APRIL']["Distance"].mean())

draw_map(pd.DataFrame.from_dict(get_month_loc_data(year['2020']['APRIL'])))
