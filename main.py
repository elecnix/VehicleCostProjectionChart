import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stSelectbox > div > div > select {
        font-size: 16px;
    }
    .stNumberInput > div > div > input {
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
    base_percentage = 0.01  # 1% of initial price for a new car
    age_factor = 1 + (age * 0.005)  # Increase by 0.5% per year
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

# Input fields
st.header("Input Variables")

col1, col2 = st.columns(2)

with col1:
    initial_price = st.number_input("Initial Purchase Price ($)", min_value=0, value=30000, step=1000)
    current_age = st.number_input("Current Vehicle Age (years)", min_value=0, max_value=30, value=5, step=1)
    kilometers_driven = st.number_input("Kilometers Driven Annually", min_value=0, value=15000, step=1000)
    fuel_consumption = st.number_input("Average Fuel Consumption (L/100km)", min_value=0.0, value=8.0, step=0.1)

with col2:
    current_market_value = st.number_input("Current Market Value ($)", min_value=0, value=20000, step=1000)
    fuel_price = st.number_input("Fuel Price ($/L)", min_value=0.0, value=1.5, step=0.1)
    discount_rate = st.number_input("Discount Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.1) / 100

# Generate projection
if st.button("Generate Cost Projection"):
    inputs = {
        'initial_price': initial_price,
        'current_age': current_age,
        'kilometers_driven': kilometers_driven,
        'fuel_consumption': fuel_consumption,
        'current_market_value': current_market_value,
        'fuel_price': fuel_price,
        'discount_rate': discount_rate
    }

    projection_data = generate_cost_projection(inputs)

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

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Display the data table
    st.subheader("Projected Costs Table")
    st.dataframe(projection_data.style.format("{:.2f}"))

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
