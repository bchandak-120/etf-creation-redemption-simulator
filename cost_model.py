"""
Transaction cost model for ETF Creation Redemption Simulator.

Models various costs associated with ETF creation and redemption arbitrage.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CostAssumptions:
    """Transaction cost assumptions for ETF arbitrage."""
    
    # Trading costs
    basket_trading_cost: float = 0.0010  # 10 bps for constituent trading
    etf_trading_cost: float = 0.0005     # 5 bps for ETF trading
    
    # ETF-specific costs
    creation_fee: float = 0.0025         # 25 bps creation fee
    redemption_fee: float = 0.0025      # 25 bps redemption fee
    
    # Market impact costs
    slippage: float = 0.0010            # 10 bps slippage
    spread_buffer: float = 0.0005       # 5 bps spread buffer
    
    # Operational costs
    settlement_risk: float = 0.0005     # 5 bps settlement risk
    financing_cost: float = 0.0003      # 3 bps financing
    
    # Minimum profit threshold
    min_profit_threshold: float = 0.0005 # 5 bps minimum profit


class CostModel:
    """Models transaction costs for ETF arbitrage strategies."""
    
    def __init__(self, assumptions: CostAssumptions = None):
        self.assumptions = assumptions or CostAssumptions()
    
    def calculate_creation_costs(self, nav_value: float) -> Dict[str, float]:
        """
        Calculate total costs for ETF creation arbitrage.
        
        Args:
            nav_value: NAV value of creation unit
            
        Returns:
            Dictionary of cost components and total
        """
        costs = {}
        
        # Trading costs
        costs['basket_trading'] = nav_value * self.assumptions.basket_trading_cost
        costs['etf_trading'] = nav_value * self.assumptions.etf_trading_cost
        
        # ETF fees
        costs['creation_fee'] = nav_value * self.assumptions.creation_fee
        
        # Market impact
        costs['slippage'] = nav_value * self.assumptions.slippage
        costs['spread_buffer'] = nav_value * self.assumptions.spread_buffer
        
        # Operational costs
        costs['settlement_risk'] = nav_value * self.assumptions.settlement_risk
        costs['financing_cost'] = nav_value * self.assumptions.financing_cost
        
        # Total cost
        costs['total_cost'] = sum(costs.values())
        
        return costs
    
    def calculate_redemption_costs(self, nav_value: float) -> Dict[str, float]:
        """
        Calculate total costs for ETF redemption arbitrage.
        
        Args:
            nav_value: NAV value of redemption unit
            
        Returns:
            Dictionary of cost components and total
        """
        costs = {}
        
        # Trading costs
        costs['basket_trading'] = nav_value * self.assumptions.basket_trading_cost
        costs['etf_trading'] = nav_value * self.assumptions.etf_trading_cost
        
        # ETF fees
        costs['redemption_fee'] = nav_value * self.assumptions.redemption_fee
        
        # Market impact
        costs['slippage'] = nav_value * self.assumptions.slippage
        costs['spread_buffer'] = nav_value * self.assumptions.spread_buffer
        
        # Operational costs
        costs['settlement_risk'] = nav_value * self.assumptions.settlement_risk
        costs['financing_cost'] = nav_value * self.assumptions.financing_cost
        
        # Total cost
        costs['total_cost'] = sum(costs.values())
        
        return costs
    
    def get_creation_threshold(self, nav_value: float) -> float:
        """
        Calculate minimum premium required for profitable creation.
        
        Args:
            nav_value: NAV value of creation unit
            
        Returns:
            Required premium threshold (as percentage)
        """
        costs = self.calculate_creation_costs(nav_value)
        total_cost_pct = costs['total_cost'] / nav_value
        threshold = total_cost_pct + self.assumptions.min_profit_threshold
        
        return threshold * 100  # Convert to percentage
    
    def get_redemption_threshold(self, nav_value: float) -> float:
        """
        Calculate minimum discount required for profitable redemption.
        
        Args:
            nav_value: NAV value of redemption unit
            
        Returns:
            Required discount threshold (as percentage)
        """
        costs = self.calculate_redemption_costs(nav_value)
        total_cost_pct = costs['total_cost'] / nav_value
        threshold = total_cost_pct + self.assumptions.min_profit_threshold
        
        return threshold * 100  # Convert to percentage
    
    def calculate_arbitrage_profit(
        self, 
        premium_discount_pct: float, 
        nav_value: float,
        action: str
    ) -> Dict[str, float]:
        """
        Calculate arbitrage profit for given premium/discount and action.
        
        Args:
            premium_discount_pct: Premium (+) or discount (-) as percentage
            nav_value: NAV value of trading unit
            action: 'create' or 'redeem'
            
        Returns:
            Dictionary with profit calculations
        """
        if action == 'create':
            if premium_discount_pct <= 0:
                return {'profit': 0, 'profit_pct': 0, 'is_profitable': False}
            
            costs = self.calculate_creation_costs(nav_value)
            gross_profit = nav_value * (premium_discount_pct / 100)
            net_profit = gross_profit - costs['total_cost']
            
        elif action == 'redeem':
            if premium_discount_pct >= 0:
                return {'profit': 0, 'profit_pct': 0, 'is_profitable': False}
            
            costs = self.calculate_redemption_costs(nav_value)
            gross_profit = nav_value * (-premium_discount_pct / 100)  # Convert discount to positive
            net_profit = gross_profit - costs['total_cost']
            
        else:
            raise ValueError("Action must be 'create' or 'redeem'")
        
        return {
            'profit': net_profit,
            'profit_pct': (net_profit / nav_value) * 100,
            'is_profitable': net_profit > 0,
            'gross_profit': gross_profit if 'gross_profit' in locals() else 0,
            'total_cost': costs['total_cost']
        }
    
    def update_assumptions(self, **kwargs) -> None:
        """
        Update cost assumptions.
        
        Args:
            **kwargs: New assumption values
        """
        for key, value in kwargs.items():
            if hasattr(self.assumptions, key):
                setattr(self.assumptions, key, value)
            else:
                raise ValueError(f"Invalid assumption: {key}")
    
    def get_assumptions_summary(self) -> Dict[str, float]:
        """
        Get summary of current cost assumptions.
        
        Returns:
            Dictionary of assumptions in basis points
        """
        assumptions_dict = {}
        for field, value in self.assumptions.__dict__.items():
            if isinstance(value, float):
                assumptions_dict[field] = value * 10000  # Convert to bps
        
        return assumptions_dict
