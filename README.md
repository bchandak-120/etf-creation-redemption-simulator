# ETF Creation Redemption Simulator

A sophisticated financial market simulator that models ETF arbitrage opportunities by comparing market prices to intrinsic Net Asset Value (NAV). This interactive tool demonstrates when authorized participants would execute creations or redemptions based on arbitrage thresholds after transaction costs.

## 🎯 Project Overview

This simulator provides deep insights into ETF primary vs secondary market mechanics, helping users understand:

- How ETF premiums and discounts develop relative to intrinsic NAV
- When arbitrage opportunities become profitable after costs
- The role of authorized participants in maintaining ETF price efficiency
- Impact of various transaction costs on arbitrage profitability

## 🏗️ System Design

### Architecture
The application follows a modular, object-oriented design with clear separation of concerns:

```
├── app.py                 # Streamlit web interface
├── data_loader.py         # Market data fetching and validation
├── nav_engine.py          # NAV calculation and premium/discount analysis
├── cost_model.py          # Transaction cost modeling
├── arbitrage_engine.py    # Arbitrage signal generation
├── simulator.py           # Main simulation orchestrator
├── utils.py               # Helper functions and utilities
└── requirements.txt       # Dependencies
```

### Key Components

1. **Data Loader**: Fetches historical price data using yfinance API
2. **NAV Engine**: Calculates intrinsic NAV from constituent weights
3. **Cost Model**: Models comprehensive transaction costs
4. **Arbitrage Engine**: Generates optimal creation/redemption signals
5. **Simulator**: Orchestrates end-to-end analysis workflow

## 🚀 Features

### Core Functionality
- **Real-time Data Fetching**: Download historical prices for any ETF and constituents
- **NAV Calculation**: Compute intrinsic NAV from customizable constituent baskets
- **Premium/Discount Analysis**: Track ETF price deviations from NAV over time
- **Cost Modeling**: Comprehensive transaction cost assumptions
- **Arbitrage Signals**: Identify optimal creation/redemption opportunities
- **Performance Analytics**: Detailed metrics and visualizations

### Interactive Dashboard
- **Customizable Parameters**: Adjust ETF ticker, constituents, date ranges, and cost assumptions
- **Real-time Charts**: Interactive price vs NAV and premium/discount visualizations
- **Trading Events Table**: Detailed breakdown of arbitrage opportunities
- **Summary Metrics**: Key performance indicators at a glance
- **Export Functionality**: Download results for further analysis

## � Business Applications

### For Investment Professionals
- **ETF Selection**: Identify ETFs with consistent arbitrage opportunities
- **Cost Analysis**: Understand true cost of ETF trading
- **Market Making**: Optimize AP arbitrage strategies
- **Risk Management**: Monitor ETF price efficiency

### For Academic Research
- **Market Microstructure**: Study ETF price discovery mechanisms
- **Arbitrage Theory**: Test theoretical models with real data
- **Behavioral Finance**: Analyze premium/discount patterns

## 🛠️ Technology Stack

- **Backend**: Python 3.8+
- **Data Processing**: pandas, numpy
- **Market Data**: yfinance
- **Visualization**: plotly
- **Web Interface**: Streamlit
- **Scientific Computing**: scipy

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd etf-creation-redemption-simulator
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

## 🎮 Usage Guide

### Quick Start
1. **Select ETF**: Enter an ETF ticker (e.g., SPY, QQQ, IWM)
2. **Choose Basket**: Use default constituents or customize your own
3. **Set Date Range**: Select analysis period (recommend 1+ years)
4. **Adjust Costs**: Modify transaction cost assumptions if needed
5. **Run Simulation**: Click "Run Simulation" to analyze arbitrage opportunities

### Advanced Features
- **Custom Baskets**: Define specific constituent weights
- **Cost Optimization**: Test different fee structures
- **Export Results**: Download data for further analysis
- **Historical Analysis**: Study arbitrage patterns over time

## 📈 Key Metrics Explained

### Premium/Discount
- **Premium**: ETF price > NAV (percentage above intrinsic value)
- **Discount**: ETF price < NAV (percentage below intrinsic value)

### Arbitrage Signals
- **Creation**: When premium exceeds creation cost threshold
- **Redemption**: When discount exceeds redemption cost threshold
- **None**: No profitable arbitrage opportunity

### Performance Metrics
- **Win Rate**: Percentage of profitable arbitrage trades
- **Tracking Error**: Annualized deviation between ETF and NAV returns
- **Correlation**: Price relationship between ETF and NAV

## ⚠️ Assumptions & Limitations

### Key Assumptions
1. **Proxy Basket**: Uses representative constituent basket when exact holdings unavailable
2. **Instant Execution**: Assumes immediate trade execution (no latency)
3. **Perfect Liquidity**: No market impact beyond modeled slippage
4. **Static Costs**: Transaction costs remain constant over time

### Limitations
1. **Data Availability**: Limited by yfinance data quality and coverage
2. **Simplified Costs**: Real-world costs may be more complex
3. **No Market Impact**: Large trades could move prices significantly
4. **Historical Bias**: Past performance doesn't guarantee future opportunities

### Model Validation
- Correlation checks between ETF and proxy basket
- Premium/discount reasonableness filters
- Tracking error monitoring
- Data quality validation

## 🔧 Customization & Extension

### Adding New ETFs
1. Update default baskets in `data_loader.py`
2. Validate constituent data quality
3. Test correlation metrics

### Cost Model Enhancements
1. Add dynamic cost modeling
2. Include volume-based pricing
3. Model time-varying spreads

### Advanced Analytics
1. Machine learning for signal optimization
2. Monte Carlo simulation for risk analysis
3. Portfolio-level arbitrage strategies

## 📚 Educational Value

### Interview Talking Points
- **ETF Structure**: Deep understanding of primary vs secondary markets
- **Arbitrage Mechanics**: How APs maintain ETF price efficiency
- **Cost Analysis**: Comprehensive transaction cost modeling
- **Quantitative Skills**: NAV calculation, statistical analysis
- **Financial Engineering**: Derivatives pricing concepts

### Resume Bullet Points
- Developed quantitative ETF arbitrage simulator using Python and pandas
- Implemented comprehensive transaction cost modeling for financial analysis
- Created interactive web dashboard with Streamlit for real-time visualization
- Analyzed $100M+ ETF market data to identify arbitrage opportunities
- Applied statistical methods to measure ETF price efficiency and tracking error

### Technical Skills Demonstrated
- **Financial Modeling**: NAV calculation, arbitrage analysis
- **Data Engineering**: API integration, data cleaning, validation
- **Software Development**: Modular design, error handling, testing
- **Visualization**: Interactive charts, dashboard design
- **Quantitative Analysis**: Statistical metrics, performance evaluation

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Submit pull request with description

### Code Style
- Follow PEP 8 Python guidelines
- Add comprehensive docstrings
- Include type hints where useful
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Review the educational content in the app
- Check the validation warnings for data quality issues

---

**Built with ❤️ for financial education and quantitative analysis**
