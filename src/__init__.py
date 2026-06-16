"""
Netflix Customer Intelligence Platform
Source utilities package.
"""

from .utils import (
    calculate_health_score,
    calculate_risk_score,
    assign_segment,
    get_risk_category,
    get_health_category,
    simulate_retention_impact,
    load_and_prepare_data
)

__all__ = [
    'calculate_health_score',
    'calculate_risk_score',
    'assign_segment',
    'get_risk_category',
    'get_health_category',
    'simulate_retention_impact',
    'load_and_prepare_data'
]
