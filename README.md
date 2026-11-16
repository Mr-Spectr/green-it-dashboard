# Green IT Data Center Efficiency Dashboard

An interactive Streamlit dashboard for measuring data-center energy efficiency. Enter your energy readings, calculate Power Usage Effectiveness (PUE) and Data Center infrastructure Efficiency (DCiE), investigate facility overhead, compare scenarios, and estimate the financial and carbon impact of efficiency improvements.

## Why it matters

Data centers use energy for more than servers. Cooling, UPS losses, lighting, and power distribution can consume a large share of total electricity. This application separates IT energy from non-IT overhead so users can identify efficiency opportunities in a clear, presentation-ready format.

## Features

- Interactive inputs for facility energy, IT energy, electricity rate, carbon factor, and measurement period
- Automatic PUE, DCiE, non-IT overhead, and IT-energy-share calculations
- Validation to prevent IT equipment energy from exceeding total facility energy
- Energy-breakdown doughnut chart and PUE performance gauge
- Editable legacy, baseline, and optimized scenario comparison
- Seven-day energy trend and hourly energy-load heatmap
- Cooling efficiency diagnostic chart
- Target-PUE improvement planner with energy, cost, and CO2e reduction estimates
- One-click CSV export for the current analysis

## Metrics

```text
PUE  = Total Facility Energy / IT Equipment Energy
DCiE = (IT Equipment Energy / Total Facility Energy) x 100
```

Lower PUE and higher DCiE indicate better energy efficiency.

### Sample calculation

| Input | Value |
| --- | ---: |
| Total facility energy | 1,000 kWh |
| IT equipment energy | 600 kWh |
| Non-IT overhead | 400 kWh |
| PUE | 1.67 |
| DCiE | 60% |

## Run locally

### Prerequisites

- Python 3.10 or newer

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/green-it-dashboard.git
cd green-it-dashboard
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Install dependencies and launch the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

## Demo flow

Use these values for a quick presentation:

| Field | Value |
| --- | ---: |
| Total facility energy | 1,000 kWh |
| IT equipment energy | 600 kWh |
| Electricity rate | 8 per kWh |
| Grid carbon factor | 0.70 kg CO2e per kWh |

1. Click **Calculate efficiency** to obtain PUE 1.67 and DCiE 60%.
2. Use the doughnut chart to explain the 400 kWh non-IT overhead.
3. Edit the scenario table to compare legacy and optimized conditions.
4. Move the Target PUE slider to 1.25 to show projected savings.
5. Download the CSV report for a stakeholder-ready summary.

## Deployment

The repository includes a `Dockerfile` and `render.yaml` for a straightforward public deployment on Render.

1. Create a new public GitHub repository and push this project.
2. In Render, choose **New +**, then **Blueprint**.
3. Select the GitHub repository and approve the generated service.
4. After the build completes, Render provides the public URL. Add that URL below.

**Live demo:** Add deployment URL after publishing.

## Data note

The core efficiency, overhead, and savings metrics use the energy values entered by the user. The monitoring trend, heatmap, and cooling diagnostic views use repeatable sample data scaled from the entered measurement. In a production installation, these views can connect to power meters, environmental sensors, UPS systems, or a building-management API.

## Project structure

```text
.
|-- app.py              # Streamlit application and calculations
|-- requirements.txt    # Python dependencies
|-- Dockerfile          # Container deployment configuration
|-- render.yaml         # Render Blueprint configuration
`-- README.md           # Project documentation
```

## Future enhancements

- Real-time IoT sensor integration
- Historical database storage and trend analysis
- Alerts for high PUE thresholds
- Location-specific carbon factors
- Predictive cooling optimization

## License

This project is available for academic and demonstration use.
