from __future__ import annotations

from datetime import date, datetime, timedelta

from alphapulse.macro.models import EconomicEvent


def get_current_week_events(reference_date: date | None = None) -> list[EconomicEvent]:
    """Get economic events for the current week.

    In a full implementation, this would scrape investing.com or use a paid API.
    This lightweight version provides known scheduled events.
    """
    today = reference_date or date.today()
    # Find the Monday of this week
    monday = today - timedelta(days=today.weekday())
    week_end = monday + timedelta(days=6)

    return _filter_events_by_range(monday, week_end)


def get_upcoming_events(n_days: int = 30, reference_date: date | None = None) -> list[EconomicEvent]:
    """Get upcoming economic events for the next n_days."""
    today = reference_date or date.today()
    end = today + timedelta(days=n_days)
    return _filter_events_by_range(today, end)


def _filter_events_by_range(start: date, end: date) -> list[EconomicEvent]:
    return [e for e in _KNOWN_EVENTS if start <= e.date <= end]


# Known scheduled economic events for 2026 (approximate dates for recurring releases)
# Users should verify these dates independently.
_KNOWN_EVENTS: list[EconomicEvent] = []


def _init_2026_events() -> list[EconomicEvent]:
    """Build a list of recurring economic events for 2026.
    Note: Exact dates may shift. Always verify with official sources.
    """
    events = []

    # Monthly recurring events (approximate dates)
    for month in range(1, 13):
        # CPI release (around 10th-15th of each month)
        events.append(EconomicEvent(
            date=date(2026, month, 12),
            time="08:30 ET",
            event="CPI (MoM) — Consumer Price Index",
            period=date(2025, month, 1).strftime("%b") if month == 1 else date(2026, month - 1, 1).strftime("%b"),
            impact="High",
        ))
        # PPI release
        events.append(EconomicEvent(
            date=date(2026, month, 14),
            time="08:30 ET",
            event="PPI (MoM) — Producer Price Index",
            period=date(2025, month, 1).strftime("%b") if month == 1 else date(2026, month - 1, 1).strftime("%b"),
            impact="Medium",
        ))
        # NFP (first Friday of each month)
        day = sorted([d for d in range(1, 8) if date(2026, month, d).weekday() == 4])[0]
        events.append(EconomicEvent(
            date=date(2026, month, day),
            time="08:30 ET",
            event="Nonfarm Payrolls & Unemployment Rate",
            period=date(2025, 12, 1).strftime("%b") if month == 1 else date(2026, month - 1, 1).strftime("%b"),
            impact="High",
        ))
        # Retail Sales
        events.append(EconomicEvent(
            date=date(2026, month, 16),
            time="08:30 ET",
            event="Retail Sales (MoM)",
            period=date(2025, month, 1).strftime("%b") if month == 1 else date(2026, month - 1, 1).strftime("%b"),
            impact="Medium",
        ))
        # ISM Manufacturing PMI (first business day)
        events.append(EconomicEvent(
            date=date(2026, month, 2),
            time="10:00 ET",
            event="ISM Manufacturing PMI",
            impact="Medium",
        ))

    # FOMC Meetings 2026 (tentative schedule)
    fomc_dates = [
        date(2026, 1, 28),
        date(2026, 3, 18),
        date(2026, 5, 6),
        date(2026, 6, 17),
        date(2026, 7, 29),
        date(2026, 9, 16),
        date(2026, 11, 4),
        date(2026, 12, 16),
    ]
    for fomc in fomc_dates:
        events.append(EconomicEvent(
            date=fomc,
            time="14:00 ET",
            event="FOMC Interest Rate Decision",
            impact="High",
        ))

    return events


_KNOWN_EVENTS = _init_2026_events()
