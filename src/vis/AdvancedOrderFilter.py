import os
import json
import gpdvega
import numpy as np
import pandas as pd
import pydeck as pdk
import altair as alt
import streamlit as st
import geopandas as gpd
from pathlib import Path
import plotly.express as px

from get_sales_data import get_sales_data, \
    ACRONYM_TO_TERRITORIES, \
    TERRITORIES_TO_COUNTRIES, \
    TERRITORIES_TO_ACRYONYM


VIS_SRC_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DF = get_sales_data()


class AdvancedOrderFilter:
    def __init__(self):
        self.sidebar()
        self.orders_over_time()
        self.orders_on_world_map()

    #========================================================================#
    #                               Sidebar                                  #
    #========================================================================#

    def sidebar(self):
        # Filter date values
        st.sidebar.header("Date Range")
        mindate = st.sidebar.date_input(
            'Minimum date', DF.ORDERDATE.min(), DF.ORDERDATE.min(), DF.ORDERDATE.max())
        maxdate = st.sidebar.date_input(
            'Maximum date', DF.ORDERDATE.max(), DF.ORDERDATE.min(), DF.ORDERDATE.max())
        df = DF[(DF.ORDERDATE >= pd.to_datetime(mindate)) &
                (DF.ORDERDATE <= pd.to_datetime(maxdate))]

        # Filter categorical columns
        st.sidebar.header("Order Details")
        dealsize = st.sidebar.selectbox(
            'Deal Size', ['(All Sizes)', 'Small', 'Medium', 'Large'])
        productline = st.sidebar.selectbox(
            'Product Line', ['(All Product Lines)'] + sorted(list(df.PRODUCTLINE.unique())))
        orderstatus = st.sidebar.selectbox(
            'Order Status', ['(All Statuses)'] + sorted(list(df.STATUS.unique())))

        st.sidebar.header("Geographic Area")
        territory = st.sidebar.selectbox(
            'Territory',
            ['(All Territories)'] + sorted([ACRONYM_TO_TERRITORIES[i] for i in list(df.TERRITORY.unique())]))
        if territory != '(All Territories)':
            country = st.sidebar.selectbox(
                'Country', ['(All Countries)'] + sorted(TERRITORIES_TO_COUNTRIES[TERRITORIES_TO_ACRYONYM[territory]]))
        else:
            country = st.sidebar.selectbox(
                'Country', ['(All Countries)'] + sorted(list(df.COUNTRY.unique())))

        if dealsize != '(All Sizes)':
            df = df[df.DEALSIZE == dealsize]
        if productline != '(All Product Lines)':
            df = df[df.PRODUCTLINE == productline]
        if orderstatus != '(All Statuses)':
            df = df[df.STATUS == orderstatus]
        if country != '(All Countries)':
            df = df[df.COUNTRY == country]
        if territory != '(All Territories)':
            df = df[df.TERRITORY == TERRITORIES_TO_ACRYONYM[territory]]

        # Filter price/totals values
        st.sidebar.header("Price")
        sales = st.sidebar.slider(
            'Select a range of order total values', float(df.SALES.min()), float(df.SALES.max()),
            (float(df.SALES.min()), float(df.SALES.max())))
        itemvalue = st.sidebar.slider(
            'Select a range of individual item values', float(df.PRICEEACH.min()), float(df.PRICEEACH.max()),
            (float(df.PRICEEACH.min()), float(df.PRICEEACH.max())))
        msrp = st.sidebar.slider(
            'Select a range of MSRPs', float(df.MSRP.min()), float(df.MSRP.max()),
            (float(df.MSRP.min()), float(df.MSRP.max())))

        df = df[(df.SALES >= sales[0]) & (df.SALES <= sales[1])]
        df = df[(df.PRICEEACH >= itemvalue[0]) & (df.PRICEEACH <= itemvalue[1])]
        df = df[(df.MSRP >= msrp[0]) & (df.MSRP <= msrp[1])]
        self.df = df

    #========================================================================#
    #                                Charts                                  #
    #========================================================================#

    def orders_over_time(self):
        st.markdown('''
        # Advanced Order Filter
        
        This page shows advanced filters, fine-tunable using the left panel.
        
        It's useful when wanting to find specific statistics about orders 
        by time, location or order type.
        ''')

        st.markdown('''
        ## Orders by Country
        ''')

        df = self.df.groupby([pd.Grouper('COUNTRY'),
                              self.df['ORDERDATE'].dt.strftime('%Y-%m')])['SALES'].sum()
        df = df.sort_values(ascending=False)
        df = df.reset_index()
        df = df.rename({'level_0': 'COUNTRY', 'level_1': 'ORDERDATE'})

        fig = px.area(df, x="ORDERDATE", y="SALES",
                      color="COUNTRY", line_group="COUNTRY")
        st.plotly_chart(fig, use_container_width=True)

    def orders_on_world_map(self):
        st.markdown('''
        # Orders on World Map
        ''')

        st.markdown('''
        ## By Geolocation
        
        This tool allows seeing precise locations where orders were placed.
        
        Coordinates are auto-generated and may contain errors in rare cases.
        ''')

        orders_heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=self.df.dropna(),
            get_position=["LONG", "LAT"],
            aggregation='"SUM"',
            get_weight="SALES",  # NOTE ME!!
            pickable=True)
        chart = pdk.Deck(
            layers=[orders_heatmap_layer],
            map_provider="carto",
            map_style=pdk.map_styles.CARTO_LIGHT)
        st.pydeck_chart(chart)

        st.header('Data Table')
        st.dataframe(self.df)
