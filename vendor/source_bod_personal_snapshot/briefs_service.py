"""
Briefs Service - PSIP Integration for Executive Briefs

This service provides the integration layer between PSIP and the application's
briefs endpoint. It:
1. Imports PSIP
2. Instantiates shared PSIP instance
3. Calls generate_executive_brief()
4. Maps output to BriefDetailReadModel

BB-FIN-021: Also integrates SPY 0DTE trade intelligence into the executive brief.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import PSIP
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from psip import PSIP
from outputs.executive_briefs.executive_brief_generator import ExecutiveBrief


# BriefDetailReadModel - The target model for brief details (BB-FIN-021 extended)
@dataclass
class BriefDetailReadModel:
    """Read model for brief details API response"""
    id: str
    date: datetime
    domain_summaries: Dict[str, str]
    strategic_priorities: List[str]
    critical_risks: List[Dict[str, Any]]
    major_opportunities: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    # BB-FIN-021: Tactical trade intelligence section
    tactical_trade_insights: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure tactical_trade_insights is always a list"""
        if self.tactical_trade_insights is None:
            self.tactical_trade_insights = []


# Shared PSIP instance
_psip_instance: Optional[PSIP] = None


def get_psip_instance(total_capital: float = 100000) -> PSIP:
    """
    Get or create the shared PSIP instance.
    
    This follows the singleton pattern to ensure a single PSIP instance
    is shared across the application.
    
    Args:
        total_capital: Total capital for the PSIP system
        
    Returns:
        PSIP instance
    """
    global _psip_instance
    
    if _psip_instance is None:
        _psip_instance = PSIP(total_capital=total_capital)
    
    return _psip_instance


def process_signal(signal_data: dict):
    """
    Process a signal through PSIP.
    
    Args:
        signal_data: Signal data dictionary with source, type, domain, payload
        
    Returns:
        Processed signal
    """
    psip = get_psip_instance()
    return psip.process_signal(signal_data)


def analyze_domain(domain: str) -> dict:
    """
    Analyze a specific domain.
    
    Args:
        domain: Domain name (finance, health, career, relationships, intelligence, life_architecture)
        
    Returns:
        Domain analysis results
    """
    psip = get_psip_instance()
    return psip.analyze_domain(domain)


def get_system_status() -> dict:
    """
    Get overall system status.
    
    Returns:
        System status dictionary
    """
    psip = get_psip_instance()
    return psip.get_system_status()


def generate_executive_brief() -> BriefDetailReadModel:
    """
    Generate an executive brief from PSIP.
    
    This is the main function that:
    1. Gets the PSIP instance
    2. Calls generate_executive_brief() on PSIP
    3. Maps the output to BriefDetailReadModel
    
    Returns:
        BriefDetailReadModel with all brief data
    """
    psip = get_psip_instance()
    
    # Call PSIP's generate_executive_brief
    brief: ExecutiveBrief = psip.generate_executive_brief()
    
    # Map to BriefDetailReadModel
    return map_to_brief_detail(brief)


def map_to_brief_detail(brief: ExecutiveBrief) -> BriefDetailReadModel:
    """
    Map ExecutiveBrief to BriefDetailReadModel.
    
    BB-FIN-021: Includes tactical_trade_insights mapping.
    
    Args:
        brief: ExecutiveBrief from PSIP
        
    Returns:
        BriefDetailReadModel
    """
    # Get tactical trade insights - handle both dict and object
    tactical_insights = getattr(brief, "tactical_trade_insights", []) or []
    
    return BriefDetailReadModel(
        id=brief.id,
        date=brief.date,
        domain_summaries=brief.domain_summaries,
        strategic_priorities=brief.strategic_priorities,
        critical_risks=brief.critical_risks,
        major_opportunities=brief.major_opportunities,
        recommended_actions=brief.recommended_actions,
        tactical_trade_insights=tactical_insights
    )


def get_brief_summary(brief: BriefDetailReadModel) -> str:
    """
    Get a formatted summary of the brief.
    
    BB-FIN-021: Includes tactical trade intelligence section.
    
    Args:
        brief: BriefDetailReadModel
        
    Returns:
        Formatted summary string
    """
    lines = [
        "=" * 60,
        "EXECUTIVE BRIEF",
        "=" * 60,
        "",
        "📊 Domains: " + ", ".join(brief.domain_summaries.keys()),
        "",
        "🎯 Strategic Priorities:"
    ]
    
    for priority in brief.strategic_priorities:
        lines.append(f"  • {priority}")
    
    lines.extend([
        "",
        "🚀 Opportunities:"
    ])
    
    for opp in brief.major_opportunities:
        domain = opp.get("domain", "?")
        title = opp.get("title", "?")
        strength = opp.get("strength", 0.5)
        source = opp.get("source", "")
        source_str = f" [{source}]" if source else ""
        lines.append(f"  • {domain.capitalize()}: {title} (strength: {strength}){source_str}")
    
    if brief.tactical_trade_insights:
        lines.extend([
            "",
            "🎯 Tactical Trade Intelligence (SPY 0DTE):"
        ])
        
        for insight in brief.tactical_trade_insights:
            strategy = insight.get("strategy_name", "?")
            bias = insight.get("market_bias", "?").capitalize()
            rec = insight.get("recommendation", "?").capitalize()
            conf = insight.get("confidence", 0) * 100
            risk = insight.get("risk_level", "?").upper()
            lines.append(f"  • {strategy}")
            lines.append(f"    Bias: {bias} | Rec: {rec} | Conf: {conf:.0f}% | Risk: {risk}")
    
    lines.extend([
        "",
        "⚠️  Critical Risks:"
    ])
    
    if brief.critical_risks:
        for risk in brief.critical_risks:
            domain = risk.get("domain", "?")
            title = risk.get("title", "?")
            severity = risk.get("severity", "?").upper()
            lines.append(f"  • [{severity}] {domain.upper()}: {title}")
    else:
        lines.append("  • None identified")
    
    lines.extend([
        "",
        "📋 Recommended Actions:"
    ])
    
    for action in brief.recommended_actions:
        priority = action.get("priority", "?").upper()
        domain = action.get("domain", "?").upper()
        desc = action.get("action") or action.get("description", "?")
        lines.append(f"  • [{priority}] [{domain}] {desc}")
    
    return "\n".join(lines)


# Demo function to show the integration in action
def demo():
    """Demo function showing PSIP briefs service integration"""
    print("=" * 60)
    print("PSIP Briefs Service Demo")
    print("=" * 60)
    
    # Process some signals
    print("\n📥 Processing signals...")
    
    process_signal({
        "source": "manual",
        "type": "spending",
        "domain": "finance",
        "payload": {"amount": 500}
    })
    
    process_signal({
        "source": "manual",
        "type": "wellness",
        "domain": "health",
        "payload": {"activity": "exercise", "duration": 30}
    })
    
    process_signal({
        "source": "manual",
        "type": "career_progress",
        "domain": "career",
        "payload": {"milestone": "promotion"}
    })
    
    # Get system status
    print("\n📈 System Status:")
    status = get_system_status()
    print(f"  - Domains: {list(status['layer3_domains'].keys())}")
    
    # Generate executive brief
    print("\n🎯 Generating Executive Brief...")
    brief = generate_executive_brief()
    
    # Print formatted summary
    print("\n" + get_brief_summary(brief))
    
    # Show the raw BriefDetailReadModel fields
    print("\n📋 BriefDetailReadModel Fields:")
    print(f"  - id: {brief.id}")
    print(f"  - date: {brief.date}")
    print(f"  - domain_summaries: {brief.domain_summaries}")
    print(f"  - strategic_priorities: {brief.strategic_priorities}")
    print(f"  - critical_risks: {brief.critical_risks}")
    print(f"  - major_opportunities: {brief.major_opportunities}")
    print(f"  - recommended_actions: {brief.recommended_actions}")
    
    return brief


if __name__ == "__main__":
    demo()
