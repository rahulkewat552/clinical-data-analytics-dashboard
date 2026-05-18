## 🏥 Clinical Data Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Dash](https://img.shields.io/badge/Dash-2.14.0-green)
![SQLite](https://img.shields.io/badge/SQLite-3-blue)
![Plotly](https://img.shields.io/badge/Plotly-5.18.0-orange)

## Overview

Healthcare analytics dashboard using **SQLite database** with Dash frontend. Visualizes patient demographics, medical conditions, billing analytics, and admission trends.

## Features

- Patient records & average billing metrics
- Age distribution by gender
- Medical condition breakdown (pie chart)
- Insurance provider comparison
- Billing amount histogram with slider
- Admission trends (line/bar toggle)
- CSV file upload support

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Dash, Bootstrap, CSS |
| Database | SQLite |
| Queries | SQL with parameterized statements |
| Visualizations | Plotly |
| Data Processing | Pandas |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create database
python scripts/csv_to_sqlite.py

# Run app
python app.py
```

The app will start on http://127.0.0.1:8050

## Project Structure
```text
├── app.py                 # Main application
├── scripts/
│   └── csv_to_sqlite.py   # Database setup
├── data/
│   ├── healthcare.csv     # Source data
│   └── healthcare.db      # SQLite database
├── assets/
│   └── style.css
└── screenshots/
```

## Dataset

The sample dataset (`healthcare.csv`) includes:

- Patient demographics (Age, Gender)
- Medical details (Condition, Date of Admission)
- Billing information (Billing Amount, Insurance Provider)

You can replace or upload your own CSV file with similar columns.

## Screenshots
Dashboard Overview
![Dashboard](screenshots/dashboard-home.png)

Demographics
![Demographics](screenshots/demographics.png)

Billing Distribution
![Billing distribution](screenshots/billing-distribution.png)

Admission Trends
![Admission trends](screenshots/admission-trends-bar.png)

## License
MIT