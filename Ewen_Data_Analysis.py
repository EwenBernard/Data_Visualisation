import streamlit as st
import seaborn as sns
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

def plotly_bar_chart(
        df: pd.DataFrame,
        x_axis_label: str = 'Month',
        y_axis_label: str = 'Monthly Value'
) -> go.Figure:
    df.values
    df.columns
    this_chart = go.Figure(
        data=[go.Bar(x=df.columns, y=df.values, text = df.values,textposition = 'auto')])
    this_chart.update_yaxes(title_text=y_axis_label)
    this_chart.update_xaxes(title_text=x_axis_label)

    return this_chart

st.title('Ewen Life')

year = {"2015" : None, "2016" : None, "2017" : None, "2018" : None, "2019" : None, "2020" : None, "2021" : None}
month = {"JANUARY" : [], "FEBRUARY" : [], "MARCH" : [], "APRIL" : [], "MAY" : [], "JUNE" : [], "JULY" : [], "AUGUST" : [], "SEPTEMBER" : [], "OCTOBER" : [], "NOVEMBER" : [], "DECEMBER" : []}
path = "C:/Users/ebern/Desktop/Notebook/Extracted_Google_Maps_Data"
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

for key_year, val_year in year.items():
    fig, axs = plt.subplots()
    month_sum = {"JANUARY" : [], "FEBRUARY" : [], "MARCH" : [], "APRIL" : [], "MAY" : [], "JUNE" : [], "JULY" : [], "AUGUST" : [], "SEPTEMBER" : [], "OCTOBER" : [], "NOVEMBER" : [], "DECEMBER" : []}
    i = 0
    for key, value in val_year.items():
        val_sum = 0
        val_sum += len(value)
        month_sum[key] = [val_sum]
    month_sum = pd.DataFrame.from_dict(month_sum)
    #month_sum.columns
    #month_sum.values
    chart = plotly_bar_chart(df=month_sum)
    st.plotly_chart(chart)
#plt.legend(framealpha=1)

#print(year_list[1])
#year["2019"]["JANUARY"]