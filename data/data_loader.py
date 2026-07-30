"""
Data loader utilities for Trading-AI.

Provides simple helpers to load cached data or request fresh data via
MarketData. Designed to be thin and unit-testable.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd

from data.market_data import MarketData, MarketDataConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class DataLoader:
    """Thin convenience wrapper around MarketData for loading datasets.

    The loader supports loading multiple tickers and returning a mapping of
    ticker -> DataFrame. It is intentionally small to remain easily tested.
    """

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        config = MarketDataConfig()
        if cache_dir:
            config.cache_dir = cache_dir
        self._md = MarketData(config)

    def load(self, tickers: List[str], interval: str = "1d", period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Load data for multiple tickers.

        Args:
            tickers: List of tickers to load.
            interval: Data interval.
            period: Period alias for historical data.

        Returns:
            Mapping of ticker -> DataFrame
        """
        logger.info("Loading tickers %s", tickers)
        return self._md.download_multiple(tickers, interval=interval, period=period)
