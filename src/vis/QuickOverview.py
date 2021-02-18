import streamlit as st
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px

from get_sales_data import get_sales_data, \
    ACRONYM_TO_TERRITORIES, \
    TERRITORIES_TO_COUNTRIES, \
    TERRITORIES_TO_ACRYONYM


DF = get_sales_data()


class QuickOverview:
    def __init__(self):
        self.basic_stats()
        self.country_stats()
        self.territory_stats()

    #========================================================================#
    #                                Charts                                  #
    #========================================================================#

    def basic_stats(self):
        st.markdown('''
        # Basic Statistics
        
        This page shows basic order statistics over time and by country.
        ''')

        # Display a basic number/total income by orders graph
        st.markdown('''
        ## Orders By Month
        
        This bar chart shows profits earned each month for all countries.
        ''')

        df = DF.groupby(DF['ORDERDATE'].dt.strftime('%Y-%m'))['SALES'] \
            .sum() \
            .sort_index().reset_index(name='SALES')
        fig = px.bar(df, y='SALES', x='ORDERDATE', text='SALES')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

    def country_stats(self):
        st.markdown('''
        # Country Statistics

        This bar chart shows total profits earned for each country.
        ''')
        countries = sorted(list(DF.COUNTRY.unique()))

        data = []
        for country in countries:
            data.append((DF[DF.COUNTRY == country].SALES.sum(), country))
        data.sort(reverse=True)

        df = pd.DataFrame(data={'Country': [i[1] for i in data],
                                'Total Sales': [i[0] for i in data]})
        fig = px.bar(df, y='Total Sales', x='Country', text='Total Sales')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

    def territory_stats(self):
        st.markdown('''
        # Territory Statistics
        
        The below charts show statistics by countries grouped into territories:

        * **APAC:** Asia Pacific
        * **EMEA:** Europe, Middle East and Africa
        * **Japan:** Japan
        * **NA:** North America
        ''')

        # Display a basic pie graph by country
        st.markdown('''
        ## Overall Profits (All Time)
        ''')
        df = DF.groupby('TERRITORY')['SALES'].sum()
        df = df.sort_values(ascending=False)
        df = df.reset_index()
        df = df.rename({'level_0': 'TERRITORY'})
        fig = px.pie(df, values='SALES', names='TERRITORY')
        st.plotly_chart(fig, use_container_width=True)

        # Display a basic stacked chart
        st.markdown('''
        ## Profits by Quarter

        This stacked bar chart shows profits earned by territory for each quarter.
        ''')
        df = DF.groupby([pd.Grouper('TERRITORY'),
                         pd.Grouper('YEAR_ID'),
                         pd.Grouper('QTR_ID')])['SALES'] \
            .sum() \
            .sort_index().reset_index(name='SALES')
        df['ORDERQUARTER'] = ['%s-Q%s' % (int(row.YEAR_ID), int(row.QTR_ID)) for x, row in df.iterrows()]

        fig = px.bar(df, y='SALES', x='ORDERQUARTER', text='SALES', color='TERRITORY')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)
