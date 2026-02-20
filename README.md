# Kotak Neo Real-Time Options Trading Dashboard

A professional-grade real-time options trading dashboard built with Python and Streamlit, streaming live data from the Kotak Neo API.

## 🚀 Features
- **Live Data Streaming**: Real-time LTP, OI, and Volume updates via WebSocket.
- **Advanced Analytics**:
  - Live Put-Call Ratio (PCR).
  - Max Pain calculation.
  - Support & Resistance detection based on OI.
  - OI Heatmaps and trend analysis.
- **Option Chain**: Professional layout with ATM highlighting.
- **Demo Mode**: Full functionality with simulated data for testing without API credentials.
- **Modular Architecture**: Clean, scalable code structure.

## 📂 Project Structure
- `app.py`: Main Streamlit dashboard.
- `kotak_api.py`: Kotak Neo API wrapper & Mock client.
- `option_chain.py`: Option chain data management.
- `analytics.py`: Financial calculations (PCR, Max Pain, Greeks).
- `ui_components.py`: Reusable Streamlit UI elements.
- `config.py`: Configuration and environment settings.

## 🛠 Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Kotak Neo API Credentials (API Key, Secret, UCC, etc.)

### 2. Installation
1. Clone the repository or download the files.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Kotak Neo SDK (if not on PyPI):
   ```bash
   pip install "git+https://github.com/Kotak-Neo/Kotak-neo-api-v2.git@v2.0.1#egg=neo_api_client"
   ```

### 3. Configuration
Create a `.env` file or update `config.py` with your credentials:
```env
KOTAK_API_KEY=your_api_key
KOTAK_API_SECRET=your_api_secret
KOTAK_MOBILE_NUMBER=your_mobile
KOTAK_PASSWORD=your_password
KOTAK_UCC=your_ucc
DEMO_MODE=True
```

### 4. Running the Dashboard
```bash
streamlit run app.py
```

## 🔐 Authentication
The dashboard supports login via the sidebar. If you don't have Kotak credentials, toggle **Demo Mode** to see the dashboard in action with simulated live data.

## 📊 Performance
- WebSocket streaming for low latency.
- Optimized UI updates every 1 second.
- Efficient memory handling for long-running sessions.

## 🛡 Disclaimer
This dashboard is for educational and informational purposes only. Trading in options involves significant risk.
