from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from prescriptions import graphs
from prescription_data import get_prescription_data


st.set_page_config(page_title="Prescriptions")
st.title("Prescription trends")

st.header("Prescription data")




for g in graphs:
    name, url, condition, filename = g()

    # Create distplot with custom bin_size
    # fig = px.bar(df_items, title=f"Prescribing trends for {name} across all GP practices in NHS England",
    # barmode='group',text_auto='.2s'

    # )
    df_items = get_prescription_data(filename=filename)
    fig = px.line(df_items, title=f"Prescribing trends for {name} across all GP practices in NHS England",
    #barmode='group',text_auto='.2s'

    )


    fig.update_layout(    xaxis_title="Year",
        yaxis_title="items prescribed per 1000 people",)

    fig.update_traces(visible="legendonly", selector=lambda t: t.name in ["2020","2021",])

    # Plot!
    st.plotly_chart(fig,)
    st.markdown(f"Reference comparison:  {url}")
    st.markdown(f"Database query filter :  {condition}")


st.header("Primary Data")

st.markdown("*Prescriptions* by GP in England. Published by NHS UK. [link](https://www.nhsbsa.nhs.uk/prescription-data/prescribing-data/english-prescribing-data-epd)  ")

st.markdown("*Population* of England. Prescriptions normalised to population using the approach used by [Open Prescribing](https://openprescribing.net/long_term_trends/) from [ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatestimeseriesdataset). Population of England in 2022 is assumed to be 56550138. [(source)](https://populationdata.org.uk/population-of-england/)   ")

st.header("Secondary Data")

st.markdown("The data that the graphs are based on can be browsed here https://tmylk--prescription-data-app.modal.run/prescriptions (built using Datasette framework)")

st.markdown("Code to process primary data is in https://github.com/tmylk/yearly_prescriptions")


st.header("Acknowledgements")

st.markdown("Conor Browne for bringing my attention to the Persistent Cyclical Immune Dysregulation idea in this [tweet](https://twitter.com/brownecfm/status/1601526039678943233). ") 

st.markdown("[Open Prescribing](https://openprescribing.net/) for open source population normalisation code") 

st.markdown("NHS Data Hackathon 2016 for introducing me to the prescription data") 

st.markdown("[Modal ](https://modal.com/) platform for making data engineering so easy  ") 
