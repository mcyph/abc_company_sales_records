import streamlit as st

from get_sales_data import get_sales_data
from vis.QuickOverview import QuickOverview
from vis.AdvancedOrderFilter import AdvancedOrderFilter


st.set_page_config(page_title='Sales Data Sample Dashboard',
                   #page_icon=favicon,
                   layout='wide',
                   initial_sidebar_state='auto')

st.markdown('''
# Sales Data Sample Dashboard

By David Morrissey 18/02/2021.

A simple demo of what can be done together with powerful data analysis tools such as 
[streamlit](https://streamlit.io), [pandas](https://pandas.pydata.org/), [plotly dash](https://plotly.com/dash/])
and [pydeck](https://deckgl.readthedocs.io/en/latest/) and sales data.
''')

df = get_sales_data()
st.sidebar.header('Page Navigation')
st.sidebar.markdown('''
Select **"Quick Overview"** for basic statistics, or **"Advanced Order Filter"** 
below for more advanced queries over time or by location.
''')
navigation = st.sidebar.radio(
    'Navigation:', options=('Quick Overview', 'Advanced Order Filter',))

if navigation == 'Quick Overview':
    QuickOverview()
elif navigation == 'Advanced Order Filter':
    AdvancedOrderFilter()
