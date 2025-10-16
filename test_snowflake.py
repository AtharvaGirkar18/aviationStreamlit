"""
Test Snowflake Connection

This script tests your Snowflake connection and queries sample data.
Run this after setting up your .env file to verify everything works.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL

load_dotenv()

def test_snowflake_connection():
    """Test Snowflake connection and query data"""
    
    print("=" * 60)
    print("❄️  SNOWFLAKE CONNECTION TEST")
    print("=" * 60)
    print()
    
    print("🔄 Testing Snowflake connection...")
    print()
    
    # Display configuration (without password)
    print("📋 Configuration:")
    print(f"   Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print(f"   User: {os.getenv('SNOWFLAKE_USER')}")
    print(f"   Database: {os.getenv('SNOWFLAKE_DATABASE')}")
    print(f"   Schema: {os.getenv('SNOWFLAKE_SCHEMA')}")
    print(f"   Warehouse: {os.getenv('SNOWFLAKE_WAREHOUSE')}")
    print(f"   Role: {os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')}")
    print()
    
    try:
        # Create connection
        print("🔗 Creating connection...")
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
        
        with engine.connect() as conn:
            print("✅ Connection established!")
            print()
            
            # Test 1: Count rows
            print("=" * 60)
            print("TEST 1: Count Total Rows")
            print("=" * 60)
            result = conn.execute(text("SELECT COUNT(*) as count FROM aviation_data"))
            count = result.fetchone()[0]
            print(f"✅ Total rows in aviation_data: {count:,}")
            print()
            
            # Test 2: Sample data
            print("=" * 60)
            print("TEST 2: Sample Data (First 5 Rows)")
            print("=" * 60)
            result = conn.execute(text("SELECT passenger_id, first_name, last_name, nationality, age FROM aviation_data LIMIT 5"))
            rows = result.fetchall()
            
            if rows:
                print(f"{'ID':<15} {'First Name':<15} {'Last Name':<15} {'Nationality':<20} {'Age':<5}")
                print("-" * 70)
                for row in rows:
                    print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<20} {row[4]:<5}")
            else:
                print("⚠️  No data found in table")
            print()
            
            # Test 3: Aggregation query
            print("=" * 60)
            print("TEST 3: Top 5 Nationalities")
            print("=" * 60)
            result = conn.execute(text(
                "SELECT nationality, COUNT(*) as count "
                "FROM aviation_data "
                "GROUP BY nationality "
                "ORDER BY count DESC "
                "LIMIT 5"
            ))
            print(f"{'Nationality':<30} {'Count':<10}")
            print("-" * 40)
            for row in result:
                print(f"{row[0]:<30} {row[1]:>10,}")
            print()
            
            # Test 4: Gender distribution
            print("=" * 60)
            print("TEST 4: Gender Distribution")
            print("=" * 60)
            result = conn.execute(text(
                "SELECT gender, COUNT(*) as count "
                "FROM aviation_data "
                "GROUP BY gender "
                "ORDER BY count DESC"
            ))
            for row in result:
                print(f"   {row[0]}: {row[1]:,} passengers")
            print()
            
            # Test 5: Flight status
            print("=" * 60)
            print("TEST 5: Flight Status Distribution")
            print("=" * 60)
            result = conn.execute(text(
                "SELECT flight_status, COUNT(*) as count "
                "FROM aviation_data "
                "GROUP BY flight_status "
                "ORDER BY count DESC"
            ))
            for row in result:
                print(f"   {row[0]}: {row[1]:,} flights")
            print()
            
            print("=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print()
            print("✅ Your Snowflake connection is working perfectly!")
            print("✅ Data is accessible and queryable")
            print("✅ Ready to use with your Streamlit app!")
            print()
            print("Next step: Update DATABASE_TYPE=snowflake in your .env file")
            print("Then run: streamlit run app.py")
            
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ CONNECTION FAILED")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("💡 Troubleshooting Steps:")
        print()
        print("1. CHECK CREDENTIALS:")
        print("   • Open your .env file")
        print("   • Verify SNOWFLAKE_ACCOUNT format (e.g., abc12345.us-east-1)")
        print("   • Check username and password are correct")
        print()
        print("2. CHECK SNOWFLAKE ACCOUNT:")
        print("   • Login to Snowflake web UI")
        print("   • Verify your account is active")
        print("   • Check warehouse is running or set to auto-resume")
        print()
        print("3. CHECK DATABASE/TABLE:")
        print("   • Run: SHOW DATABASES;")
        print("   • Run: SHOW SCHEMAS IN DATABASE aviation_db;")
        print("   • Run: SHOW TABLES IN SCHEMA aviation_db.analytics;")
        print()
        print("4. CHECK NETWORK:")
        print("   • Verify internet connection")
        print("   • Check firewall settings")
        print("   • Try from different network if issues persist")
        print()
        print("5. VERIFY PACKAGES:")
        print("   • Run: pip install snowflake-connector-python snowflake-sqlalchemy")
        print()

if __name__ == "__main__":
    try:
        test_snowflake_connection()
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        print()
        print("Make sure you have installed:")
        print("  pip install snowflake-connector-python snowflake-sqlalchemy python-dotenv")
