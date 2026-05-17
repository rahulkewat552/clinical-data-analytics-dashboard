"""
CSV to SQLite Migration Script
Converts healthcare.csv to SQLite database with proper schema and indexes
Run this script once to create the database
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_database():
    """Convert CSV to SQLite database with optimized schema"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Read CSV file
    print(" Reading CSV file...")
    df = pd.read_csv('data/healthcare.csv')
    
    # Convert data types to match SQLite-friendly formats
    print(" Converting data types...")
    df["Billing Amount"] = pd.to_numeric(df['Billing Amount'], errors='coerce')
    df["Date of Admission"] = pd.to_datetime(df['Date of Admission'], errors='coerce')
    df["Age"] = pd.to_numeric(df['Age'], errors='coerce')
    
    # Create SQLite connection
    conn = sqlite3.connect('data/healthcare.db')
    cursor = conn.cursor()
    
    # Drop table if exists (for clean re-runs)
    cursor.execute("DROP TABLE IF EXISTS healthcare")
    
    # Create table with explicit schema for better performance
    print(" Creating table schema...")
    cursor.execute("""
        CREATE TABLE healthcare (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Age INTEGER,
            Gender TEXT,
            "Blood Type" TEXT,
            "Medical Condition" TEXT,
            "Date of Admission" DATE,
            Doctor TEXT,
            Hospital TEXT,
            "Insurance Provider" TEXT,
            "Billing Amount" REAL,
            "Room Number" INTEGER,
            "Admission Type" TEXT,
            "Discharge Date" DATE,
            Medication TEXT,
            "Test Results" TEXT,
            YearMonth TEXT
        )
    """)
    
    # Add YearMonth column (same as your pandas version)
    df["YearMonth"] = df["Date of Admission"].dt.strftime("%Y-%m")
    
    # Insert data into SQLite
    print(f" Inserting {len(df)} records into database...")
    df.to_sql('healthcare', conn, if_exists='replace', index=False)
    
    # Create indexes for frequently queried columns (improves performance)
    print(" Creating indexes for faster queries...")
    cursor.execute("CREATE INDEX idx_gender ON healthcare(Gender)")
    cursor.execute("CREATE INDEX idx_medical_condition ON healthcare('Medical Condition')")
    cursor.execute("CREATE INDEX idx_insurance ON healthcare('Insurance Provider')")
    cursor.execute("CREATE INDEX idx_billing ON healthcare('Billing Amount')")
    cursor.execute("CREATE INDEX idx_date ON healthcare('Date of Admission')")
    cursor.execute("CREATE INDEX idx_yearmonth ON healthcare(YearMonth)")
    
    # Verify data was inserted correctly
    cursor.execute("SELECT COUNT(*) FROM healthcare")
    count = cursor.fetchone()[0]
    print(f" Database created successfully! {count} records inserted.")
    
    # Show sample of data
    print("\n Sample data from database:")
    sample_df = pd.read_sql_query("SELECT * FROM healthcare LIMIT 5", conn)
    print(sample_df)
    
    # Close connection
    conn.commit()
    conn.close()
    
    print("\n Database ready at: data/healthcare.db")

if __name__ == "__main__":
    create_database()