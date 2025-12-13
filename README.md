# 📊 X-Company Sales Analytics Dashboard  
**Diagnostic & Decision Intelligence**

This project presents an end-to-end sales analytics solution built to move from **analysis to action**.  
It is structured into two complementary dashboards:

- **A2 – Diagnostic Dashboard** → explains *what is happening and why*
- **A3 – Decision Dashboard** → focuses on *what should be done next*

Both dashboards are built using **Streamlit, Pandas, and Plotly**, and are designed to handle real-world, imperfect datasets safely.

---

## 🔹 Project Overview

Organizations often have access to sales data but struggle to translate it into clear, actionable decisions.  
This project addresses that gap by separating analytics into two layers:

- **Diagnostic layer** for exploration, trends, and root-cause analysis  
- **Decision layer** for executive-ready insights, risk identification, and recommended actions  

The result is a workflow similar to what is used in real **business intelligence and analytics teams**.

---

## 🔍 A2 – Diagnostic Dashboard

### Purpose
To explore sales performance, profitability, discount behavior, and regional trends in order to understand **what is happening and why**.

### Key Features
- Sales and profit trends over time  
- Category and sub-category performance  
- Regional and state-level analysis  
- Discount vs profit risk analysis  
- Interactive filtering and visual exploration  

### Dashboard Preview
![A2 Diagnostic Dashboard](A2_Diagnostic_Dashboard/screenshots.png)

### Files
- `A2_Diagnostic_Dashboard/app.py`  
- `A2_Diagnostic_Dashboard/case-study.md`  
- `A2_Diagnostic_Dashboard/requirements.txt`  

---

## 🎯 A3 – Decision Dashboard

### Purpose
To convert analytical findings into **clear, actionable business decisions** suitable for leadership and stakeholders.

### Key Features
- Executive KPI snapshot (Sales, Profit, Loss Orders)  
- Profit risk by category and region  
- Discount threshold impact analysis  
- Identification of loss-making sub-categories  
- Decision summary and recommended actions  
- Robust schema validation with column mapping for uploaded datasets  

### Dashboard Preview
![A3 Decision Dashboard](A3_Decision_Dashboard/screenshots.png)

### Files
- `A3_Decision_Dashboard/app.py`  
- `A3_Decision_Dashboard/case-study.md`  
- `A3_Decision_Dashboard/requirements.txt`  

---

## 🧠 Advanced Data Handling

To reflect real-world conditions, the project includes:

- Schema validation to ensure analytical correctness  
- Interactive column mapping for uploaded datasets  
- Safe numeric cleaning and coercion  
- Graceful handling of missing or imperfect data without crashes  

These features make the dashboards **robust and production-oriented**, not demo-only.

---

## 🛠️ Tech Stack

- **Python**  
- **Streamlit** – interactive dashboards  
- **Pandas** – data processing  
- **Plotly** – interactive visualizations  

---

## 📁 Repository Structure

X_Company-AI-Sales-Dashboard/
│
├── README.md
├── sales_data.csv
│
├── A2_Diagnostic_Dashboard/
│ ├── app.py
│ ├── requirements.txt
│ ├── case-study.md
│ └── screenshots.png
│
├── A3_Decision_Dashboard/
│ ├── app.py
│ ├── requirements.txt
│ ├── case-study.md
│ └── screenshots.png
```

---

## ✅ Key Takeaway

This project demonstrates the ability to:

- Perform structured exploratory analysis  
- Translate insights into business decisions  
- Build robust, user-safe analytics tools  
- Communicate findings clearly to non-technical stakeholders  

It reflects an **end-to-end analytics mindset**, not just visualization.
