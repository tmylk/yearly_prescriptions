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

st.markdown("source data in https://tmylk--prescription-data-app.modal.run/prescriptions")

st.markdown("source code in https://github.com/tmylk/yearly_prescriptions")



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

