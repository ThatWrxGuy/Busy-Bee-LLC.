"""
Finance Trade Intelligence Service - SPY 0DTE Adapter

This service provides the integration layer between the SPY 0DTE tactical
trade engine and PSIP executive brief pipeline.

Responsibilities:
- Interface with SPY 0DTE engine
- Collect latest recommendation / trade report
- Normalize to stable schema for PSIP consumption
- Return None or empty object safely if unavailable (graceful degradation)
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import random

from tactical_trade_models import (
    TacticalTradeInsight,
    TradeOpportunity,
    TradeRisk,
    TradeAction,
    RECOMMENDATION_PRIORITY_MAP,
    QUALITY_STRENGTH_MAP,
    RISK_SEVERITY_MAP
)

logger = logging.getLogger(__name__)


# ============================================================
# SPY 0DTE Engine Interface
# ============================================================

def get_spy0dte_engine_report() -> Optional[Dict[str, Any]]:
    """
    Get the latest SPY 0DTE engine report.
    
    In production, this would call the actual SPY 0DTE engine.
    For now, returns a simulated report for demonstration.
    
    Returns:
        Raw engine report dict or None if unavailable
    """
    # Simulate engine availability - in production this would be a real API call
    # For demo purposes, we'll generate a report 80% of the time
    if random.random() > 0.2:  # 80% availability
        return _generate_mock_spy0dte_report()
    return None


def _generate_mock_spy0dte_report() -> Dict[str, Any]:
    """Generate a mock SPY 0DTE report for demonstration"""
    
    # Sample data for realistic mock reports
    setups = [
        {
            "strategy_id": "spy0dte_momentum_001",
            "strategy_name": "SPY 0DTE Momentum Breakout",
            "instrument": "SPY",
            "market_bias": "bullish",
            "recommendation": "enter",
            "confidence": 0.82,
            "risk_level": "high",
            "setup_quality": "strong",
            "thesis": "Opening momentum and trend continuation align with intraday breakout conditions. Volume confirms institutional flow.",
            "entry_criteria": [
                "Price holds above opening range high",
                "Volume confirms breakout (>1.5x avg)",
                "RSI momentum remains bullish above 60"
            ],
            "invalidation_criteria": [
                "Loss of key support at open",
                "Failed breakout within first hour",
                "Negative divergence on momentum"
            ],
            "targets": [
                "First scale at +0.5% from entry",
                "Full target at +1.0%",
                "Exit if momentum weakens"
            ],
            "warnings": [
                "0DTE decay accelerates rapidly after 10am",
                "Reversal risk elevated during macro headlines",
                "High gamma exposure may cause rapid swings"
            ]
        },
        {
            "strategy_id": "spy0dte_mean_reversion_002",
            "strategy_name": "SPY 0DTE Mean Reversion",
            "instrument": "SPY",
            "market_bias": "bearish",
            "recommendation": "watch",
            "confidence": 0.65,
            "risk_level": "medium",
            "setup_quality": "moderate",
            "thesis": "Overextension above VWAP with negative breadth divergence suggests mean reversion opportunity.",
            "entry_criteria": [
                "Price rejects from VWAP + 0.5%",
                "Bearish candle formation",
                "Volume on rejection"
            ],
            "invalidation_criteria": [
                "Sustained break above VWAP + 1%",
                "Broad market strength continues"
            ],
            "targets": [
                "First target: VWAP",
                "Full target: opening range low"
            ],
            "warnings": [
                "Trend may continue longer than expected",
                "Watch for overnight gap risk"
            ]
        },
        {
            "strategy_id": "spy0dte_volatility_compression_003",
            "strategy_name": "SPY 0DTE Volatility Compression",
            "instrument": "SPY",
            "market_bias": "neutral",
            "recommendation": "avoid",
            "confidence": 0.45,
            "risk_level": "extreme",
            "setup_quality": "weak",
            "thesis": "IV crush expected post-event. Direction unclear. Best to stay on sidelines.",
            "entry_criteria": [],
            "invalidation_criteria": [
                "Clear directional move with volume"
            ],
            "targets": [],
            "warnings": [
                "Unknown directional outcome",
                "IV crush will penalize long options",
                "High gamma/risk of gap"
            ]
        }
    ]
    
    # Rotate through setups based on time of day
    hour = datetime.now().hour
    
    if 9 <= hour < 11:
        # Morning - momentum setup
        report = setups[0]
    elif 11 <= hour < 14:
        # Midday - mean reversion
        report = setups[1]
    else:
        # End of day / other - volatility compression
        report = setups[2]
    
    report["generated_at"] = datetime.now().isoformat()
    return report


# ============================================================
# Normalization Functions
# ============================================================

def map_spy0dte_report_to_tactical_insight(
    report: Dict[str, Any]
) -> TacticalTradeInsight:
    """
    Map raw SPY 0DTE report to normalized TacticalTradeInsight.
    
    Args:
        report: Raw engine report dictionary
        
    Returns:
        Normalized TacticalTradeInsight
    """
    # Parse generated_at to datetime
    generated_at = report.get("generated_at")
    if isinstance(generated_at, str):
        try:
            generated_at = datetime.fromisoformat(generated_at)
        except (ValueError, TypeError):
            generated_at = datetime.now()
    
    return TacticalTradeInsight(
        strategy_id=report.get("strategy_id", ""),
        strategy_name=report.get("strategy_name", ""),
        generated_at=generated_at,
        instrument=report.get("instrument", "SPY"),
        market_bias=report.get("market_bias", "neutral"),
        recommendation=report.get("recommendation", "watch"),
        confidence=report.get("confidence", 0.5),
        risk_level=report.get("risk_level", "medium"),
        setup_quality=report.get("setup_quality", "moderate"),
        thesis=report.get("thesis", ""),
        entry_criteria=report.get("entry_criteria", []),
        invalidation_criteria=report.get("invalidation_criteria", []),
        targets=report.get("targets", []),
        warnings=report.get("warnings", []),
        metadata=report.get("metadata", {})
    )


# ============================================================
# Main Service Functions
# ============================================================

def get_latest_spy0dte_trade_insight() -> Optional[TacticalTradeInsight]:
    """
    Get the latest SPY 0DTE trade insight.
    
    This is the main entry point for PSIP to retrieve tactical trade intelligence.
    
    Returns:
        TacticalTradeInsight or None if unavailable
    """
    try:
        report = get_spy0dte_engine_report()
        
        if report is None:
            logger.warning("SPY 0DTE engine report unavailable")
            return None
        
        insight = map_spy0dte_report_to_tactical_insight(report)
        logger.info(f"Retrieved SPY 0DTE insight: {insight.strategy_name}, "
                   f"recommendation={insight.recommendation}, "
                   f"confidence={insight.confidence}")
        
        return insight
        
    except Exception as e:
        logger.error(f"Error retrieving SPY 0DTE trade insight: {e}")
        return None


# ============================================================
# Brief Enrichment Functions
# ============================================================

def build_trade_opportunity(insight: TacticalTradeInsight) -> Optional[Dict[str, Any]]:
    """
    Build a trade opportunity from tactical insight.
    
    Only creates opportunity if:
    - recommendation is 'enter' or 'watch'
    - confidence is above threshold
    - setup quality is at least moderate
    
    Args:
        insight: TacticalTradeInsight
        
    Returns:
        Dict representation of opportunity or None
    """
    if not insight.is_actionable(confidence_threshold=0.6):
        return None
    
    return TradeOpportunity(
        domain="finance",
        title=f"SPY 0DTE tactical setup: {insight.strategy_name}",
        description=insight.thesis,
        strength=QUALITY_STRENGTH_MAP.get(insight.setup_quality, "medium"),
        confidence=insight.confidence,
        market_bias=insight.market_bias,
        instrument=insight.instrument,
        source="spy0dte_engine"
    ).to_dict()


def build_trade_risk(insight: TacticalTradeInsight) -> Optional[Dict[str, Any]]:
    """
    Build a trade risk from tactical insight.
    
    Creates risk if:
    - risk_level is high or extreme
    - warnings are present
    
    Args:
        insight: TacticalTradeInsight
        
    Returns:
        Dict representation of risk or None
    """
    if not insight.has_elevated_risk():
        return None
    
    # Build description from warnings or thesis
    if insight.warnings:
        description = "; ".join(insight.warnings)
    else:
        description = f"{insight.risk_level.title()} risk: {insight.thesis}"
    
    return TradeRisk(
        domain="finance",
        title=f"SPY 0DTE tactical risk: {insight.risk_level.title()} level",
        description=description,
        severity=RISK_SEVERITY_MAP.get(insight.risk_level, "medium"),
        source="spy0dte_engine"
    ).to_dict()


def build_trade_action(insight: TacticalTradeInsight) -> Optional[Dict[str, Any]]:
    """
    Build a recommended action from tactical insight.
    
    Args:
        insight: TacticalTradeInsight
        
    Returns:
        Dict representation of action
    """
    # Build action text based on recommendation
    if insight.recommendation == "enter":
        action_text = _build_enter_action(insight)
    elif insight.recommendation == "watch":
        action_text = _build_watch_action(insight)
    elif insight.recommendation == "avoid":
        action_text = "Avoid SPY 0DTE trades today. Market conditions do not favor tactical entry."
    elif insight.recommendation == "reduce_risk":
        action_text = "Reduce SPY 0DTE exposure. Consider taking profits or tightening stops."
    else:
        action_text = f"Monitor SPY 0DTE: {insight.thesis[:100]}"
    
    return TradeAction(
        domain="finance",
        action=action_text,
        priority=RECOMMENDATION_PRIORITY_MAP.get(insight.recommendation, "medium"),
        action_type="tactical_trade",
        confidence=insight.confidence,
        strategy_name=insight.strategy_name,
        entry_criteria=insight.entry_criteria,
        risk_level=insight.risk_level,
        source="spy0dte_engine"
    ).to_dict()


def _build_enter_action(insight: TacticalTradeInsight) -> str:
    """Build action text for enter recommendation"""
    criteria = insight.entry_criteria[:2] if insight.entry_criteria else []
    
    if criteria:
        criteria_text = " and ".join(criteria[:2])
        return (f"Prepare SPY 0DTE {insight.market_bias} setup. "
                f"Execute only if: {criteria_text}. "
                f"Confidence: {insight.confidence:.0%}")
    else:
        return (f"Execute SPY 0DTE {insight.market_bias} trade "
                f"per {insight.strategy_name}. Confidence: {insight.confidence:.0%}")


def _build_watch_action(insight: TacticalTradeInsight) -> str:
    """Build action text for watch recommendation"""
    return (f"Watch for SPY 0DTE {insight.market_bias} entry. "
            f"Thesis: {insight.thesis[:80]}... "
            f"Confidence: {insight.confidence:.0%}")


def build_finance_trade_summary_appendix(insight: TacticalTradeInsight) -> str:
    """
    Build a finance domain summary appendix for tactical trade intelligence.
    
    Args:
        insight: TacticalTradeInsight
        
    Returns:
        Formatted summary string
    """
    parts = []
    
    # Bias and confidence
    bias_text = insight.market_bias.capitalize()
    conf_pct = insight.confidence * 100
    risk_text = insight.risk_level.capitalize()
    
    parts.append(
        f"Tactical SPY 0DTE: {bias_text} bias ({conf_pct:.0f}% confidence, "
        f"{risk_text} risk)"
    )
    
    # Recommendation
    rec_text = insight.recommendation.replace("_", " ").capitalize()
    parts.append(f"Recommendation: {rec_text}")
    
    # Action readiness
    if insight.is_actionable():
        parts.append(f"Setup quality: {insight.setup_quality.capitalize()}")
    else:
        parts.append("No actionable setup currently")
    
    # Key warnings
    if insight.warnings:
        parts.append(f"Warnings: {len(insight.warnings)} risk factor(s) noted")
    
    return ". ".join(parts)


def enrich_brief_with_trade_insight(
    brief: Any,
    insight: TacticalTradeInsight
) -> Any:
    """
    Enrich an executive brief with tactical trade insight.
    
    Args:
        brief: ExecutiveBrief object
        insight: TacticalTradeInsight
        
    Returns:
        Enriched ExecutiveBrief
    """
    # Add to opportunities
    opportunity = build_trade_opportunity(insight)
    if opportunity:
        # Check for duplicates
        existing_opps = [o.get("title", "") for o in getattr(brief, "major_opportunities", [])]
        if opportunity["title"] not in existing_opps:
            brief.major_opportunities.append(opportunity)
    
    # Add to risks
    risk = build_trade_risk(insight)
    if risk:
        existing_risks = [r.get("title", "") for r in getattr(brief, "critical_risks", [])]
        if risk["title"] not in existing_risks:
            brief.critical_risks.append(risk)
    
    # Add to recommended actions
    action = build_trade_action(insight)
    if action:
        existing_actions = [a.get("action", "") for a in getattr(brief, "recommended_actions", [])]
        if action["action"] not in existing_actions:
            brief.recommended_actions.append(action)
    
    # Add to tactical trade insights section
    if hasattr(brief, "tactical_trade_insights"):
        brief.tactical_trade_insights.append(insight.to_dict())
    else:
        brief.tactical_trade_insights = [insight.to_dict()]
    
    # Enrich finance domain summary
    if hasattr(brief, "domain_summaries") and "finance" in brief.domain_summaries:
        trade_summary = build_finance_trade_summary_appendix(insight)
        existing_summary = brief.domain_summaries.get("finance", "")
        
        # Append to existing summary
        if existing_summary and not existing_summary.endswith("."):
            existing_summary += "."
        brief.domain_summaries["finance"] = f"{existing_summary} {trade_summary}"
    
    return brief


# ============================================================
# Demo Function
# ============================================================

def demo():
    """Demo function showing SPY 0DTE trade intelligence"""
    print("=" * 60)
    print("SPY 0DTE Trade Intelligence Demo")
    print("=" * 60)
    
    # Get latest insight
    insight = get_latest_spy0dte_trade_insight()
    
    if insight is None:
        print("\n⚠️  SPY 0DTE engine unavailable (graceful degradation)")
        return
    
    print(f"\n📊 Strategy: {insight.strategy_name}")
    print(f"   Instrument: {insight.instrument}")
    print(f"   Market Bias: {insight.market_bias}")
    print(f"   Recommendation: {insight.recommendation}")
    print(f"   Confidence: {insight.confidence:.0%}")
    print(f"   Risk Level: {insight.risk_level}")
    print(f"   Setup Quality: {insight.setup_quality}")
    print(f"   Thesis: {insight.thesis}")
    
    print("\n🎯 Entry Criteria:")
    for criterion in insight.entry_criteria:
        print(f"   • {criterion}")
    
    print("\n⚠️  Warnings:")
    for warning in insight.warnings:
        print(f"   • {warning}")
    
    # Build mapped objects
    print("\n📋 Mapped Objects:")
    
    opportunity = build_trade_opportunity(insight)
    if opportunity:
        print(f"   Opportunity: {opportunity}")
    
    risk = build_trade_risk(insight)
    if risk:
        print(f"   Risk: {risk}")
    
    action = build_trade_action(insight)
    if action:
        print(f"   Action: {action}")
    
    print("\n📝 Finance Summary Appendix:")
    print(f"   {build_finance_trade_summary_appendix(insight)}")


if __name__ == "__main__":
    demo()
