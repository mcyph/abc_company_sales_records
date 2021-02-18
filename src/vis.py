import streamlit as st

from get_sales_data import get_sales_data
from vis.QuickOverview import QuickOverview
from vis.AdvancedOrderFilter import AdvancedOrderFilter


st.set_page_config(page_title='Sales Data Sample Dashboard',
                   #page_icon=favicon,
                   layout='wide',
                   initial_sidebar_state='auto')

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
