import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///aviation.db")

df = pd.read_csv("Airline_Dataset.csv")  

df['Departure Date'] = pd.to_datetime(df['Departure Date'], format='%d-%m-%Y', errors='coerce')

df.to_sql("aviation_data", engine, if_exists="replace", index=False)

print("Data loaded successfully into aviation_data table.")
