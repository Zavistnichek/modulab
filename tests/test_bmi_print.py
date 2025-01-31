import sys
import os
from day_01.bmi_calculator import BMICalculator

# Adjust the path to point to the correct directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

print("Current sys.path:", sys.path)

bmi = BMICalculator.calculate(70, 175)
print(bmi)
