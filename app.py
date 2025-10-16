import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import requests
import hashlib
import os
from snowflake.sqlalchemy import URL


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"



def get_database_engine():
    
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
        
        return create_engine("sqlite:///aviation.db")

engine = get_database_engine()


if os.getenv('DATABASE_TYPE', 'sqlite').lower() == 'snowflake':
    db_info = f"❄️ Snowflake: {os.getenv('SNOWFLAKE_DATABASE')}.{os.getenv('SNOWFLAKE_SCHEMA')}"
else:
    db_info = "💾 SQLite (Local)"



USERS = {
    os.getenv("USER1_USERNAME", "admin"): os.getenv("USER1_PASSWORD", "admin123"),
    os.getenv("USER2_USERNAME", "analyst"): os.getenv("USER2_PASSWORD", "analyst123"),
}


def hash_password(password):
   
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(username, password):
    
    if username in USERS:
        return USERS[username] == password
    return False


def login_page():
   
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔒 Login")
        st.markdown("### Aviation BI Chatbot")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                elif check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("---")
        st.info("💡 **Demo Credentials:**\n\n**Username:** admin | **Password:** admin123\n\n**Username:** analyst | **Password:** analyst123")


def logout():
   
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.conversation_history = []
    st.session_state.query_count = 0
    st.rerun()



if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = None



if not st.session_state.authenticated:
    login_page()
    st.stop()


AVIATION_SCHEMA = (
    "aviation_data table schema:\n"
    "passenger_id (VARCHAR), first_name (VARCHAR), last_name (VARCHAR), "
    "gender (VARCHAR), age (INTEGER), nationality (VARCHAR), airport_name (VARCHAR), "
    "airport_country_code (VARCHAR), country_name (VARCHAR), airport_continent (VARCHAR), "
    "continents (VARCHAR), departure_date (DATE), arrival_airport (VARCHAR), "
    "pilot_name (VARCHAR), flight_status (VARCHAR)"
)


def generate_sql(nl_query):
   
    prompt = (
        f"{AVIATION_SCHEMA}\n\n"
        "Translate this natural language query into a SQLite-compatible SELECT SQL query for the aviation_data table only. "
        "IMPORTANT: You MUST enclose column names with spaces (e.g., \"Passenger ID\") in double quotes. "
        f"Natural Language Query: {nl_query}"
    )
   
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
   
    response = requests.post(API_URL, headers=headers, params=params, json=data)
    result = response.json()
    st.code(f"Full Gemini API response:\n{result}", language="json")


    sql = ""
    try:
       
        generated_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
       
   
        if generated_text.startswith("```"):
           
            sql = generated_text.rstrip('`').strip()
           
            first_newline_index = sql.find('\n')
           
            if first_newline_index != -1:
                sql = sql[first_newline_index + 1:].strip()
            else:


                parts = sql.split(' ', 1)
                if len(parts) > 1:
                    sql = parts[1].strip()
                else:
                    sql = ""
        else:
            sql = generated_text
       
           
    except Exception as e:
        st.error(f"Error parsing Gemini response: {e}. Check the response structure.")
        sql = ""
       
    return sql




def run_query(sql):
    if not sql.lower().strip().startswith("select"):
        st.warning("Generated query is not a SELECT statement. Please ask a question that retrieves data.")
        return None
    try:
   
        return pd.read_sql(sql, engine)
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        st.error(f"Failed query: {sql}")
        return None


def create_smart_visualizations(results, query):

    import numpy as np
    from matplotlib import pyplot as plt
    import seaborn as sns
    

    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    
    numeric_cols = results.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = results.select_dtypes(exclude=['number']).columns.tolist()
    date_cols = [col for col in results.columns if 'date' in col.lower() or 'time' in col.lower()]
    
    num_rows = len(results)
    
    # Case 1: Single numeric column 
    if len(numeric_cols) == 1 and len(categorical_cols) == 0:
        return create_single_numeric_viz(results, numeric_cols[0])
    
    # Case 2: Multiple numeric columns only (Correlation, distribution)
    if len(numeric_cols) >= 2 and len(categorical_cols) == 0:
        return create_multi_numeric_viz(results, numeric_cols)
    
    # Case 3: One categorical + one numeric (Classic comparison)
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        n_unique = results[cat_col].nunique()
        
        # Sub-case: Time series data
        if cat_col in date_cols or 'date' in cat_col.lower():
            return create_time_series_viz(results, cat_col, num_col)
        
        # Sub-case: Few categories (2-20)
        if 2 <= n_unique <= 20:
            return create_categorical_comparison_viz(results, cat_col, num_col, n_unique)
        
        # Sub-case: Many categories (>20)
        if n_unique > 20:
            return create_top_n_viz(results, cat_col, num_col, top_n=15)
    
    # Case 4: Multiple categorical columns (Cross-tabulation)
    if len(categorical_cols) >= 2:
        return create_cross_tab_viz(results, categorical_cols[:2])
    
    # Case 5: Large dataset overview (Sample visualization)
    if num_rows > 100:
        return create_large_dataset_viz(results, numeric_cols, categorical_cols)
    
    # Default: Simple table representation
    return None


def create_single_numeric_viz(results, col_name):
    """Visualize single numeric column with histogram and box plot"""
    fig, axs = plt.subplots(1, 3, figsize=(16, 5))
    
    data = results[col_name].dropna()
    
    # Histogram
    axs[0].hist(data, bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
    axs[0].set_title(f'Distribution of {col_name}', fontsize=12, fontweight='bold')
    axs[0].set_xlabel(col_name)
    axs[0].set_ylabel('Frequency')
    axs[0].grid(alpha=0.3)
    
    # Box plot
    axs[1].boxplot(data, vert=True)
    axs[1].set_title(f'Box Plot of {col_name}', fontsize=12, fontweight='bold')
    axs[1].set_ylabel(col_name)
    axs[1].grid(alpha=0.3)
    
    # Statistics
    axs[2].axis('off')
    stats_text = f"""
    📊 Summary Statistics
    
    Count: {len(data):,}
    Mean: {data.mean():.2f}
    Median: {data.median():.2f}
    Std Dev: {data.std():.2f}
    Min: {data.min():.2f}
    Max: {data.max():.2f}
    """
    axs[2].text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    return fig


def create_multi_numeric_viz(results, numeric_cols):
    """Visualize multiple numeric columns with correlation and scatter plots"""
    n_cols = min(len(numeric_cols), 4)  # Limit to 4 columns for clarity
    selected_cols = numeric_cols[:n_cols]
    
    fig = plt.figure(figsize=(16, 10))
    
    # Correlation heatmap
    ax1 = plt.subplot(2, 2, 1)
    corr_matrix = results[selected_cols].corr()
    im = ax1.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    ax1.set_xticks(range(len(selected_cols)))
    ax1.set_yticks(range(len(selected_cols)))
    ax1.set_xticklabels(selected_cols, rotation=45, ha='right')
    ax1.set_yticklabels(selected_cols)
    ax1.set_title('Correlation Matrix', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax1)
    
    # Add correlation values
    for i in range(len(selected_cols)):
        for j in range(len(selected_cols)):
            ax1.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                    ha='center', va='center', color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black')
    
    # Scatter plot (first two numeric columns)
    if len(selected_cols) >= 2:
        ax2 = plt.subplot(2, 2, 2)
        ax2.scatter(results[selected_cols[0]], results[selected_cols[1]], 
                   alpha=0.6, c='#A23B72', edgecolors='black', linewidth=0.5)
        ax2.set_xlabel(selected_cols[0])
        ax2.set_ylabel(selected_cols[1])
        ax2.set_title(f'{selected_cols[1]} vs {selected_cols[0]}', fontsize=12, fontweight='bold')
        ax2.grid(alpha=0.3)
    
    # Distribution comparison
    ax3 = plt.subplot(2, 2, 3)
    for col in selected_cols[:3]:  # Limit to 3 for readability
        ax3.hist(results[col].dropna(), bins=20, alpha=0.5, label=col)
    ax3.set_title('Distribution Comparison', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Value')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # Box plots comparison
    ax4 = plt.subplot(2, 2, 4)
    ax4.boxplot([results[col].dropna() for col in selected_cols], labels=selected_cols)
    ax4.set_title('Box Plot Comparison', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Value')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_time_series_viz(results, date_col, value_col):
    """Create time series visualizations"""
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    
    # Sort by date
    df_sorted = results.sort_values(date_col)
    
    # Line chart
    axs[0, 0].plot(df_sorted[date_col], df_sorted[value_col], marker='o', linewidth=2, markersize=4, color='#2E86AB')
    axs[0, 0].set_title(f'{value_col} Over Time', fontsize=12, fontweight='bold')
    axs[0, 0].set_xlabel(date_col)
    axs[0, 0].set_ylabel(value_col)
    axs[0, 0].tick_params(axis='x', rotation=45)
    axs[0, 0].grid(alpha=0.3)
    
    # Area chart
    axs[0, 1].fill_between(range(len(df_sorted)), df_sorted[value_col], alpha=0.6, color='#A23B72')
    axs[0, 1].plot(df_sorted[value_col], linewidth=2, color='#6C1D45')
    axs[0, 1].set_title(f'{value_col} Trend (Area)', fontsize=12, fontweight='bold')
    axs[0, 1].set_xlabel('Observation')
    axs[0, 1].set_ylabel(value_col)
    axs[0, 1].grid(alpha=0.3)
    
    # Moving average (if enough data points)
    if len(df_sorted) >= 5:
        window = min(5, len(df_sorted) // 3)
        moving_avg = df_sorted[value_col].rolling(window=window).mean()
        axs[1, 0].plot(df_sorted[value_col], alpha=0.5, label='Actual', color='lightblue')
        axs[1, 0].plot(moving_avg, linewidth=2, label=f'{window}-period MA', color='red')
        axs[1, 0].set_title(f'{value_col} with Moving Average', fontsize=12, fontweight='bold')
        axs[1, 0].set_xlabel('Observation')
        axs[1, 0].set_ylabel(value_col)
        axs[1, 0].legend()
        axs[1, 0].grid(alpha=0.3)
    
    # Cumulative sum
    cumsum = df_sorted[value_col].cumsum()
    axs[1, 1].plot(cumsum, linewidth=2, color='#F18F01')
    axs[1, 1].set_title(f'Cumulative {value_col}', fontsize=12, fontweight='bold')
    axs[1, 1].set_xlabel('Observation')
    axs[1, 1].set_ylabel(f'Cumulative {value_col}')
    axs[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_categorical_comparison_viz(results, cat_col, num_col, n_unique):
    """Create comprehensive visualizations for categorical vs numeric data"""
    # Aggregate data
    agg_data = results.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count']).reset_index()
    agg_data = agg_data.sort_values('sum', ascending=False)
    
    # Decide number of charts based on categories
    if n_unique <= 6:
        fig, axs = plt.subplots(2, 3, figsize=(18, 10))
        axs = axs.flatten()
    else:
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        axs = axs.flatten()
    
    chart_idx = 0
    
    # 1. Bar chart (Sum)
    axs[chart_idx].bar(agg_data[cat_col], agg_data['sum'], color='#4C72B0', edgecolor='black')
    axs[chart_idx].set_title(f'Total {num_col} by {cat_col}', fontsize=12, fontweight='bold')
    axs[chart_idx].set_xlabel(cat_col)
    axs[chart_idx].set_ylabel(f'Total {num_col}')
    axs[chart_idx].tick_params(axis='x', rotation=45)
    axs[chart_idx].grid(alpha=0.3, axis='y')
    chart_idx += 1
    
    # 2. Horizontal bar chart (for better readability with many categories)
    axs[chart_idx].barh(agg_data[cat_col], agg_data['sum'], color='#55A630', edgecolor='black')
    axs[chart_idx].set_title(f'Total {num_col} by {cat_col} (Horizontal)', fontsize=12, fontweight='bold')
    axs[chart_idx].set_xlabel(f'Total {num_col}')
    axs[chart_idx].set_ylabel(cat_col)
    axs[chart_idx].grid(alpha=0.3, axis='x')
    chart_idx += 1
    
    # 3. Pie chart (only if reasonable number of categories)
    if n_unique <= 8:
        colors = plt.cm.Set3(range(len(agg_data)))
        axs[chart_idx].pie(agg_data['sum'], labels=agg_data[cat_col], autopct='%1.1f%%', 
                          startangle=90, colors=colors)
        axs[chart_idx].set_title(f'{num_col} Distribution by {cat_col}', fontsize=12, fontweight='bold')
        chart_idx += 1
    
    # 4. Average comparison
    axs[chart_idx].bar(agg_data[cat_col], agg_data['mean'], color='#F77F00', edgecolor='black')
    axs[chart_idx].set_title(f'Average {num_col} by {cat_col}', fontsize=12, fontweight='bold')
    axs[chart_idx].set_xlabel(cat_col)
    axs[chart_idx].set_ylabel(f'Average {num_col}')
    axs[chart_idx].tick_params(axis='x', rotation=45)
    axs[chart_idx].axhline(agg_data['mean'].mean(), color='red', linestyle='--', label='Overall Mean')
    axs[chart_idx].legend()
    axs[chart_idx].grid(alpha=0.3, axis='y')
    chart_idx += 1
    
    # 5. Count bar chart
    if chart_idx < len(axs):
        axs[chart_idx].bar(agg_data[cat_col], agg_data['count'], color='#C9184A', edgecolor='black')
        axs[chart_idx].set_title(f'Count by {cat_col}', fontsize=12, fontweight='bold')
        axs[chart_idx].set_xlabel(cat_col)
        axs[chart_idx].set_ylabel('Count')
        axs[chart_idx].tick_params(axis='x', rotation=45)
        axs[chart_idx].grid(alpha=0.3, axis='y')
        chart_idx += 1
    
    # 6. Line chart (showing trend)
    if chart_idx < len(axs):
        axs[chart_idx].plot(agg_data[cat_col], agg_data['sum'], marker='o', linewidth=2, 
                           markersize=8, color='#9D4EDD')
        axs[chart_idx].set_title(f'{num_col} Trend by {cat_col}', fontsize=12, fontweight='bold')
        axs[chart_idx].set_xlabel(cat_col)
        axs[chart_idx].set_ylabel(f'Total {num_col}')
        axs[chart_idx].tick_params(axis='x', rotation=45)
        axs[chart_idx].grid(alpha=0.3)
        chart_idx += 1
    
    # Hide unused subplots
    for idx in range(chart_idx, len(axs)):
        axs[idx].axis('off')
    
    plt.tight_layout()
    return fig


def create_top_n_viz(results, cat_col, num_col, top_n=15):
    """Create visualizations for categories with many unique values (show top N)"""
    agg_data = results.groupby(cat_col)[num_col].sum().reset_index()
    agg_data = agg_data.sort_values(num_col, ascending=False).head(top_n)
    
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    
    # 1. Bar chart (Top N)
    axs[0, 0].bar(range(len(agg_data)), agg_data[num_col], color='#4C72B0', edgecolor='black')
    axs[0, 0].set_title(f'Top {top_n} {cat_col} by {num_col}', fontsize=12, fontweight='bold')
    axs[0, 0].set_xlabel(cat_col)
    axs[0, 0].set_ylabel(num_col)
    axs[0, 0].set_xticks(range(len(agg_data)))
    axs[0, 0].set_xticklabels(agg_data[cat_col], rotation=45, ha='right')
    axs[0, 0].grid(alpha=0.3, axis='y')
    
    # 2. Horizontal bar chart
    axs[0, 1].barh(agg_data[cat_col], agg_data[num_col], color='#55A630', edgecolor='black')
    axs[0, 1].set_title(f'Top {top_n} {cat_col} (Horizontal)', fontsize=12, fontweight='bold')
    axs[0, 1].set_xlabel(num_col)
    axs[0, 1].set_ylabel(cat_col)
    axs[0, 1].invert_yaxis()
    axs[0, 1].grid(alpha=0.3, axis='x')
    
    # 3. Pareto chart (cumulative percentage)
    cumsum = agg_data[num_col].cumsum()
    cumsum_pct = cumsum / agg_data[num_col].sum() * 100
    
    ax3 = axs[1, 0]
    ax3_twin = ax3.twinx()
    
    ax3.bar(range(len(agg_data)), agg_data[num_col], color='#F77F00', alpha=0.7, edgecolor='black')
    ax3_twin.plot(range(len(agg_data)), cumsum_pct, color='red', marker='D', linewidth=2, markersize=6)
    ax3_twin.axhline(80, color='green', linestyle='--', label='80%')
    
    ax3.set_xlabel(cat_col)
    ax3.set_ylabel(num_col, color='#F77F00')
    ax3_twin.set_ylabel('Cumulative %', color='red')
    ax3.set_title(f'Pareto Chart: Top {top_n} {cat_col}', fontsize=12, fontweight='bold')
    ax3.set_xticks(range(len(agg_data)))
    ax3.set_xticklabels(agg_data[cat_col], rotation=45, ha='right')
    ax3_twin.legend(loc='center right')
    ax3.grid(alpha=0.3, axis='y')
    
    # 4. Comparison with "Others"
    top_sum = agg_data[num_col].sum()
    total_sum = results.groupby(cat_col)[num_col].sum().sum()
    others_sum = total_sum - top_sum
    
    labels = [f'Top {top_n}', 'Others']
    sizes = [top_sum, others_sum]
    colors = ['#4C72B0', '#CCCCCC']
    
    axs[1, 1].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    axs[1, 1].set_title(f'Top {top_n} vs Others', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_cross_tab_viz(results, cat_cols):
    """Create cross-tabulation visualization for two categorical columns"""
    cat1, cat2 = cat_cols[0], cat_cols[1]
    
    # Limit categories for visualization
    top_cat1 = results[cat1].value_counts().head(10).index
    top_cat2 = results[cat2].value_counts().head(10).index
    
    filtered_results = results[results[cat1].isin(top_cat1) & results[cat2].isin(top_cat2)]
    
    crosstab = pd.crosstab(filtered_results[cat1], filtered_results[cat2])
    
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    
    # Heatmap
    im = axs[0].imshow(crosstab.values, cmap='YlOrRd', aspect='auto')
    axs[0].set_xticks(range(len(crosstab.columns)))
    axs[0].set_yticks(range(len(crosstab.index)))
    axs[0].set_xticklabels(crosstab.columns, rotation=45, ha='right')
    axs[0].set_yticklabels(crosstab.index)
    axs[0].set_title(f'Cross-tabulation: {cat1} vs {cat2}', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=axs[0])
    
    # Stacked bar chart
    crosstab.plot(kind='bar', stacked=True, ax=axs[1], colormap='Set3', edgecolor='black')
    axs[1].set_title(f'{cat1} by {cat2} (Stacked)', fontsize=12, fontweight='bold')
    axs[1].set_xlabel(cat1)
    axs[1].set_ylabel('Count')
    axs[1].tick_params(axis='x', rotation=45)
    axs[1].legend(title=cat2, bbox_to_anchor=(1.05, 1), loc='upper left')
    axs[1].grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig


def create_large_dataset_viz(results, numeric_cols, categorical_cols):
    """Create overview visualizations for large datasets"""
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    
    # Sample data for visualization
    sample_size = min(1000, len(results))
    sample_data = results.sample(sample_size)
    
    # 1. Data overview
    axs[0, 0].axis('off')
    overview_text = f"""
    📊 Dataset Overview
    
    Total Rows: {len(results):,}
    Total Columns: {len(results.columns)}
    Numeric Columns: {len(numeric_cols)}
    Categorical Columns: {len(categorical_cols)}
    
    Sample Size: {sample_size:,} rows
    """
    axs[0, 0].text(0.1, 0.5, overview_text, fontsize=12, verticalalignment='center',
                  bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # 2. Numeric columns distribution (if available)
    if numeric_cols:
        col = numeric_cols[0]
        axs[0, 1].hist(sample_data[col].dropna(), bins=30, color='#4C72B0', alpha=0.7, edgecolor='black')
        axs[0, 1].set_title(f'Distribution of {col} (Sample)', fontsize=12, fontweight='bold')
        axs[0, 1].set_xlabel(col)
        axs[0, 1].set_ylabel('Frequency')
        axs[0, 1].grid(alpha=0.3)
    
    # 3. Categorical distribution (if available)
    if categorical_cols:
        col = categorical_cols[0]
        top_categories = sample_data[col].value_counts().head(15)
        axs[1, 0].barh(range(len(top_categories)), top_categories.values, color='#55A630', edgecolor='black')
        axs[1, 0].set_yticks(range(len(top_categories)))
        axs[1, 0].set_yticklabels(top_categories.index)
        axs[1, 0].set_title(f'Top Categories in {col} (Sample)', fontsize=12, fontweight='bold')
        axs[1, 0].set_xlabel('Count')
        axs[1, 0].invert_yaxis()
        axs[1, 0].grid(alpha=0.3, axis='x')
    
    # 4. Multi-column correlation (if multiple numeric columns)
    if len(numeric_cols) >= 2:
        cols_to_plot = numeric_cols[:min(5, len(numeric_cols))]
        corr_matrix = sample_data[cols_to_plot].corr()
        im = axs[1, 1].imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        axs[1, 1].set_xticks(range(len(cols_to_plot)))
        axs[1, 1].set_yticks(range(len(cols_to_plot)))
        axs[1, 1].set_xticklabels(cols_to_plot, rotation=45, ha='right')
        axs[1, 1].set_yticklabels(cols_to_plot)
        axs[1, 1].set_title('Correlation Matrix (Sample)', fontsize=12, fontweight='bold')
        plt.colorbar(im, ax=axs[1, 1])
    
    plt.tight_layout()
    return fig


# Header with user info and logout
col1, col2 = st.columns([4, 1])
with col1:
    st.title("✈️ Aviation Conversational BI Chatbot")
    st.markdown("Ask questions about flights, and I'll analyze the data for you!")
    st.caption(f"📊 Data Source: {db_info}")
with col2:
    st.markdown(f"**👤 {st.session_state.username}**")
    if st.button("🚪 Logout", use_container_width=True):
        logout()

st.markdown("---")

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Display conversation history
if st.session_state.conversation_history:
    st.markdown("### 💬 Conversation History")
    for i, entry in enumerate(st.session_state.conversation_history):
        with st.container():
            # User message
            st.markdown(f"**🧑 You:** {entry['user_query']}")
            
            # Bot response
            with st.expander(f"🤖 Assistant Response #{i+1}", expanded=(i == len(st.session_state.conversation_history) - 1)):
                st.markdown(f"**Generated SQL:**")
                st.code(entry['sql'], language="sql")
                
                if entry['results'] is not None and not entry['results'].empty:
                    st.markdown(f"**Query Results:** ({len(entry['results'])} rows)")
                    st.dataframe(entry['results'], use_container_width=True)
                    
                    # Display chart if available
                    if 'chart' in entry and entry['chart'] is not None:
                        st.pyplot(entry['chart'])
                else:
                    st.warning(entry.get('error', 'No results returned.'))
            
            st.markdown("---")

# Input area at the bottom
st.markdown("### 💭 Ask a new question")
col1, col2 = st.columns([5, 1])

with col1:
    user_query = st.text_input(
        "Your question:",
        placeholder="e.g., 'Count passengers by Nationality' or 'Show top 5 airports'",
        key=f"user_input_{st.session_state.query_count}",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤 Send", type="primary", use_container_width=True)
    
# Clear history button
if st.session_state.conversation_history:
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.session_state.query_count = 0
        st.rerun()

if (user_query and send_button) or (user_query and not send_button and st.session_state.query_count == 0):
    # Create a new conversation entry
    conversation_entry = {
        'user_query': user_query,
        'sql': '',
        'results': None,
        'chart': None,
        'error': None
    }
    
    # Generate SQL
    with st.spinner("🤔 Thinking and generating SQL..."):
        sql = generate_sql(user_query)
        conversation_entry['sql'] = sql
    
    if not sql:
        conversation_entry['error'] = "No SQL generated or extraction failed."
    else:
        # Run query
        with st.spinner("🔍 Executing query..."):
            results = run_query(sql)
            conversation_entry['results'] = results
        
        if results is None or results.empty:
            conversation_entry['error'] = "No results returned or query could not be executed."
        else:
            # Generate visualizations
            with st.spinner("📊 Creating visualizations..."):
                fig = create_smart_visualizations(results, user_query)
                if fig:
                    conversation_entry['chart'] = fig
    
    
    st.session_state.conversation_history.append(conversation_entry)
    st.session_state.query_count += 1
    
    st.rerun()