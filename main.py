import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from time import time

# Set page configuration
st.set_page_config(
    page_title="Vehicle Cost Projection",
    page_icon="🚗",
    layout="wide"
)

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
""", unsafe_allow_html=True)

# Title and description
st.title("Vehicle Cost Projection")
st.write("This application generates a stacked bar chart showing the projected costs of owning a single vehicle over the next 10 years.")

# Functions for calculations
def calculate_fuel_cost(kilometers, fuel_consumption, fuel_price):
    return (kilometers * fuel_consumption / 100) * fuel_price

def calculate_maintenance_cost(age, initial_price):
    base_percentage = 0.02  # 2% of initial price for a new car
    age_factor = 1 + (age * 0.05)  # Increase by 5% per year (modified)
    return initial_price * base_percentage * age_factor

def calculate_opportunity_cost(market_value, discount_rate):
    return market_value * discount_rate

def discount_cash_flow(cost, discount_rate, year):
    return cost / (1 + discount_rate) ** year

def generate_cost_projection(inputs):
    years = range(11)  # 0 to 10 years
    data = []

    for year in years:
        current_age = inputs['current_age'] + year
        market_value = max(0, inputs['current_market_value'] * (1 - 0.1) ** year)  # Simple linear depreciation

        fuel_cost = calculate_fuel_cost(inputs['kilometers_driven'], inputs['fuel_consumption'], inputs['fuel_price'])
        maintenance_cost = calculate_maintenance_cost(current_age, inputs['initial_price'])
        opportunity_cost = calculate_opportunity_cost(market_value, inputs['discount_rate'])

        discounted_fuel_cost = discount_cash_flow(fuel_cost, inputs['discount_rate'], year)
        discounted_maintenance_cost = discount_cash_flow(maintenance_cost, inputs['discount_rate'], year)
        discounted_opportunity_cost = discount_cash_flow(opportunity_cost, inputs['discount_rate'], year)

        data.append({
            'Year': year,
            'Fuel Cost': discounted_fuel_cost,
            'Maintenance Cost': discounted_maintenance_cost,
            'Opportunity Cost': discounted_opportunity_cost
        })

    return pd.DataFrame(data)

# Initialize session state
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'initial_price': 30000,
        'current_age': 5,
        'kilometers_driven': 15000,
        'fuel_consumption': 8.0,
        'current_market_value': 20000,
        'fuel_price': 1.5,
        'discount_rate': 0.10
    }

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

    for cost_type in ['Fuel Cost', 'Maintenance Cost', 'Opportunity Cost']:
        fig.add_trace(go.Bar(
            x=projection_data['Year'],
            y=projection_data[cost_type],
            name=cost_type
        ))

    fig.update_layout(
        title="10-Year Vehicle Cost Projection",
        xaxis_title="Year",
        yaxis_title="Discounted Costs ($)",
        barmode='stack',
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Update the graph placeholder with a dynamic key
    graph_placeholder.plotly_chart(fig, use_container_width=True, key=f"cost_projection_chart_{st.session_state.get('chart_key', 0)}")
    
    # Increment the chart key
    st.session_state['chart_key'] = st.session_state.get('chart_key', 0) + 1

    # Update the data table placeholder
    table_placeholder.subheader("Projected Costs Table")
    table_placeholder.dataframe(projection_data.style.format("{:.2f}"))

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
        st.session_state.inputs['initial_price'] = st.slider("Initial Purchase Price ($)", min_value=0, max_value=100000, value=st.session_state.inputs['initial_price'], step=1000)
        st.session_state.inputs['current_age'] = st.slider("Current Vehicle Age (years)", min_value=0, max_value=30, value=st.session_state.inputs['current_age'], step=1)
        st.session_state.inputs['kilometers_driven'] = st.slider("Kilometers Driven Annually", min_value=0, max_value=50000, value=st.session_state.inputs['kilometers_driven'], step=1000)
        st.session_state.inputs['fuel_consumption'] = st.slider("Average Fuel Consumption (L/100km)", min_value=0.0, max_value=20.0, value=st.session_state.inputs['fuel_consumption'], step=0.1)

    with col2:
        st.session_state.inputs['current_market_value'] = st.slider("Current Market Value ($)", min_value=0, max_value=100000, value=st.session_state.inputs['current_market_value'], step=1000)
        st.session_state.inputs['fuel_price'] = st.slider("Fuel Price ($/L)", min_value=0.0, max_value=5.0, value=st.session_state.inputs['fuel_price'], step=0.1)
        st.session_state.inputs['discount_rate'] = st.slider("Discount Rate (%)", min_value=0.0, max_value=20.0, value=st.session_state.inputs['discount_rate'] * 100, step=0.1) / 100

    submit_button = st.form_submit_button(label='Update Graph')

if submit_button:
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
- Maintenance costs increase with the vehicle's age and are based on a percentage of the initial purchase price.
""")

# Footer
st.markdown("---")
st.markdown("Created with Streamlit • Data is for illustrative purposes only")
