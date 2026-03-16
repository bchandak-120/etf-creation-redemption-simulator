# Contributing to ETF Creation Redemption Simulator

Thank you for your interest in contributing! This document provides guidelines for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of financial markets and ETFs

### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/etf-creation-redemption-simulator.git
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
   pip install -e .[dev]  # Install development dependencies
   ```

4. **Run tests**
   ```bash
   python -m pytest
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 Python guidelines
- Use type hints where appropriate
- Add comprehensive docstrings
- Keep functions focused and modular

### Testing
- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

### Documentation
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update docstrings for API changes

## 🔄 Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code following guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test thoroughly**
   ```bash
   python -m pytest
   python -m flake8 .
   python -m mypy .
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🐛 Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

## 💡 Feature Requests

Feature requests should:
- Clearly describe the proposed feature
- Explain the use case and benefits
- Consider implementation complexity
- Include examples if applicable

## 📊 Project Structure

```
├── app.py                 # Main Streamlit application
├── data_loader.py         # Market data fetching
├── nav_engine.py          # NAV calculations
├── cost_model.py          # Transaction cost modeling
├── arbitrage_engine.py    # Arbitrage signal generation
├── simulator.py           # Main simulation orchestrator
├── utils.py               # Helper functions
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
├── README.md             # Project documentation
└── LICENSE               # MIT License
```

## 🎯 Contribution Areas

### High Priority
- [ ] Additional ETF default baskets
- [ ] Enhanced error handling
- [ ] Performance optimizations
- [ ] More comprehensive tests

### Medium Priority
- [ ] Machine learning for signal optimization
- [ ] Real-time data integration
- [ ] Portfolio-level arbitrage analysis
- [ ] Advanced visualization features

### Low Priority
- [ ] Mobile responsiveness
- [ ] Multi-language support
- [ ] Database integration
- [ ] API endpoint for external access

## 🤝 Code Review Process

1. **Automated checks** pass (tests, linting, type checking)
2. **Manual review** by maintainers
3. **Feedback** addressed by contributor
4. **Approval** and merge to main branch

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional communication

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Invited to collaborate on future projects

Thank you for contributing to the ETF Creation Redemption Simulator! 🎉
