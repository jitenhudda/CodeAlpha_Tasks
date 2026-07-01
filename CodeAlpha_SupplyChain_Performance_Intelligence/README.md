# Supply Chain Performance Intelligence

## Overview

The goal of this project is to perform an end-to-end Exploratory Data Analysis (EDA) on the DataCo Smart Supply Chain dataset and transform raw operational data into actionable business insights.

The analysis explores sales performance, profitability, customer demand patterns, delivery performance, and operational efficiency. In addition, an interactive Business Intelligence dashboard was built using Streamlit and Plotly to help users explore the data dynamically.

---

## Business Problem

Supply chain organizations generate large amounts of operational data every day. However, without proper analysis, it becomes difficult to identify:

* High-performing markets
* Profitable product categories
* Seasonal demand patterns
* Delivery performance issues
* Profitability risks
* Operational bottlenecks

This project aims to convert raw supply chain data into meaningful insights that can support business decision-making.

---

## Project Objectives

The project was designed to achieve the following objectives:

✔ Explore the dataset structure and data quality

✔ Identify trends, patterns, and anomalies

✔ Test business assumptions using statistical analysis

✔ Detect operational issues affecting profitability

✔ Generate actionable business recommendations

✔ Build an interactive dashboard for decision-makers

---

## Dataset Information

Dataset: DataCo Smart Supply Chain Dataset

The dataset contains information related to:

* Orders
* Products
* Customers
* Markets
* Sales
* Profit
* Shipping
* Delivery Performance

The dataset is commonly used for supply chain analytics and business intelligence projects.

---

## Exploratory Data Analysis (EDA)

The analysis includes:

### Data Understanding

* Dataset shape and dimensions
* Column analysis
* Data type inspection
* Summary statistics

### Data Quality Assessment

* Missing value detection
* Duplicate record identification
* Data consistency checks

### Business Analysis

* Sales Performance Analysis
* Profitability Analysis
* Market Analysis
* Product Category Analysis
* Delivery Performance Analysis
* Seasonal Demand Analysis

### Statistical Analysis

* Correlation Analysis
* Hypothesis Testing
* Trend Validation
* Performance Comparisons

---

## Key Business Questions

The following questions were investigated during the analysis:

1. Which markets generate the highest revenue?
2. Which product categories generate the highest profit?
3. Do higher discounts reduce profitability?
4. How do shipping delays impact profit?
5. What seasonal trends exist in customer demand?
6. Which business segments contribute the most revenue?
7. What operational improvements can increase profitability?

---

## Dashboard Features

The project includes a professional interactive dashboard built with Streamlit.

### Dashboard Components

#### KPI Cards

* Total Sales
* Total Profit
* Total Orders
* Average Profit per Order

#### Interactive Filters

* Market Filter
* Year Filter

#### Interactive Charts

* Top Product Categories
* Monthly Performance Trends

#### Business Intelligence Panels

* Executive Summary
* Business Insights
* Strategic Recommendations

---

## Technologies Used

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Data Analysis             |
| Pandas     | Data Manipulation         |
| NumPy      | Numerical Analysis        |
| Matplotlib | Visualization             |
| Seaborn    | Statistical Visualization |
| Plotly     | Interactive Charts        |
| Streamlit  | Dashboard Development     |
| SciPy      | Statistical Testing       |

---

## Project Structure

```text
SupplyChain_Performance_Intelligence/

├── EDA_Task1.ipynb
├── app.py
├── dashboard_data.csv
├── DataCoSupplyChainDataset.csv
├── Requirements.txt
├── README.md
├── LICENSE
└── Dashboard_Screenshot.png
```

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard

```bash
streamlit run app.py
```

### 4. Open in Browser

```text
http://localhost:8501
```

---

## Key Insights

The analysis revealed several important findings:

* Certain markets contribute a significant share of total revenue.
* Product profitability varies considerably across categories.
* High discount levels negatively impact profit margins.
* Late deliveries are associated with lower profitability.
* Demand follows seasonal patterns that can support inventory planning.
* Operational efficiency improvements can increase overall business performance.

---

## Business Recommendations

Based on the analysis:

* Optimize discount strategies to protect margins.
* Improve delivery performance through logistics monitoring.
* Increase focus on high-profit product categories.
* Prepare inventory before seasonal demand peaks.
* Monitor underperforming markets and shipping methods.
* Use data-driven decision making for supply chain planning.

---

## Learning Outcomes

Through this project, the following skills were applied and strengthened:

* Exploratory Data Analysis (EDA)
* Statistical Analysis
* Data Visualization
* Business Intelligence
* Dashboard Development
* Supply Chain Analytics
* Data Storytelling

---

## Author

Jiten Hudda
