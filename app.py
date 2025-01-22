from flask import Flask, render_template, request
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Database setup
conn = sqlite3.connect('customer_calls.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS calls (
        call_time TIMESTAMP,
        last_name TEXT,
        first_name TEXT,
        referral_type TEXT,
        call_attempts INTEGER,
        product_type TEXT,
        apt_date DATE,
        apt_time TIME,
        address TEXT,
        sales INTEGER
    )
''')
conn.commit()
conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get data from the form
        call_time = datetime.now()
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        referral_type = request.form['referral_type']
        call_attempts = int(request.form['call_attempts'])
        product_type = request.form['product_type']
        apt_date = request.form['apt_date']
        apt_time = request.form['apt_time']
        address = request.form['address']
        sales = int(request.form['sales'])

        # Save data to the database
        conn = sqlite3.connect('customer_calls.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (call_time, last_name, first_name, referral_type, call_attempts, product_type, apt_date, apt_time, address, sales))
        conn.commit()
        conn.close()

    # Analysis and metrics
    conn = sqlite3.connect('customer_calls.db')
    df = pd.read_sql_query("SELECT * FROM calls", conn)
    conn.close()

    total_calls = len(df)
    calls_per_day = df.groupby(df['call_time'].dt.date).size().to_dict()
    conversion_rate = (df['sales'].sum() / total_calls) * 100 if total_calls else 0

    # Create charts
    img = io.BytesIO()

    # Example: Calls per day bar chart
    plt.figure(figsize=(8, 6))
    plt.bar(calls_per_day.keys(), calls_per_day.values())
    plt.xlabel('Date')
    plt.ylabel('Number of Calls')
    plt.title('Calls per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    calls_per_day_chart = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('index.html', total_calls=total_calls, conversion_rate=conversion_rate, calls_per_day_chart=calls_per_day_chart)

if __name__ == '__main__':
    app.run(debug=True)
