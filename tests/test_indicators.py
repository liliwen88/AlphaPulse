"""Tests for technical indicator computations."""

import numpy as np
import pandas as pd

from alphapulse.technical.indicators import (
    compute_atr,
    compute_bollinger,
    compute_macd,
    compute_rsi,
    compute_sma,
)
from alphapulse.technical.levels import find_swing_highs, find_swing_lows


class TestSMA:
    def test_basic(self, sample_ohlcv_df):
        sma20 = compute_sma(sample_ohlcv_df["Close"], 20)
        assert len(sma20) == len(sample_ohlcv_df)
        assert not pd.isna(sma20.iloc[-1])

    def test_insufficient_data(self):
        close = pd.Series([10, 20, 30])
        sma5 = compute_sma(close, 5)
        assert pd.isna(sma5.iloc[-1])


class TestRSI:
    def test_normal_range(self, sample_ohlcv_df):
        rsi = compute_rsi(sample_ohlcv_df["Close"])
        assert 0 <= rsi.value <= 100

    def test_signal_labels(self, sample_ohlcv_df):
        rsi = compute_rsi(sample_ohlcv_df["Close"])
        assert rsi.signal in ("overbought", "oversold", "neutral")


class TestMACD:
    def test_returns_result(self, sample_ohlcv_df):
        macd = compute_macd(sample_ohlcv_df["Close"])
        assert macd.histogram == round(macd.macd_line - macd.signal_line, 4)

    def test_signal_not_empty(self, sample_ohlcv_df):
        macd = compute_macd(sample_ohlcv_df["Close"])
        assert macd.signal in (
            "bullish_crossover", "bearish_crossover",
            "above_zero", "below_zero",
        )


class TestBollinger:
    def test_band_ordering(self, sample_ohlcv_df):
        bb = compute_bollinger(sample_ohlcv_df["Close"])
        assert bb.lower < bb.middle < bb.upper
        assert bb.bandwidth > 0

    def test_position(self, sample_ohlcv_df):
        bb = compute_bollinger(sample_ohlcv_df["Close"])
        assert bb.position in ("above_upper", "inside", "below_lower")


class TestATR:
    def test_positive(self, sample_ohlcv_df):
        atr = compute_atr(sample_ohlcv_df)
        assert atr is not None
        assert atr > 0


class TestSwingPoints:
    def test_find_highs(self, sample_ohlcv_df):
        highs = find_swing_highs(sample_ohlcv_df["High"])
        assert isinstance(highs, list)

    def test_find_lows(self, sample_ohlcv_df):
        lows = find_swing_lows(sample_ohlcv_df["Low"])
        assert isinstance(lows, list)
