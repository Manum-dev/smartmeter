# Smart Meter Analyst - AI Energy Assistant ⚡

An interactive, responsive full-stack web application designed to analyze smart meter energy data (consumption, solar production, grid feeds) and provide tailored energy efficiency recommendations using a local Large Language Model (LLM).

Developed as a prototype showcase for a company, combining classical Data Science with modern Generative AI.

---

## 🌟 Key Features

- **Energy Performance Dashboard**: Instantly displays key aggregated metrics (Total Consumption, Solar Production, Self-Consumption Rate, and Night Consumption Rate) processed via Pandas.
- **Local AI Energy Consultant**: Interactive chat powered by **Meta's Llama 3.2** running locally via **Ollama**, acting as an expert energy consultant.
- **Interactive Visualization**: Line chart displaying daily consumption vs. solar production using **Chart.js**.
- **One-Click PDF Report**: Generates and downloads a branded PDF report containing current metrics and the rendered chart using **jsPDF**.
- **Responsive Dark Design**: Premium dark-mode UI optimized for both desktop and mobile screens.

---

## 🔒 Security & Architecture Best Practices

This project was built with security in mind, addressing key vulnerabilities (OWASP Top 10):
- **Path Traversal Protection**: The backend enforces a strict, hardcoded file path (`dati_consumi.csv`) for the dataset. Users cannot supply arbitrary file paths, preventing local file inclusion (LFI) attacks.
- **Strict Content Security Policy (CSP)**: Headers are dynamically configured to restrict script and style sources. Inline scripts and styles are completely blocked.
- **No Inline JavaScript (XSS Prevention)**: All frontend logic is separated into `static/app.js` using event listeners instead of inline attributes (e.g., `onclick`), eliminating Cross-Site Scripting vulnerabilities.
- **Data Isolation**: The application utilizes a Python Virtual Environment (`venv`) to keep dependencies isolated and avoid dependency clutter.

---

## 📂 Project Structure

```text
smart_meter_analyst/
│
├── static/                   # Frontend assets
│   ├── index.html            # Markup structure
│   ├── style.css             # Responsive styling (Mobile-First)
│   └── app.js                # Core JS logic & Chart initialization
│
├── .gitignore                # Excludes venv, pycache, and CSV files from Git
├── README.md                 # Project documentation
├── analyzer.py               # Pandas logic for data aggregation
├── main.py                   # FastAPI backend & Ollama integration
├── generate_dataset.py       # Helper script to generate realistic energy data
└── dati_consumi.csv          # Generated smart meter CSV dataset