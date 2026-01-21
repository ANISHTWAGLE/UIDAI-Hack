Dataset:- https://drive.google.com/file/d/1aoPOthnz2MjjGWDWdrwyVkT8TVtPg0si/view?usp=sharing

Dashboard Visualizations:- https://drive.google.com/drive/folders/1NReTLnt5K_LQKdzjXXnsoz3dHwyQRzvc?usp=drive_link
# Aadhaar Infrastructure Decision Dashboard

A comprehensive data-driven decision support system for analyzing Aadhaar enrollment and update infrastructure stress across India. This project transforms raw Aadhaar transaction data into actionable insights for government infrastructure planning and resource allocation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Installation](#installation)
- [Usage](#usage)
- [Dashboard Components](#dashboard-components)
- [Data Quality](#data-quality)
- [Methodology](#methodology)
- [Contributing](#contributing)

## 🎯 Overview

The Aadhaar Infrastructure Decision Dashboard is a government-focused analytical platform that:

- **Processes** millions of Aadhaar transaction records across India
- **Analyzes** enrollment and update patterns to identify infrastructure stress
- **Recommends** specific interventions (mobile vans, permanent centers, additional counters)
- **Quantifies** resource requirements (operators, budget, equipment)
- **Visualizes** insights through interactive maps, charts, and executive reports

Built with **no proprietary APIs** (uses OpenStreetMap), making it suitable for government deployment with minimal external dependencies.

## ✨ Features

### 📊 Analytics Engine
- **Stress Classification**: Categorizes districts into Critical/Warning/Normal based on EUR (Enrolment-Update Ratio)
- **Time-Window Analysis**: Evaluates patterns across short-term, mid-term, and long-term periods
- **Capacity Gap Estimation**: Calculates operator requirements and budget needs

### 🗺️ Interactive Dashboard
- **Stress Heatmap**: Geographic visualization of infrastructure stress using OpenStreetMap
- **Trend Analysis**: Time-series charts showing stress evolution
- **Decision Matrix**: Scatter plots correlating stress intensity with volatility
- **Recommendation Engine**: Rule-based system with full auditability
- **Action Tables**: Executive-ready CSV exports for administrative use
- **Rankings**: Top stressed and best-served districts for budget allocation
- **Capacity Planning**: Detailed staffing and budget projections

### 🎨 Design Principles
- **Government-appropriate**: Professional styling, minimal external dependencies
- **Decision-driven**: Focuses on actionable outputs, not just analytics
- **Auditable**: Rule-based recommendations (no black-box ML)
- **Exportable**: All insights available as downloadable CSV files

## 📁 Project Structure

```
UIDAI-Hack/
├── dashboard/
│   ├── app.py                          # Main Streamlit application
│   ├── data_loader.py                  # Data loading and preprocessing
│   └── components/
│       ├── __init__.py
│       ├── heatmap.py                  # Geographic stress visualization
│       ├── time_series.py              # Trend analysis charts
│       ├── scatter.py                  # Decision matrix visualization
│       ├── recommendation_engine.py    # Rule-based intervention logic
│       ├── action_table.py             # Executive action plan tables
│       ├── rankings.py                 # Priority rankings
│       └── capacity_gap.py             # Resource requirement estimation
│
├── data_preprocessing.py               # Initial data merging script
├── clean_master_data.py                # State/district standardization
├── aggregate_duplicates_v2.py          # Duplicate consolidation
├── 03_eur_stability_and_intervention_classification.ipynb  # Analysis notebook
├── data_quality_check.ipynb            # Quality validation notebook
│
├── district_recommendations.csv        # Primary analysis output
├── operator_requirements.csv           # Capacity requirements
├── aadhaar_daily_activity.csv         # Daily transaction aggregates
├── final_aadhaar_intervention_classification.csv  # Complete classification
│
├── requirements.txt                    # Python dependencies
└── README.md                          # This file
```

## 🔄 Data Pipeline

### 1. **Data Collection** (Raw Data)
- **Source Files**: Separate CSVs for Enrolments, Biometric Updates, Demographic Updates
- **Coverage**: 36 states/UTs, 1000+ districts, 19,000+ pincodes
- **Time Range**: March 2025 - December 2025 (115 days)

### 2. **Preprocessing** (`data_preprocessing.py`)
```python
# Merges three data streams
python data_preprocessing.py
```
**Output**: `master_aadhaar_data.csv`

**Processes**:
- Loads enrolment, biometric, and demographic data
- Performs outer joins on [date, state, district, pincode]
- Calculates derived metrics:
  - `total_enrolments` = age_0_5 + age_5_17 + age_18_greater
  - `total_updates` = biometric + demographic updates
  - `update_to_enrolment_ratio`
  - `overall_activity` = enrolments + updates
- Adds temporal features (month_name, day_name, is_weekend)

### 3. **Data Cleaning** (`clean_master_data.py`)
```python
python clean_master_data.py
```
**Output**: `master_aadhaar_data_final_cleaned.csv`

**Standardizations**:
- **State Names**: 
  - Case normalization ("andhra Pradesh" → "Andhra Pradesh")
  - Spelling fixes ("Chhatisgarh" → "Chhattisgarh")
  - UT consolidations ("Daman & Diu" → "Dadra and Nagar Haveli and Daman and Diu")
- **District Names**: Title case standardization
- **Data Types**: Ensures integers for counts, handles missing values
- **Invalid Records**: Removes '100000' placeholder entries

### 4. **Duplicate Aggregation** (`aggregate_duplicates_v2.py`)
```python
python aggregate_duplicates_v2.py
```
**Output**: `master_aadhaar_data_fully_cleaned.csv`

**Process**:
- Groups by [date, state, district, pincode]
- Sums all transaction counts
- Recalculates derived ratios
- Ensures unique keys

### 5. **EUR Analysis & Classification** (Jupyter Notebook)
```python
# Run in Jupyter/Google Colab
03_eur_stability_and_intervention_classification.ipynb
```
**Outputs**: 
- `district_recommendations.csv`
- `operator_requirements.csv`
- `final_aadhaar_intervention_classification.csv`

**Analysis**:
1. **EUR Calculation**: 
   ```
   EUR = total_updates / (total_enrolments + 0.1)
   ```
2. **Statistical Features**:
   - `eur_mean`: Average stress intensity
   - `eur_std`: Volatility measure
   - `stress_percentile`: Relative ranking (0-100)

3. **Window Classification**:
   - Short-term: < 30 days of data
   - Mid-term: 30-90 days
   - Long-term: > 90 days

4. **Intervention Logic**:
   ```
   IF stress_percentile > 85% AND window = short_term:
       recommendation = "Mobile Aadhaar Van"
   ELIF stress_percentile > 85% AND window IN [mid_term, long_term]:
       recommendation = "Permanent Centre"
   ELIF stress_percentile > 50%:
       recommendation = "Extra Counters"
   ELSE:
       recommendation = "Monitor / No Action"
   ```

5. **Capacity Estimation**:
   ```
   operators_needed = daily_gap / operator_capacity
   daily_gap = max(0, avg_daily_activity - current_capacity)
   ```

### 6. **Quality Validation** (`data_quality_check.ipynb`)

Comprehensive checks for:
- ✅ Null values (0 found)
- ✅ Duplicates (0 after aggregation)
- ✅ State name consistency (36 unique states)
- ✅ District-state mappings
- ✅ Pincode validity (6-digit format)
- ✅ Data type correctness
- ✅ Temporal coverage

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ANISHTWAGLE/UIDAI-Hack.git
   cd UIDAI-Hack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset**
   - Download from [Google Drive](https://drive.google.com/file/d/1aoPOthnz2MjjGWDWdrwyVkT8TVtPg0si/view?usp=sharing)
   - Extract to project root directory

## 📖 Usage

### Running the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Running the Data Pipeline

**Complete Pipeline**:
```bash
# Step 1: Merge raw data
python data_preprocessing.py

# Step 2: Clean and standardize
python clean_master_data.py

# Step 3: Aggregate duplicates
python aggregate_duplicates_v2.py

# Step 4: Run EUR analysis (in Jupyter)
jupyter notebook 03_eur_stability_and_intervention_classification.ipynb

# Step 5: Launch dashboard
streamlit run dashboard/app.py
```

## 🎛️ Dashboard Components

### 1. 🗺️ Stress Map
- **OpenStreetMap Integration**: No API keys required
- **Heat Layer**: Red clusters indicate critical stress
- **District Markers**: Click for detailed recommendations
- **Legend**: Color-coded by intervention type

### 2. 📈 Trends
- **Window Class Analysis**: Short/mid/long-term patterns
- **Enrolments vs Updates**: State-level comparisons
- **Stress Distribution**: Histogram with thresholds at 50% and 85%

### 3. 🎯 Decisions
- **Decision Matrix**: EUR Mean (intensity) vs EUR Std (volatility)
- **Quadrant Logic**: 
  - High stress + High volatility → Mobile Van
  - High stress + Low volatility → Permanent Centre
  - Medium stress → Extra Counters
  - Low stress → Monitor

### 4. 🧠 Engine
- **Rule Display**: Complete decision logic for auditability
- **Distribution Pie Chart**: Recommendations by type
- **District Lookup**: Search specific locations
- **Audit Summary**: Aggregated statistics

### 5. 📋 Actions
- **Executive Table**: Sorted by stress severity
- **Filtering**: By state, action type, operator requirements
- **CSV Export**: Ready for administrative use
- **State Summary**: Aggregated view

### 6. 🏆 Rankings
- **Top 10 Most Stressed**: Priority for intervention
- **Top 10 Best Served**: Potential for reallocation
- **State Overview**: Average stress by state
- **Detailed Tables**: Full district information

### 7. 🧮 Capacity
- **Configurable Assumptions**:
  - Operator capacity (default: 50 transactions/day)
  - Salary (default: ₹15,000/month)
  - Hardware cost (default: ₹3,00,000/station)
  - Monthly rent (default: ₹20,000/station)

- **Outputs**:
  - Total operators needed
  - Monthly recurring costs
  - One-time hardware budget
  - First-year total budget
  - State-wise breakdowns

### Sidebar Filters
- **State Selection**: All states or specific state
- **District Selection**: Depends on state filter
- **Stress Category**: Critical/Warning/Normal
- **Quick Stats**: Real-time counts

## ✅ Data Quality

### Final Dataset Statistics
- **Total Records**: 2,307,730
- **Null Values**: 0
- **Duplicates**: 0
- **States**: 36 (matches official count)
- **Districts**: 1,001
- **Pincodes**: 19,814
- **Date Range**: March 1, 2025 - December 31, 2025

### Known Data Characteristics
- **Multi-state Districts**: 23 districts appear in multiple states (e.g., Hyderabad in Andhra Pradesh and Telangana)
- **Multi-state Pincodes**: 705 pincodes span state borders (border regions)
- **Missing Months**: August 2025 has no data
- **Partial Months**: March-July 2025 have limited daily coverage

## 🧪 Methodology

### Stress Metrics

**EUR (Enrolment-Update Ratio)**:
```
EUR = Total Updates / (Total Enrolments + 0.1)
```
- Higher EUR → More update load relative to enrolments
- Indicates infrastructure strain

**Stress Percentile**:
- Ranks districts from 0-100%
- Uses empirical distribution
- Accounts for both mean and standard deviation

### Intervention Thresholds

| Stress Level | Percentile | Recommendation | Rationale |
|--------------|------------|----------------|-----------|
| Critical | >85% | Mobile Van / Permanent Centre | Immediate action required |
| Warning | 50-85% | Extra Counters / Temporary Support | Preventive measures |
| Normal | <50% | Monitor / No Action | Within acceptable range |

### Capacity Calculation

```python
daily_gap = max(0, avg_daily_activity - current_capacity)
operators_needed = ceiling(daily_gap / operator_capacity)
```

**Assumptions**:
- Operator capacity: 50 transactions/day (configurable)
- Working days: 25 days/month (configurable)

## 👥 Contributors

- [Anish Wagle](https://github.com/ANISHTWAGLE) - Project Lead
- [geeky33](https://github.com/geeky33)
- [Shreyas Gurav](https://github.com/shreyasgurav)

## 📄 License

This project is intended for government use and academic purposes. Please contact the maintainers for usage permissions.

## 🙏 Acknowledgments

- UIDAI for Aadhaar infrastructure data
- OpenStreetMap for mapping capabilities
- Streamlit for the dashboard framework
- Plotly for interactive visualizations

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact the maintainers directly

---

**Built for government deployment with minimal external dependencies** | **Decision-Driven Government Dashboard** | **Powered by OpenStreetMap**
