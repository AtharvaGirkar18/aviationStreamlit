

import pandas as pd
import os
from dotenv import load_dotenv
from snowflake.connector import connect
from sqlalchemy import create_engine
from sqlalchemy import text
from snowflake.sqlalchemy import URL

load_dotenv()

def load_data_to_snowflake():
    
    
    print("=" * 60)
    print("❄️  SNOWFLAKE DATA LOADER")
    print("=" * 60)
    print()
    
    print("🔄 Starting data load to Snowflake...")
    print()
    
    
    print("🔗 Connecting to Snowflake...")
    connection_url = URL(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
    )
    
    engine = create_engine(connection_url)
    
    
    print("📂 Reading CSV file...")
    try:
        df = pd.read_csv('Airline_Dataset.csv')
    except FileNotFoundError:
        print("❌ Error: Airline_Dataset.csv not found!")
        print("   Make sure the CSV file is in the same directory as this script.")
        return
    
    
    column_mapping = {
        'Passenger ID': 'passenger_id',
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'Gender': 'gender',
        'Age': 'age',
        'Nationality': 'nationality',
        'Airport Name': 'airport_name',
        'Airport Country Code': 'airport_country_code',
        'Country Name': 'country_name',
        'Airport Continent': 'airport_continent',
        'Continents': 'continents',
        'Departure Date': 'departure_date',
        'Arrival Airport': 'arrival_airport',
        'Pilot Name': 'pilot_name',
        'Flight Status': 'flight_status'
    }
    
    df = df.rename(columns=column_mapping)
    
    
    print("📅 Converting date column...")
    df['departure_date'] = pd.to_datetime(df['departure_date'], errors='coerce')
    
    print(f"✅ Loaded {len(df):,} rows from CSV")
    print(f"📋 Columns: {len(df.columns)}")
    print()
    
    
    print("📊 Sample data (first 3 rows):")
    print(df.head(3).to_string())
    print()
    
    
    print("⬆️  Uploading to Snowflake...")
    print("   (This may take a few minutes for large datasets)")
    
    try:
        df.to_sql(
            'aviation_data',
            engine,
            if_exists='replace',  
            index=False,
            chunksize=5000,
            method='multi'
        )
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Data loaded to Snowflake")
        print("=" * 60)
        print()
        print(f"📊 Total rows loaded: {len(df):,}")
        print(f"📍 Database: {os.getenv('SNOWFLAKE_DATABASE')}")
        print(f"📍 Schema: {os.getenv('SNOWFLAKE_SCHEMA')}")
        print(f"📍 Table: aviation_data")
        print()
        
       
        print("🔍 Verifying data in Snowflake...")
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) as count FROM aviation_data'))
            print(result.fetchone())
            row_count = result.fetchone()[0]
            print(f"✅ Verification: {row_count:,} rows confirmed in Snowflake table")
            
            
            result = conn.execute("SELECT nationality, COUNT(*) as count FROM aviation_data GROUP BY nationality ORDER BY count DESC LIMIT 5")
            print()
            print("🌍 Top 5 Nationalities:")
            for row in result:
                print(f"   {row[0]}: {row[1]:,} passengers")
        
        print()
        print("=" * 60)
        print("🎉 All done! Your data is now in Snowflake!")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("❌ Error during upload:")
        print(f"   {e}")
        print()
        print("💡 Troubleshooting tips:")
        print("   1. Check that the aviation_data table exists in Snowflake")
        print("   2. Verify your .env credentials are correct")
        print("   3. Ensure your Snowflake warehouse is running")

if __name__ == "__main__":
    try:
        load_data_to_snowflake()
    except Exception as e:
        print()
        print("❌ Error:", e)
        print()
        print("💡 Tips:")
        print("1. Check your .env file has correct Snowflake credentials")
        print("2. Verify Snowflake packages are installed:")
        print("   pip install snowflake-connector-python snowflake-sqlalchemy")
        print("3. Make sure Airline_Dataset.csv is in the same folder")
