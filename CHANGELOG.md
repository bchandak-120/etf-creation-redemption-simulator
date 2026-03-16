# Changelog

All notable changes to ETF Creation Redemption Simulator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-16

### Added
- Initial release of ETF Creation Redemption Simulator
- Interactive Streamlit web interface
- Real-time market data fetching via yfinance
- NAV calculation from constituent baskets
- Premium/discount analysis
- Comprehensive transaction cost modeling
- Arbitrage signal generation (creation/redemption)
- Performance metrics and analytics
- Export functionality for results
- Educational content about ETF mechanics
- Support for custom constituent baskets
- Default baskets for major ETFs (SPY, QQQ, IWM)
- Interactive charts with Plotly
- Summary metrics dashboard
- Trading events table
- Cost assumption customization
- Data validation and error handling
- Comprehensive documentation
- Unit tests for core functionality

### Features
- **Data Loading**: Fetch historical prices for any ETF and constituents
- **NAV Engine**: Calculate intrinsic NAV and premium/discount metrics
- **Cost Model**: Model comprehensive transaction costs (trading, fees, slippage)
- **Arbitrage Engine**: Generate optimal creation/redemption signals
- **Simulator**: End-to-end analysis workflow orchestration
- **Web Interface**: Beautiful, interactive Streamlit dashboard
- **Analytics**: Detailed performance metrics and visualizations

### Technical
- Python 3.8+ compatibility
- Modular, object-oriented architecture
- Type hints and comprehensive docstrings
- Error handling and data validation
- Unit test coverage
- Production-ready code quality

### Documentation
- Comprehensive README with installation and usage guide
- API documentation for all modules
- Educational content about ETF arbitrage
- Interview talking points and resume bullets
- Contribution guidelines
- MIT License

## [Unreleased]

### Planned
- Machine learning for signal optimization
- Real-time data streaming
- Portfolio-level arbitrage analysis
- Advanced visualization features
- Mobile responsiveness
- API endpoints for external access
