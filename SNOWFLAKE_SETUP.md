# ❄️ Snowflake Integration Guide - Aviation BI Chatbot

## 🎯 Quick Setup Guide

This guide will help you replace SQLite with Snowflake for enterprise-scale data warehousing.

---

## 📦 Step 1: Install Snowflake Connector

Run this command in your terminal:

```bash
pip install snowflake-connector-python snowflake-sqlalchemy
```

---

## ❄️ Step 2: Set Up Snowflake Account

### Create Free Account

1. Go to: https://signup.snowflake.com/
2. Sign up for **free trial** (30 days, $400 credit)
3. Choose your cloud provider and region
4. Complete registration

### Note Your Account Information

After signing up, you'll get:

- **Account Identifier**: `abc12345.us-east-1` (example)
- **Username**: your email or chosen username
- **Password**: your password
- **Warehouse**: `COMPUTE_WH` (default)

---

## 🗄️ Step 3: Create Database and Table in Snowflake

### 📝 Using Snowflake Web UI (Recommended - Easy!)

**Step-by-step with screenshots:**

1. **Login to Snowflake**:

   - Go to: https://app.snowflake.com/
   - Enter your username and password

2. **Navigate to Worksheets**:

   - Look at the **LEFT SIDEBAR**
   - Click on **"Projects"** (or you might see **"Worksheets"** directly)
   - If you see "Projects", click on it first
   - Then click **"Worksheets"**

3. **Create a New Worksheet**:

   - Click the **"+ Worksheet"** button (top right corner)
   - OR click the blue **"+"** button
   - A new blank worksheet will open

4. **Select Your Warehouse**:

   - At the top right of the worksheet, you'll see a dropdown
   - Select **"COMPUTE_WH"** (or your default warehouse)
   - Make sure it says "Running" (green dot) or "Resuming"

5. **Copy and Paste ALL this SQL** into the worksheet:

```sql
-- Step 1: Create database
CREATE DATABASE aviation_db;

-- Step 2: Use the database
USE DATABASE aviation_db;

-- Step 3: Create schema
CREATE SCHEMA analytics;

-- Step 4: Use the schema
USE SCHEMA analytics;

-- Step 5: Create table
CREATE TABLE aviation_data (
    passenger_id VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(50),
    age INTEGER,
    nationality VARCHAR(100),
    airport_name VARCHAR(200),
    airport_country_code VARCHAR(10),
    country_name VARCHAR(100),
    airport_continent VARCHAR(50),
    continents VARCHAR(50),
    departure_date DATE,
    arrival_airport VARCHAR(200),
    pilot_name VARCHAR(100),
    flight_status VARCHAR(50)
);

-- Step 6: Verify table was created
SHOW TABLES;

-- Step 7: Check table structure
DESCRIBE TABLE aviation_data;
```

6. **Run the SQL**:

   - Click the **blue "Run" button** at the top (▶️ Play button)
   - OR press `Ctrl + Enter`
   - You should see "Statement executed successfully" messages

7. **Verify Everything Worked**:
   - At the bottom, you should see results showing:
     - Database created ✅
     - Schema created ✅
     - Table created ✅
   - The `SHOW TABLES;` command should display `aviation_data`

### 🔍 **Troubleshooting Worksheet Issues:**

**Problem: Can't find Worksheets in sidebar?**

- Try clicking **"Projects"** → **"Worksheets"**
- Or look for **"SQL Worksheets"**
- The UI might look slightly different based on your Snowflake version

**Problem: Sidebar isn't updating?**

- **Refresh your browser** (F5)
- **Clear cache**: Ctrl + Shift + Delete
- Try a different browser (Chrome recommended)
- Log out and log back in

**Problem: "Warehouse not available" error?**

- Select warehouse from dropdown at top-right
- Make sure warehouse is running (green indicator)
- If suspended, it will auto-resume when you run SQL

**Problem: Can't click Run button?**

- Make sure you've selected a warehouse (top-right dropdown)
- Check that SQL is pasted in the worksheet
- Try clicking directly on the SQL text first

### ✅ **What Success Looks Like:**

After running the SQL, you should see in the **Results** pane (bottom):

```
✓ Database AVIATION_DB successfully created.
✓ Schema ANALYTICS successfully created.
✓ Table AVIATION_DATA successfully created.
```

And `SHOW TABLES;` should show:

```
name: AVIATION_DATA
database_name: AVIATION_DB
schema_name: ANALYTICS
```

---

### 🔄 **Alternative: If Worksheets Don't Load**

If you're having persistent UI issues, you can use **SnowSQL** (command line):

1. **Download SnowSQL**: https://docs.snowflake.com/en/user-guide/snowsql-install-config.html
2. **Connect**:
   ```bash
   snowsql -a <your_account> -u <your_username>
   ```
3. **Paste and run the SQL** from above

But **Worksheets UI is recommended** for beginners!

---

## 🔑 Step 4: Update Your .env File

Add these lines to your `.env` file:

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=aviation_db
SNOWFLAKE_SCHEMA=analytics
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN

# Set database type
DATABASE_TYPE=snowflake
```

### How to find your account identifier:

1. Login to Snowflake
2. Look at the URL: `https://app.snowflake.com/abc12345/us-east-1/...`
3. Your account is: `abc12345.us-east-1`

---

## 💾 Step 5: Load Data to Snowflake

Create a new file `load_data_to_snowflake.py`:

```python
import pandas as pd
import os
from dotenv import load_dotenv
from snowflake.connector import connect
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

load_dotenv()

def load_data_to_snowflake():
    """Load CSV data to Snowflake"""

    print("🔄 Starting data load to Snowflake...")

    # Create Snowflake connection
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

    # Read CSV file
    print("📂 Reading CSV file...")
    df = pd.read_csv('Airline_Dataset.csv')

    # Clean column names (match table schema)
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

    # Convert date column
    df['departure_date'] = pd.to_datetime(df['departure_date'])

    print(f"📊 Loaded {len(df):,} rows from CSV")
    print(f"📋 Columns: {', '.join(df.columns)}")

    # Write to Snowflake
    print("⬆️ Uploading to Snowflake...")
    df.to_sql(
        'aviation_data',
        engine,
        if_exists='replace',  # Change to 'append' if you want to add data
        index=False,
        chunksize=5000,
        method='multi'
    )

    print(f"✅ Successfully loaded {len(df):,} rows to Snowflake!")
    print(f"📍 Database: {os.getenv('SNOWFLAKE_DATABASE')}")
    print(f"📍 Schema: {os.getenv('SNOWFLAKE_SCHEMA')}")
    print(f"📍 Table: aviation_data")

    # Verify data
    with engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) as count FROM aviation_data")
        row_count = result.fetchone()[0]
        print(f"\n🔍 Verification: {row_count:,} rows in Snowflake table")

if __name__ == "__main__":
    try:
        load_data_to_snowflake()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("1. Check your .env file has correct Snowflake credentials")
        print("2. Verify table exists in Snowflake")
        print("3. Make sure Airline_Dataset.csv is in the same folder")
```

Run it:

```bash
python load_data_to_snowflake.py
```

---

## 🔧 Step 6: Update app.py

Find the line where the engine is created (around line 17-18):

```python
engine = create_engine("sqlite:///aviation.db")
```

Replace the entire database connection section with:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

load_dotenv()

# Database configuration
def get_database_engine():
    """Get database engine - supports SQLite (dev) and Snowflake (prod)"""
    db_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()

    if db_type == 'snowflake':
        connection_url = URL(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        )
        return create_engine(connection_url)
    else:
        # Default to SQLite for development
        return create_engine("sqlite:///aviation.db")

engine = get_database_engine()
```

---

## ✅ Step 7: Test Connection

Create `test_snowflake.py`:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL

load_dotenv()

def test_snowflake_connection():
    """Test Snowflake connection and query data"""

    print("🔄 Testing Snowflake connection...")

    try:
        # Create connection
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
            # Test 1: Count rows
            result = conn.execute(text("SELECT COUNT(*) as count FROM aviation_data"))
            count = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 Total rows in aviation_data: {count:,}")

            # Test 2: Sample data
            result = conn.execute(text("SELECT * FROM aviation_data LIMIT 5"))
            print(f"\n📋 Sample data:")
            rows = result.fetchall()
            for i, row in enumerate(rows, 1):
                print(f"  Row {i}: {row[1]} {row[2]} - {row[5]}")  # First name, Last name, Nationality

            # Test 3: Aggregation query
            result = conn.execute(text("SELECT nationality, COUNT(*) as count FROM aviation_data GROUP BY nationality ORDER BY count DESC LIMIT 5"))
            print(f"\n🌍 Top 5 Nationalities:")
            for row in result:
                print(f"  {row[0]}: {row[1]:,} passengers")

            print("\n🎉 All tests passed! Snowflake is ready to use!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your .env file has correct credentials")
        print("2. Verify your Snowflake account is active")
        print("3. Ensure the table 'aviation_data' exists")
        print("4. Check your network connection")

if __name__ == "__main__":
    test_snowflake_connection()
```

Run it:

```bash
python test_snowflake.py
```

---

## 🚀 Step 8: Run Your App

```bash
streamlit run app.py
```

Your app will now use Snowflake instead of SQLite! 🎉

---

## 🔄 Switching Between SQLite and Snowflake

In your `.env` file, simply change:

```env
# Use Snowflake
DATABASE_TYPE=snowflake

# Or use SQLite (for local development)
DATABASE_TYPE=sqlite
```

---

## 📊 Update Table Schema in Prompt

Update the `AVIATION_SCHEMA` variable in `app.py` to match Snowflake column names (lowercase with underscores):

```python
AVIATION_SCHEMA = (
    "aviation_data table schema:\n"
    "passenger_id (VARCHAR), first_name (VARCHAR), last_name (VARCHAR), "
    "gender (VARCHAR), age (INTEGER), nationality (VARCHAR), airport_name (VARCHAR), "
    "airport_country_code (VARCHAR), country_name (VARCHAR), airport_continent (VARCHAR), "
    "continents (VARCHAR), departure_date (DATE), arrival_airport (VARCHAR), "
    "pilot_name (VARCHAR), flight_status (VARCHAR)"
)
```

---

## 💰 Snowflake Costs

### Free Trial

- **$400 credit**
- **30 days**
- Perfect for testing and development

### After Trial (Pay-as-you-go)

- **Compute**: ~$2-4 per hour (only when warehouse is running)
- **Storage**: ~$40 per TB per month
- **For small datasets**: Usually < $10/month

### Cost Optimization Tips

1. **Auto-suspend warehouse** (stops when idle)
2. **Use smaller warehouse** (X-Small for development)
3. **Resume only when needed**
4. **Monitor query costs** in Snowflake UI

---

## 🔒 Security Best Practices

### 1. Credentials

```env
# Never commit .env to Git!
# Use strong passwords
# Rotate credentials regularly
```

### 2. Network Security

- Enable network policies in Snowflake
- Whitelist your IP address
- Use VPN for production

### 3. Access Control

```sql
-- Create read-only role for app
CREATE ROLE aviation_app_role;
GRANT USAGE ON DATABASE aviation_db TO ROLE aviation_app_role;
GRANT USAGE ON SCHEMA analytics TO ROLE aviation_app_role;
GRANT SELECT ON TABLE aviation_data TO ROLE aviation_app_role;
GRANT USAGE ON WAREHOUSE compute_wh TO ROLE aviation_app_role;

-- Create user for app
CREATE USER aviation_app_user PASSWORD='strong_password_here';
GRANT ROLE aviation_app_role TO USER aviation_app_user;
```

Then use this user in your `.env`:

```env
SNOWFLAKE_USER=aviation_app_user
SNOWFLAKE_PASSWORD=strong_password_here
SNOWFLAKE_ROLE=aviation_app_role
```

---

## 🐛 Troubleshooting

### Error: "Account not found"

**Solution**: Check your account identifier format

```env
# Correct format
SNOWFLAKE_ACCOUNT=abc12345.us-east-1

# Not just
SNOWFLAKE_ACCOUNT=abc12345
```

### Error: "Invalid username or password"

**Solution**:

- Verify credentials in Snowflake UI
- Check for typos in .env
- Ensure password doesn't have special characters that need escaping

### Error: "Object does not exist"

**Solution**:

- Verify database and schema names
- Check table was created
- Run: `SHOW TABLES IN SCHEMA aviation_db.analytics;`

### Error: "Warehouse does not exist"

**Solution**:

- Create warehouse: `CREATE WAREHOUSE compute_wh;`
- Or use existing warehouse name

### Connection Timeout

**Solution**:

- Check firewall settings
- Verify network connection
- Try from different network

---

## 📈 Performance Tips

### 1. Add Indexes (Clustering Keys)

```sql
ALTER TABLE aviation_data CLUSTER BY (departure_date, nationality);
```

### 2. Use Caching

Snowflake automatically caches query results for 24 hours

### 3. Optimize Warehouse Size

```sql
-- Start with X-Small for development
ALTER WAREHOUSE compute_wh SET WAREHOUSE_SIZE = 'X-SMALL';

-- Scale up for production
ALTER WAREHOUSE compute_wh SET WAREHOUSE_SIZE = 'SMALL';
```

### 4. Auto-Suspend

```sql
-- Suspend after 5 minutes of inactivity
ALTER WAREHOUSE compute_wh SET AUTO_SUSPEND = 300;
ALTER WAREHOUSE compute_wh SET AUTO_RESUME = TRUE;
```

---

## ✅ Checklist

- [ ] Snowflake account created
- [ ] Packages installed (`pip install snowflake-connector-python snowflake-sqlalchemy`)
- [ ] Database and table created in Snowflake
- [ ] `.env` file updated with Snowflake credentials
- [ ] Data loaded to Snowflake (`load_data_to_snowflake.py`)
- [ ] Connection tested (`test_snowflake.py`)
- [ ] `app.py` updated with Snowflake connection
- [ ] App tested with Streamlit

---

## 🎉 You're Done!

Your Aviation BI Chatbot is now powered by Snowflake!

### Benefits You Now Have:

✅ Enterprise-scale data warehousing  
✅ Cloud-based (access from anywhere)  
✅ Handles massive datasets  
✅ Multiple concurrent users  
✅ Automatic backups  
✅ Advanced analytics capabilities

---

## 📚 Resources

- **Snowflake Docs**: https://docs.snowflake.com/
- **Python Connector**: https://docs.snowflake.com/en/user-guide/python-connector.html
- **SQLAlchemy**: https://docs.snowflake.com/en/user-guide/sqlalchemy.html
- **Free Trial**: https://signup.snowflake.com/

---

**Need help?** Check the Snowflake documentation or contact support!
