import time
from geopy.geocoders import Nominatim
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import pydeck as pdk
import math
from sklearn.cluster import KMeans, AgglomerativeClustering

path = "Extracted_Google_Maps_Data"
st.set_page_config(layout="wide")

app = Nominatim(user_agent="tutorial")
year = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
year_sum = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
total_year_sum = {"2015": None, "2016": None, "2017": None, "2018": None, "2019": None, "2020": None, "2021": None}
month = {"JANUARY": [], "FEBRUARY": [], "MARCH": [], "APRIL": [], "MAY": [], "JUNE": [], "JULY": [], "AUGUST": [],
         "SEPTEMBER": [], "OCTOBER": [], "NOVEMBER": [], "DECEMBER": []}
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
date_loc_dict = {'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': [], 'Saturday': [],
                 'Sunday': []}
covid_death = pd.read_csv("covid_death/covid_death_by_month.csv")
covid_death = covid_death / 300
year_range = []
total_data_sum = 0
color_count = 0
current_year = None
current_month = None

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
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        cols[i - 1].plotly_chart(fig, use_container_width=True)
        i += 1


def data_bar_plot_covid():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.write("")
    with col2:
        dict_2020 = {"2020": list(year_sum["2020"].keys()), 'Number of trips': list(year_sum["2020"].values())}
        fig = px.line(x=dict_2020["2020"], y=covid_death.values.tolist(), width=1200, color=px.Constant("Covid death"),
                      labels=dict(x="2020", color="Data"))
        fig.add_bar(x=dict_2020["2020"], y=dict_2020['Number of trips'], name="Number of trips")
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        st.plotly_chart(fig)
    with col3:
        st.write("")


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
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=pdk.ViewState(
            latitude=48.75,
            longitude=2.26,
            zoom=12,
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
        ],
    ))


def draw_ml_map(df):
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=pdk.ViewState(
            latitude=48.75,
            longitude=2.26,
            zoom=12,
            pitch=50,
        ),
        layers=[
            pdk.Layer('ColumnLayer',
                      data=df,
                      get_position='[lon, lat]',
                      get_elevation='[percentage]',
                      radius=200,
                      getFillColor= '[color_r, color_g, color_b]',
                      elevation_scale=100,
                      elevation_range=[0, 100],
                      pickable=True,
                      extruded=True,
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
    return sum(temp) / len(temp)


def initialize_date_loc():
    for day in days:
        date_loc_dict[day] = year[current_year][current_month].loc[
            year[current_year][current_month]['StartTime'].dt.day_name() == day]
    for key in ["EndLocationLon", "EndLocationLat", "StartLocationLon", "StartLocationLat"]:
        date_loc_dict[day][key] = convert_loc_data(date_loc_dict[day][key])
    for date in ["StartTime", "EndTime"]:
        date_loc_dict[day][date] = date_loc_dict[day][date].dt.date


def get_current_month():
    month = "JANUARY"
    for key in list(year[current_year].keys()):
        if len(year[current_year][key]) == 0:
            break
        month = key
    return month


def predict_loc_with_date():
    return_dict = {'percentage': [], 'lat': [], 'lon': []}
    features = ['EndLocationLat', 'EndLocationLon']
    data = date_loc_dict['Monday'][features]
    kmeans = KMeans(
        init="random",
        n_clusters=8,
        n_init=10,
        max_iter=300,
        random_state=42
    )
    kmeans.fit(data)
    labels = kmeans.labels_
    date_loc_dict['Monday']['cluster'] = labels
    count = date_loc_dict['Monday']['cluster'].value_counts()
    clusters_number = count.index.tolist()[:3]
    return_dict['percentage'] = proportion(count.tolist())[:3]
    for index in clusters_number:
        separated_cluster = date_loc_dict['Monday'].loc[date_loc_dict['Monday']['cluster'] == index]
        return_dict['lat'].append(convert_loc_data(separated_cluster['EndLocationLat'].mean()))
        return_dict['lon'].append(convert_loc_data(separated_cluster['EndLocationLon'].mean()))
    return return_dict


def proportion(input_list):
    return [value * 100 / sum(input_list) for value in input_list]


def get_address_by_location(latitude, longitude, language="en"):
    coordinates = f"{latitude}, {longitude}"
    time.sleep(1)
    try:
        return app.reverse(coordinates, language=language).raw
    except:
        return get_address_by_location(latitude, longitude)


def init():
    global total_data_sum
    global current_year
    global current_month
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
                    read['StartTime'] = pd.to_datetime(read['StartTime'], unit='ms')
                    read['EndTime'] = pd.to_datetime(read['EndTime'], unit='ms')
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
    current_year = list(year.keys())[len(list(year.keys())) - 1]
    current_month = get_current_month()
    initialize_date_loc()


def intro():
    year_range.append(list(year.keys())[0])
    year_range.append(list(year.keys())[len(list(year.keys())) - 1])

    st.title('Ewen life from {0} to {1} :sunglasses:'.format(year_range[0], year_range[1]))
    st.write(
        "The purpose of this presentation is to show how we can know many facets of a person's life just by "
        "analyzing their personal data. For this purpose we will process and analyze my personal data, "
        "in this case my google locations datas.")
    st.write('This presentation has been designed to be dynamically updated if the data is updated. (Last Data Update {0} - {1}).'.format(current_month, current_year))
    st.write("Total number of location data : ", total_data_sum)
    sum_dict = {"Years": list(total_year_sum.keys()), 'Number of Datas': list(total_year_sum.values())}
    fig = px.bar(sum_dict, x="Years", y='Number of Datas')
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    st.plotly_chart(fig, use_container_width=True)


def high_school_part():
    st.title("High School years")
    st.write(
        "Data location has been collected since August 2015, date of purchase of a phone running recent version of "
        "android (android 5). Before December 2017 we notice that few data have been collected. This is explained by "
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
        "It is noticeable that "
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
    st.write("Average distance travelled per trip in meters :")
    st.write("Before August 2018:",
             int(distance_mean(['2017', '2018'], ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY'])))
    st.write("After August 2018:", int(distance_mean(['2018', '2019'],
                                                     ['AUGUST', "SEPTEMBER", "OCTOBER", 'NOVEMBER', 'DECEMBER'])))
    st.write("There is a clear increase in the average distance travelled per trip. "
             "This is due to the fact that my school is much further from my home than my high school")


def covid_pandemic():
    st.title("Covid Pandemic")
    st.write("By the end of 2019, the covid-19 virus affects the entire planet. We observe more and more contamination "
             "until the first containment that lasted from March 17 to May 11, 2020 in France. ")
    st.write("")
    draw_map(pd.DataFrame.from_dict(get_month_loc_data(year['2020']['APRIL'])))
    st.write("")
    st.write("The only places I went during this period were the supermarkets and the area of less than a kilometer "
             "around my home to walk around")
    avg_dict = {"Average distance by day": ["Before the containment", "During the containment"],
                'Distance in meter': [round(int(distance_mean(['2018', '2019'], ['AUGUST', "SEPTEMBER",
                                                                                 "OCTOBER", 'NOVEMBER', 'DECEMBER']))),
                                      round(year['2020']['APRIL']['Distance'].mean())]}
    cols1, cols2, cols3 = st.columns([1, 6, 1])
    with cols1:
        st.write("")
    with cols2:
        fig = px.bar(avg_dict, x="Average distance by day", y='Distance in meter', text='Distance in meter', width=1200)
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        st.plotly_chart(fig)
    with cols3:
        st.write("")
    st.metric(label="", value="Distance traveled during the containment",
              delta="-{}%".format(round(int(distance_mean(['2018', '2019'],
                                                          ['AUGUST', "SEPTEMBER", "OCTOBER", 'NOVEMBER', 'DECEMBER'])) /
                                        year['2020']['APRIL']['Distance'].mean(), 1) * 100))
    st.write("")
    st.write("However, the", 1607, "m covered per day during the confinement were done on foot. If we consider that a "
                                   "man spends", 60,
             "kilocalories per km walked and that one hour of low activity is given "
             "by the Metabolic Equivalent of Task (MET) formula: ")
    st.latex(r'''MET = 1kcal * weight = 1 * 75 = 75 kcal/h''')
    st.write("1 hour of sleep is", 0.9, "MET. If we consider a typical day during confinement with", 8,
             "hours of sleep,", 16, "hours of low activity period and", 1.6, "km of walking we obtain : ")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.write("")
    with col2:
        cal_dict = {"Kilo Calories": [1836, 2100], "Calories burn": ["In containment", "Average for an healthy man"]}
        fig = px.bar(cal_dict, x="Calories burn", y='Kilo Calories', text='Kilo Calories', width=1200)
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        st.plotly_chart(fig)
    with col3:
        st.write("")
    st.write("So during the lockdown I was at a deficit of", 264, "kilocalories spent per day. So over", 54,
             "days, a total of ", 54, " * ", 264, " = ", 14256, "kilocalories. Moreover, it is estimated that", 1,
             "kilo of fat for a man represents", 7000, "kilocalories ")
    st.write("According to these calculations I would have gained", 2.1, "kg during the confinement."
                                                                         "However, these estimates are not very "
                                                                         "precise and do not take into account the "
                                                                         "few sports sessions "
                                                                         "I did and the food I ate.")
    data_bar_plot_covid()
    st.write("If we look at my travel history for the year", 2020, "and superimpose the death curve for the same year "
                                                                   "in France rescale to my location data, we notice "
                                                                   "that they are perfectly correlated. "
                                                                   "This is due to all the measures taken by the "
                                                                   "government in order to slow down the epidemic. We "
                                                                   "notice that the months where I moved less are "
                                                                   "April and November corresponding to the 2 "
                                                                   "confinements. I moved more in December, "
                                                                   "having a job "
                                                                   "in a supermarket the weekend.")

def prediction_part():
    prediction = predict_loc_with_date()
    prediction["color_r"] = [255, 0, 0]
    prediction["color_g"] = [0, 255, 0]
    prediction["color_b"] = [0, 0, 255]
    st.write(prediction)
    address = []
    for i in range(3):
        address.append(get_address_by_location(prediction['lat'][i], prediction['lon'][i]))

    draw_ml_map(pd.DataFrame.from_dict(prediction))
    st.write("First predicted place (Red): ", address[0].get('display_name'))
    st.write("Confidence :", prediction["percentage"][0], " %")
    st.write("Second predicted place (Green):", address[1].get('display_name'))
    st.write("Confidence :", prediction["percentage"][1], " %")
    st.write("Third predicted place (Blue):", address[2].get('display_name'))
    st.write("Confidence :", prediction["percentage"][2], " %")



init()
intro()
# high_school_part()
# university_part()
#covid_pandemic()
prediction_part()


