"""
Streamlit application for ETF Creation Redemption Simulator.

Interactive web interface for analyzing ETF arbitrage opportunities.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

from simulator import ETFSimulator
from cost_model import CostAssumptions
from utils import (
    validate_ticker, validate_date_format, validate_weights,
    parse_constituents_input, create_sample_constituents,
    get_date_range, format_currency, format_percentage, format_bps,
    generate_report_summary
)


# Configure Streamlit page
st.set_page_config(
    page_title="ETF Creation Redemption Simulator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f77b4;
}
.metric-label {
    font-size: 0.9rem;
    color: #666;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.error-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'simulator' not in st.session_state:
        st.session_state.simulator = ETFSimulator()
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'last_run_params' not in st.session_state:
        st.session_state.last_run_params = {}


def render_sidebar():
    """Render the sidebar with input controls."""
    st.sidebar.header("📊 Simulation Parameters")
    
    # ETF Configuration
    st.sidebar.subheader("ETF Configuration")
    
    etf_ticker = st.sidebar.text_input(
        "ETF Ticker",
        value="SPY",
        help="Enter ETF ticker symbol (e.g., SPY, QQQ, IWM)"
    )
    
    # Constituents
    st.sidebar.subheader("Constituent Basket")
    
    use_default = st.sidebar.checkbox(
        "Use default basket",
        value=True,
        help="Use a pre-defined proxy basket for the ETF"
    )
    
    constituents_input = ""
    if not use_default:
        constituents_input = st.sidebar.text_area(
            "Constituents (TICKER:weight)",
            value="AAPL:0.07,MSFT:0.07,AMZN:0.03,NVDA:0.04",
            help="Enter constituents as TICKER:weight, separated by commas"
        )
    
    # Date Range
    st.sidebar.subheader("Date Range")
    
    default_start, default_end = get_date_range(years_back=1)
    
    start_date = st.sidebar.date_input(
        "Start Date",
        value=default_start,
        help="Analysis start date"
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        value=default_end,
        help="Analysis end date"
    )
    
    # Cost Assumptions
    st.sidebar.subheader("Transaction Cost Assumptions")
    
    with st.sidebar.expander("Trading Costs", expanded=False):
        basket_trading_cost = st.slider(
            "Basket Trading Cost (bps)",
            min_value=0,
            max_value=50,
            value=10,
            help="Cost to trade constituent basket"
        )
        
        etf_trading_cost = st.slider(
            "ETF Trading Cost (bps)",
            min_value=0,
            max_value=25,
            value=5,
            help="Cost to trade ETF shares"
        )
    
    with st.sidebar.expander("ETF Fees", expanded=False):
        creation_fee = st.slider(
            "Creation Fee (bps)",
            min_value=0,
            max_value=100,
            value=25,
            help="ETF creation fee charged by issuer"
        )
        
        redemption_fee = st.slider(
            "Redemption Fee (bps)",
            min_value=0,
            max_value=100,
            value=25,
            help="ETF redemption fee charged by issuer"
        )
    
    with st.sidebar.expander("Market Impact", expanded=False):
        slippage = st.slider(
            "Slippage (bps)",
            min_value=0,
            max_value=50,
            value=10,
            help="Expected slippage on trades"
        )
        
        spread_buffer = st.slider(
            "Spread Buffer (bps)",
            min_value=0,
            max_value=25,
            value=5,
            help="Buffer for bid-ask spread"
        )
    
    with st.sidebar.expander("Other Costs", expanded=False):
        settlement_risk = st.slider(
            "Settlement Risk (bps)",
            min_value=0,
            max_value=25,
            value=5,
            help="Risk premium for settlement timing"
        )
        
        financing_cost = st.slider(
            "Financing Cost (bps)",
            min_value=0,
            max_value=25,
            value=3,
            help="Cost of financing positions"
        )
        
        min_profit_threshold = st.slider(
            "Min Profit Threshold (bps)",
            min_value=0,
            max_value=25,
            value=5,
            help="Minimum profit required to execute arbitrage"
        )
    
    # Run Simulation Button
    st.sidebar.markdown("---")
    
    run_button = st.sidebar.button(
        "🚀 Run Simulation",
        type="primary",
        use_container_width=True
    )
    
    # Return parameters
    params = {
        'etf_ticker': etf_ticker.upper(),
        'use_default': use_default,
        'constituents_input': constituents_input,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'cost_assumptions': CostAssumptions(
            basket_trading_cost=basket_trading_cost / 10000,
            etf_trading_cost=etf_trading_cost / 10000,
            creation_fee=creation_fee / 10000,
            redemption_fee=redemption_fee / 10000,
            slippage=slippage / 10000,
            spread_buffer=spread_buffer / 10000,
            settlement_risk=settlement_risk / 10000,
            financing_cost=financing_cost / 10000,
            min_profit_threshold=min_profit_threshold / 10000
        )
    }
    
    return run_button, params


def validate_inputs(params):
    """Validate user inputs."""
    errors = []
    warnings = []
    
    # Validate ETF ticker
    if not validate_ticker(params['etf_ticker']):
        errors.append("Invalid ETF ticker format")
    
    # Validate dates
    if not validate_date_format(params['start_date']):
        errors.append("Invalid start date format")
    
    if not validate_date_format(params['end_date']):
        errors.append("Invalid end date format")
    
    # Validate date range
    try:
        start = pd.to_datetime(params['start_date'])
        end = pd.to_datetime(params['end_date'])
        
        if start >= end:
            errors.append("Start date must be before end date")
        
        if end > datetime.now():
            warnings.append("End date is in the future")
        
        if (end - start).days < 30:
            warnings.append("Analysis period is less than 30 days")
        
    except Exception as e:
        errors.append(f"Date validation error: {str(e)}")
    
    # Validate constituents if not using default
    if not params['use_default'] and params['constituents_input']:
        constituents = parse_constituents_input(params['constituents_input'])
        is_valid, constituent_errors = validate_weights(constituents)
        
        if not is_valid:
            errors.extend(constituent_errors)
        elif not constituents:
            errors.append("No valid constituents provided")
    
    return errors, warnings


def run_simulation(params):
    """Run the ETF simulation."""
    try:
        # Parse constituents
        if params['use_default']:
            constituents = None
        else:
            constituents = parse_constituents_input(params['constituents_input'])
        
        # Update cost assumptions
        st.session_state.simulator = ETFSimulator(params['cost_assumptions'])
        
        # Run simulation
        results = st.session_state.simulator.run_simulation(
            etf_ticker=params['etf_ticker'],
            constituents=constituents,
            start_date=params['start_date'],
            end_date=params['end_date'],
            use_default_basket=params['use_default']
        )
        
        # Store results
        st.session_state.results = results
        st.session_state.last_run_params = params
        
        return True, None
        
    except Exception as e:
        return False, str(e)


def render_header():
    """Render the application header."""
    st.title("📈 ETF Creation Redemption Simulator")
    st.markdown("""
    Analyze ETF arbitrage opportunities by comparing market prices to intrinsic NAV.
    This tool simulates when authorized participants would execute creations or redemptions
    based on arbitrage thresholds after transaction costs.
    """)
    
    # Educational content
    with st.expander("📚 Understanding ETF Creation & Redemption", expanded=False):
        st.markdown("""
        **ETF Primary vs Secondary Market Mechanics:**
        
        - **Secondary Market**: Where most investors buy/sell ETF shares like stocks
        - **Primary Market**: Where authorized participants (APs) create/redeem ETF shares directly with the issuer
        
        **Arbitrage Process:**
        1. When ETF trades **above** NAV → APs create new shares (buy basket, deliver for ETF shares)
        2. When ETF trades **below** NAV → APs redeem shares (deliver ETF shares, receive basket)
        
        **Key Costs Considered:**
        - Trading costs for constituent basket
        - ETF creation/redemption fees
        - Market impact and slippage
        - Settlement and financing costs
        
        This simulation helps identify profitable arbitrage opportunities after all costs.
        """)


def render_metrics_cards(results):
    """Render summary metrics cards."""
    metrics = st.session_state.simulator.get_summary_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_premium']}</div>
            <div class="metric-label">Average Premium</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['creation_events']}</div>
            <div class="metric-label">Creation Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_arbitrage_profit']}</div>
            <div class="metric-label">Total Arbitrage Profit</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['arbitrage_win_rate']}</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_discount']}</div>
            <div class="metric-label">Average Discount</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['redemption_events']}</div>
            <div class="metric-label">Redemption Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['tracking_error']}</div>
            <div class="metric-label">Tracking Error</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['correlation']}</div>
            <div class="metric-label">Correlation</div>
        </div>
        """, unsafe_allow_html=True)


def render_price_chart(results):
    """Render ETF price vs NAV chart."""
    chart_data = st.session_state.simulator.get_chart_data()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('ETF Price vs NAV', 'Premium/Discount'),
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4]
    )
    
    # Price chart
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['etf_prices'],
            name='ETF Price',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['nav_values'],
            name='NAV',
            line=dict(color='red', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Premium/Discount chart
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['premium_discount'],
            name='Premium/Discount',
            line=dict(color='green', width=1.5)
        ),
        row=2, col=1
    )
    
    # Threshold lines
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['creation_threshold'],
            name='Creation Threshold',
            line=dict(color='orange', width=1, dash='dot')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['redemption_threshold'],
            name='Redemption Threshold',
            line=dict(color='purple', width=1, dash='dot')
        ),
        row=2, col=1
    )
    
    # Mark trading events
    trading_events = results['trading_events']
    if not trading_events.empty:
        creation_events = trading_events[trading_events['signal'] == 'CREATE']
        redemption_events = trading_events[trading_events['signal'] == 'REDEEM']
        
        if not creation_events.empty:
            fig.add_trace(
                go.Scatter(
                    x=creation_events.index,
                    y=creation_events['premium_discount'],
                    mode='markers',
                    name='Creation Events',
                    marker=dict(color='orange', size=8, symbol='triangle-up')
                ),
                row=2, col=1
            )
        
        if not redemption_events.empty:
            fig.add_trace(
                go.Scatter(
                    x=redemption_events.index,
                    y=redemption_events['premium_discount'],
                    mode='markers',
                    name='Redemption Events',
                    marker=dict(color='purple', size=8, symbol='triangle-down')
                ),
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        height=600,
        title_text="ETF Price Analysis and Arbitrage Opportunities",
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Premium/Discount (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)


def render_trading_events_table(results):
    """Render trading events table."""
    trading_events = results['trading_events']
    
    if trading_events.empty:
        st.info("No arbitrage opportunities detected in the analysis period.")
        return
    
    st.subheader("📋 Trading Events")
    
    # Format data for display
    display_data = trading_events.copy()
    display_data['Date'] = display_data.index.strftime('%Y-%m-%d')
    display_data['Signal'] = display_data['signal']
    display_data['Premium/Discount'] = display_data['premium_discount'].apply(lambda x: f"{x:.2f}%")
    display_data['Profit'] = display_data['profit'].apply(format_currency)
    display_data['Profit %'] = display_data['profit_pct'].apply(lambda x: f"{x:.2f}%")
    display_data['NAV Value'] = display_data['nav_value'].apply(format_currency)
    
    # Select columns to display
    columns_to_show = ['Date', 'Signal', 'Premium/Discount', 'Profit', 'Profit %', 'NAV Value']
    
    st.dataframe(
        display_data[columns_to_show],
        use_container_width=True,
        hide_index=True
    )


def render_cumulative_profits_chart(results):
    """Render cumulative profits chart."""
    chart_data = st.session_state.simulator.get_chart_data()
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=chart_data['dates'],
            y=chart_data['cumulative_profits'],
            mode='lines',
            name='Cumulative Profits',
            line=dict(color='green', width=2)
        )
    )
    
    fig.update_layout(
        title="Cumulative Arbitrage Profits Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative Profit ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_cost_assumptions_summary(results):
    """Render cost assumptions summary."""
    st.subheader("💰 Cost Assumptions Summary")
    
    cost_assumptions = results['cost_assumptions']
    
    # Group costs by category
    trading_costs = {
        'Basket Trading': cost_assumptions.get('basket_trading_cost', 0),
        'ETF Trading': cost_assumptions.get('etf_trading_cost', 0)
    }
    
    etf_fees = {
        'Creation Fee': cost_assumptions.get('creation_fee', 0),
        'Redemption Fee': cost_assumptions.get('redemption_fee', 0)
    }
    
    market_impact = {
        'Slippage': cost_assumptions.get('slippage', 0),
        'Spread Buffer': cost_assumptions.get('spread_buffer', 0)
    }
    
    other_costs = {
        'Settlement Risk': cost_assumptions.get('settlement_risk', 0),
        'Financing Cost': cost_assumptions.get('financing_cost', 0),
        'Min Profit Threshold': cost_assumptions.get('min_profit_threshold', 0)
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Trading Costs (bps):**")
        for cost_name, cost_value in trading_costs.items():
            st.write(f"- {cost_name}: {cost_value:.0f} bps")
        
        st.write("**ETF Fees (bps):**")
        for fee_name, fee_value in etf_fees.items():
            st.write(f"- {fee_name}: {fee_value:.0f} bps")
    
    with col2:
        st.write("**Market Impact (bps):**")
        for impact_name, impact_value in market_impact.items():
            st.write(f"- {impact_name}: {impact_value:.0f} bps")
        
        st.write("**Other Costs (bps):**")
        for other_name, other_value in other_costs.items():
            st.write(f"- {other_name}: {other_value:.0f} bps")


def render_export_section(results):
    """Render export options."""
    st.subheader("📤 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to CSV"):
            try:
                filename = st.session_state.simulator.export_results()
                st.success(f"Results exported to {filename}_*.csv files")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("📄 Generate Report"):
            report = generate_report_summary(results)
            st.text_area("Simulation Report", report, height=300)


def main():
    """Main application function."""
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    run_button, params = render_sidebar()
    
    # Handle simulation run
    if run_button:
        # Validate inputs
        errors, warnings = validate_inputs(params)
        
        # Display warnings
        if warnings:
            for warning in warnings:
                st.warning(warning)
        
        # Display errors and stop if any
        if errors:
            for error in errors:
                st.error(error)
            st.stop()
        
        # Run simulation
        with st.spinner("Running simulation... This may take a few moments."):
            success, error = run_simulation(params)
        
        if not success:
            st.error(f"Simulation failed: {error}")
            st.stop()
        
        st.success("Simulation completed successfully!")
    
    # Display results if available
    if st.session_state.results:
        results = st.session_state.results
        
        # Validation warnings
        validation = st.session_state.simulator.validate_simulation()
        if not validation['is_valid']:
            for error in validation['errors']:
                st.error(error)
        
        if validation['warnings']:
            for warning in validation['warnings']:
                st.warning(warning)
        
        # Main dashboard
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Metrics cards
        render_metrics_cards(results)
        
        # Charts
        st.markdown("---")
        render_price_chart(results)
        
        # Cumulative profits
        st.markdown("---")
        render_cumulative_profits_chart(results)
        
        # Trading events
        st.markdown("---")
        render_trading_events_table(results)
        
        # Cost assumptions
        st.markdown("---")
        render_cost_assumptions_summary(results)
        
        # Export options
        st.markdown("---")
        render_export_section(results)
    
    else:
        # Welcome message
        st.info("👋 Configure parameters in the sidebar and click 'Run Simulation' to begin analysis.")


if __name__ == "__main__":
    main()
