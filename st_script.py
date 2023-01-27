from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from prescription_data import (get_amoxicillin_prescription_data,
                               get_antibac_prescription_data,
                               get_antifungal_prescription_data,
                               get_infection_data,
                               get_penicillins_prescription_data)

st.set_page_config(page_title="Prescriptions")
st.title("Prescription trends")


st.header("Prescription data")

st.markdown("source data in https://tmylk--prescription-data-app.modal.run/prescriptions")

graphs = [get_infection_data,  get_antibac_prescription_data, get_penicillins_prescription_data, get_amoxicillin_prescription_data, get_antifungal_prescription_data,]

for g in graphs:
    name, url, df_items = g()

    # Create distplot with custom bin_size
    # fig = px.bar(df_items, title=f"Prescribing trends for {name} across all GP practices in NHS England",
    # barmode='group',text_auto='.2s'

    # )
    fig = px.line(df_items, title=f"Prescribing trends for {name} across all GP practices in NHS England",
    #barmode='group',text_auto='.2s'

    )


    fig.update_layout(    xaxis_title="Year",
        yaxis_title="items prescribed",)

    fig.update_traces(visible="legendonly", selector=lambda t: not t.name in ["2022","2019","2018","2017"])

    # Plot!
    st.plotly_chart(fig,)
    st.markdown("Source: https://openprescribing.net/bnf/0501/ ")


# grid_options = {
#     "columnDefs": [
#         {
            
#             "field": "year",
#             "editable": False,
#         },
#         {
#             "headerName": 'Cumulative',
#             "children": [
#                 { "field": 'cumulative % out of work due to all the 3 reasons', "editable": False, },
                
                
#                     ]
#         },
#         {
#             "headerName": 'Editable',
#             "children": [
#         {
            
#             "field": 'R0, covid and secondary increase, times more infection from prev year',
#             "editable": False,
#         }]},
#             {"headerName": 'Yearly',
#             "children": [

#         {
            
#             "field": '% of population who acquired a new COVID infection/re-infection this year',
#             "editable": False,
#         },


#                         {
            
#             "field":        '% of population acquiring a new secondary infection this year',
#             "editable": False,
#         },

#         {
            
#             "field":         '% of population who failed to recieve medical care this year due to healthcare system overload ',
#             "editable": False,
#         },]},
#             {"headerName": 'Yearly Increase',
#             "children": [

#         {
            
#             "field":         '% population out of work due to chronic covid sequelae, increase',
#             "editable": False,
#         },

#         {
            
#             "field":         '% out of work due to chronic secondary infection sequelae, increase',
#             "editable": False,
#         },
      
#         {
            
#             "field":         '% of population who failed to recieve medical care due to healthcare system overload and who had to leave the workforce due to it, increase',
#             "editable": False,
#         },]}
       
       
       
       
       

#     ],
#     }

# grid_return = AgGrid(df, grid_options)
# df = grid_return["data"]



