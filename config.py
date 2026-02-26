"""
Configuration and constants for the Autonomous Strategy Evolution Platform.
Centralizes all configurable parameters for maintainability and easy environment switching.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List
import logging
from datetime import timedelta

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtesting engine"""
    initial_capital: float = 10000.0
    commission_rate: float = 0.001  # 0.1% commission
    slippage_rate: float = 0.0005   # 0.05% slippage
    risk_free_rate: float = 0.02    # 2% annual risk-free rate
    min_trades_for_evaluation: int = 10
    max_drawdown_threshold: float = 0.25  # 25% max drawdown
    
@dataclass
class StrategyConfig:
    """Configuration for strategy generation"""
    population_size: int = 50
    max_generations: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elite_size: int = 5
    min_indicators: int = 2
    max_indicators: int = 5
    
@dataclass
class DataConfig:
    """Configuration for data collection"""
    symbols: List[str] = None
    timeframe: str = '1h'
    lookback_days: int = 365
    train_test_split: float = 0.7
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    
@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    collection_strategies: str = "evolving_strategies"
    collection_backtests: str = "backtest_results"
    collection_deployments: str = "live_deployments"
    collection_metrics: str = "performance_metrics"
    
@dataclass
class PlatformConfig:
    """Main platform configuration"""
    backtest: BacktestConfig = BacktestConfig()
    strategy: StrategyConfig = StrategyConfig()
    data: DataConfig = DataConfig()
    firebase: FirebaseConfig = FirebaseConfig()
    max_parallel_backtests: int = 5
    evolution_interval_hours: int = 24
    performance_evaluation_window: int = 30  # days
    
    @classmethod
    def from_env(cls) -> 'PlatformConfig':
        """Create configuration from environment variables"""
        try:
            return cls(
                backtest=BacktestConfig(
                    initial_capital=float(os.getenv('INITIAL_CAPITAL', 10000.0)),
                    commission_rate=float(os.getenv('COMMISSION_RATE', 0.001)),
                    slippage_rate=float(os.getenv('SLIPPAGE_RATE', 0.0005))
                ),
                strategy=StrategyConfig(
                    population_size=int(os.getenv('POPULATION_SIZE', 50)),
                    mutation_rate=float(os.getenv('MUTATION_RATE', 0.1))
                )
            )
        except ValueError as e:
            logger.error(f"Error loading config from env: {e}")
            return cls()  # Return default config

# Global configuration instance
CONFIG = PlatformConfig()