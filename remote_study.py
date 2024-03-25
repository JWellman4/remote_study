import streamlit as st
import pandas as pd
import plotly_express as px

st.set_page_config(
    page_title="Office vs Remote",
    page_icon="bar_chart",
    layout="wide",
)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Load the data
df = load_data('studysession/Correlation.csv')

# Transforming Data
## create a dictionary of replacements
replacements = {'Work': 'Office', 'Home': 'Remote'}

## replace values using the .map() method
df['Work Location'] = df['Work Location'].map(replacements).fillna(df['Work Location'])

# Creating Defs
def add_select_all_option(options_data):
    options_with_select_all = ['Select All'] + options_data
    return options_with_select_all

def options_select():
    if "selected_options" in st.session_state:
        if "Select All" in st.session_state["selected_options"]:
            st.session_state["selected_options"] = [available_options[0]]
            st.session_state["max_selections"] = 1
        else:
            st.session_state["max_selections"] = len(available_options)

# Load options from a CSV file
options_data = df['Name'].unique().tolist()
options_with_select_all = add_select_all_option(options_data)
available_options = options_with_select_all

if "max_selections" not in st.session_state:
    st.session_state["max_selections"] = len(available_options)

with st.sidebar:
    st.title('Select Filters')
    select_options =st.multiselect(
            label="Select an Option",
            options=options_with_select_all,
            key="selected_options",
            max_selections=st.session_state["max_selections"],
            on_change=options_select,
            format_func=lambda x: "Select All" if x == "Select All" else f"{x}",
)

# Filter DataFrame based on selected options from both multiselects
if 'Select All' in select_options:
    df_filtered = df
else:
    df_filtered = df[df['Name'].isin(select_options)]

# Grouping and Calculations
filtered_df_grouped = df_filtered.groupby(by=['Name'], as_index=False)['TotalCoreHours (Sum)'].sum()
loc_filtered_df_grouped = df_filtered.groupby(by=['Work Location'], as_index=False)['TotalHoursWorkOut (Sum)'].sum()

# Display selected options
def pie_chart():
    fig3 = px.pie(
        loc_filtered_df_grouped,
        values='TotalHoursWorkOut (Sum)',
        names= 'Work Location',
        labels= {'Work Location': 'Location','TotalHoursWorkOut (Sum)':'Output Hours'}
    )
    st.plotly_chart(fig3, use_container_width=True)

def scatter_chart():
    fig4 = px.scatter(
        df_filtered, 
        x='TotalHoursAtWork (Sum)',
        y='TotalHoursWorkOut (Sum)', 
        color='Work Location',
        hover_data= 'Date',
        labels={'Work Location': 'Location','Date':'Week Ending','TotalHoursAtWork (Sum)': 'Hours At Work', 
                'TotalHoursWorkOut (Sum)': 'Output Hours'} 
    )
    fig4.update_traces(
        marker=dict(size=8, symbol="diamond", line=dict(width=1, color="DarkSlateGrey")),
        selector=dict(mode="markers"))
    fig4.update_layout(showlegend=False)
    fig4.update_yaxes(showgrid=False)
    st.plotly_chart(fig4, use_container_width=True)
            

# Create layout using st.columns
col1, col2 = st.columns([2,3], gap='medium')
with col1:
    st.header("Is there a drop in Productivity due to working Remote?")
    st.markdown('This has been a common belief, since even before **COVID**.\
                However my research of over **300** weekly, employee data **points** show that \
                there is **:green[no significant difference]** in **productivity** based on where you choose to work. \
                So, find your Happy Place and Work from there!')
    with st.popover("Division of Output"):
        pie_chart()

with col2:
    scatter_chart()
