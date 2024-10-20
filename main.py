import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from time import time
import json
import os

# Set page configuration
st.set_page_config(page_title="Vehicle Cost Projection",
                   page_icon="🚗",
                   layout="wide")

# Custom CSS to improve responsiveness
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stSlider > div > div > div > div {
        font-size: 16px;
    }
</style>
""",
            unsafe_allow_html=True)

# Title and description
st.title("Vehicle Cost Projection")
st.write(
    "This application generates a stacked bar chart showing the projected costs of owning a single vehicle over the next 10 years."
)

# Functions for calculations
def calculate_fuel_cost(kilometers, fuel_consumption, fuel_price):
    return (kilometers * fuel_consumption / 100) * fuel_price

def calculate_maintenance_cost(age, initial_price, year_offset=0):
    return initial_price * (0.0015 * (age + year_offset) + 0.005)

def calculate_opportunity_cost(market_value, discount_rate):
    return market_value * discount_rate

def discount_cash_flow(cost, discount_rate, year):
    return cost / (1 + discount_rate)**year

def generate_cost_projection(inputs):
    years = range(11)  # 0 to 10 years
    data = []

    for year in years:
        current_age = inputs['current_age'] + year
        market_value = max(0, inputs['current_market_value'] *
                           (1 - 0.1)**year)  # Simple linear depreciation
        discounted_market_value = discount_cash_flow(market_value,
                                                     inputs['discount_rate'],
                                                     year)

        fuel_cost = calculate_fuel_cost(inputs['kilometers_driven'],
                                        inputs['fuel_consumption'],
                                        inputs['fuel_price'])
        maintenance_cost = calculate_maintenance_cost(inputs['current_age'],
                                                      inputs['initial_price'],
                                                      year)
        opportunity_cost = calculate_opportunity_cost(market_value,
                                                      inputs['discount_rate'])

        discounted_fuel_cost = discount_cash_flow(fuel_cost,
                                                  inputs['discount_rate'],
                                                  year)
        discounted_maintenance_cost = discount_cash_flow(
            maintenance_cost, inputs['discount_rate'], year)
        discounted_opportunity_cost = discount_cash_flow(
            opportunity_cost, inputs['discount_rate'], year)

        total_discounted_cost = (discounted_fuel_cost + discounted_maintenance_cost +
                                 discounted_opportunity_cost)

        data.append({
            'Year': year,
            'Market Value (Nominal)': market_value,
            'Market Value (Discounted)': discounted_market_value,
            'Fuel Cost (Actual)': fuel_cost,
            'Fuel Cost (Discounted)': discounted_fuel_cost,
            'Maintenance Cost (Actual)': maintenance_cost,
            'Maintenance Cost (Discounted)': discounted_maintenance_cost,
            'Opportunity Cost (Actual)': opportunity_cost,
            'Opportunity Cost (Discounted)': discounted_opportunity_cost,
            'Total Cost (Discounted)': total_discounted_cost,
        })

    df = pd.DataFrame(data)
    df['Cumulative Cost (Discounted)'] = df['Total Cost (Discounted)'].cumsum()
    return df

# Functions for persistent storage
def load_inputs():
    if os.path.exists('user_inputs.json'):
        with open('user_inputs.json', 'r') as f:
            return json.load(f)
    return {
        'initial_price': 30000,
        'current_age': 5,
        'kilometers_driven': 15000,
        'fuel_consumption': 8.0,
        'current_market_value': 20000,
        'fuel_price': 1.5,
        'discount_rate': 0.10
    }

def save_inputs(inputs):
    with open('user_inputs.json', 'w') as f:
        json.dump(inputs, f)

# Initialize session state
if 'inputs' not in st.session_state:
    st.session_state.inputs = load_inputs()

# Initialize chart_key in session state
if 'chart_key' not in st.session_state:
    st.session_state.chart_key = 0

# Create placeholders for graph and table
graph_placeholder = st.empty()
table_placeholder = st.empty()

# Function to update graph
def update_graph():
    projection_data = generate_cost_projection(st.session_state.inputs)

    # Create stacked bar chart
    fig = go.Figure()

    for cost_type in [
            'Fuel Cost (Discounted)', 'Maintenance Cost (Discounted)',
            'Opportunity Cost (Discounted)'
    ]:
        fig.add_trace(
            go.Bar(x=projection_data['Year'],
                   y=projection_data[cost_type].round().astype(int),
                   name=cost_type))

    # Add cumulative cost line
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Cumulative Cost (Discounted)'].round().astype(int),
        name='Cumulative Cost',
        yaxis='y2'
    ))

    fig.update_layout(
        title="10-Year Vehicle Cost Projection (Discounted)",
        xaxis_title="Year",
        yaxis_title="Annual Costs ($)",
        yaxis2=dict(title='Cumulative Cost ($)', overlaying='y', side='right'),
        barmode='stack',
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Update the graph placeholder with a dynamic key
    graph_placeholder.plotly_chart(
        fig,
        use_container_width=True,
        key=f"cost_projection_chart_{st.session_state.get('chart_key', 0)}")

    # Increment the chart key
    st.session_state['chart_key'] = st.session_state.get('chart_key', 0) + 1

    # Update the data table placeholder
    table_placeholder.subheader("Projected Costs Table (Actual vs Discounted)")

    # Format the DataFrame for display
    display_df = projection_data.copy()
    for column in display_df.columns:
        if column != 'Year':
            display_df[column] = display_df[column].round().astype(int).apply(lambda x: f'${x:,}')

    # Display the table with improved formatting
    table_placeholder.dataframe(
        display_df.style.set_properties(**{'text-align': 'right'}))

# Debounce function
def debounce(func):
    last_run = 0

    def debounced(*args, **kwargs):
        nonlocal last_run
        if time() - last_run > 0.5:  # 500ms debounce time
            func(*args, **kwargs)
            last_run = time()

    return debounced

# Wrap update_graph with debounce
update_graph_debounced = debounce(update_graph)

# Use st.form to wrap all inputs
with st.form(key='input_form'):
    st.header("Input Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.inputs['initial_price'] = st.slider(
            "Initial Purchase Price ($)",
            min_value=0,
            max_value=100000,
            value=st.session_state.inputs['initial_price'],
            step=1000)
        st.session_state.inputs['current_age'] = st.slider(
            "Current Vehicle Age (years)",
            min_value=0,
            max_value=30,
            value=st.session_state.inputs['current_age'],
            step=1)
        st.session_state.inputs['kilometers_driven'] = st.slider(
            "Kilometers Driven Annually",
            min_value=0,
            max_value=50000,
            value=st.session_state.inputs['kilometers_driven'],
            step=1000)
        st.session_state.inputs['fuel_consumption'] = st.slider(
            "Average Fuel Consumption (L/100km)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.inputs['fuel_consumption'],
            step=0.1)

    with col2:
        st.session_state.inputs['current_market_value'] = st.slider(
            "Current Market Value ($)",
            min_value=0,
            max_value=100000,
            value=st.session_state.inputs['current_market_value'],
            step=1000)
        st.session_state.inputs['fuel_price'] = st.slider(
            "Fuel Price ($/L)",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.inputs['fuel_price'],
            step=0.1)
        st.session_state.inputs['discount_rate'] = st.slider(
            "Discount Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.inputs['discount_rate'] * 100,
            step=0.1) / 100

    submit_button = st.form_submit_button(label='Update Graph')

if submit_button:
    save_inputs(st.session_state.inputs)
    update_graph_debounced()

# Generate initial graph
update_graph()

# Additional information
st.markdown("""
### Assumptions and Notes
- The current market value is depreciated linearly over time.
- Insurance costs are excluded in this prototype.
- All costs are discounted to present value.
- The opportunity cost is calculated based on the current market value of the vehicle.
- Maintenance costs are calculated using the formula: MC(A+t) = V * (0.0015 * (A+t) + 0.005), where V is the initial price, A is the current age, and t is the year offset.
""")

# Footer
st.markdown("---")
st.markdown("Created with Streamlit • Data is for illustrative purposes only")
