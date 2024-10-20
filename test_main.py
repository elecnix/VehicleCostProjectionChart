import unittest
from main import (calculate_fuel_cost, calculate_maintenance_cost,
                  calculate_opportunity_cost, discount_cash_flow,
                  generate_cost_projection)
import pandas as pd


class TestVehicleCostProjection(unittest.TestCase):

    def test_calculate_fuel_cost(self):
        self.assertAlmostEqual(calculate_fuel_cost(15000, 8.0, 1.5), 1800.0)
        self.assertAlmostEqual(calculate_fuel_cost(10000, 6.5, 2.0), 1300.0)

    def test_calculate_maintenance_cost(self):
        self.assertAlmostEqual(calculate_maintenance_cost(5, 30000), 375.0)
        self.assertAlmostEqual(calculate_maintenance_cost(8, 25000, 2), 500.0)

    def test_calculate_opportunity_cost(self):
        self.assertAlmostEqual(calculate_opportunity_cost(20000, 0.10), 2000.0)
        self.assertAlmostEqual(calculate_opportunity_cost(15000, 0.05), 750.0)

    def test_discount_cash_flow(self):
        self.assertAlmostEqual(discount_cash_flow(1000, 0.10, 1),
                               909.09,
                               places=2)
        self.assertAlmostEqual(discount_cash_flow(1000, 0.05, 2),
                               907.03,
                               places=2)

    def test_generate_cost_projection(self):
        inputs = {
            'initial_price': 30000,
            'current_age': 5,
            'kilometers_driven': 15000,
            'fuel_consumption': 8.0,
            'current_market_value': 20000,
            'fuel_price': 1.5,
            'discount_rate': 0.10
        }
        projection = generate_cost_projection(inputs)

        self.assertIsInstance(projection, pd.DataFrame)
        self.assertEqual(len(projection), 11)  # 0 to 10 years
        self.assertTrue(
            all(col in projection.columns for col in
                ['Year', 'Fuel Cost', 'Maintenance Cost', 'Opportunity Cost']))

        # Test the first year's values
        first_year = projection.iloc[0]
        self.assertEqual(first_year['Year'], 0)
        self.assertAlmostEqual(first_year['Fuel Cost'], 1800.0)
        self.assertAlmostEqual(first_year['Maintenance Cost'], 375.0)
        self.assertAlmostEqual(first_year['Opportunity Cost'], 2000.0)


if __name__ == '__main__':
    unittest.main()
