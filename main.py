import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from time import time


def calculate_fuel_cost(kilometers_driven, fuel_consumption, fuel_price):
    return (kilometers_driven * fuel_consumption / 100) * fuel_price


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

        fuel_cost = calculate_fuel_cost(inputs['kilometers_driven'],
                                        inputs['fuel_consumption'],
                                        inputs['fuel_price'])
        maintenance_cost = calculate_maintenance_cost(current_age,
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

        data.append({
            'Year': year,
            'Fuel Cost': discounted_fuel_cost,
            'Maintenance Cost': discounted_maintenance_cost,
            'Opportunity Cost': discounted_opportunity_cost
        })

    return pd.DataFrame(data)


# Rest of the code remains unchanged
