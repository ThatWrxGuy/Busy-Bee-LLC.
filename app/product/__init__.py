# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Product layer - DTOs and formatters for human-consumable outputs."""

from app.product.recommendation_dto import ProductRecommendation
from app.product.executive_brief_dto import ExecutiveBrief, ExecutiveSystemView
from app.product.dashboard_dto import DashboardView

__all__ = [
    "ProductRecommendation",
    "ExecutiveBrief",
    "ExecutiveSystemView",
    "DashboardView",
]
