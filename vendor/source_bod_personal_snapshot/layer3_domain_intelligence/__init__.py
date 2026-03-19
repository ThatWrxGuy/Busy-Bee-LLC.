"""
Layer 3: Domain Intelligence Systems

Contains:
- Finance: Chief Financial Officer + specialist agents
- Health: Chief Health Officer + specialist agents
- Career: Chief Career Officer + specialist agents
- Relationships: Chief Relationship Officer + specialist agents
- Intelligence: Chief Intelligence Officer + specialist agents
- Life Architecture: Chief Life Architect + specialist agents
"""

from .base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport
from .finance.chief_financial_officer.chief_financial_officer import ChiefFinancialOfficer
from .health.chief_health_officer.chief_health_officer import ChiefHealthOfficer
from .career.chief_career_officer.chief_career_officer import ChiefCareerOfficer
from .relationships.chief_relationship_officer.chief_relationship_officer import ChiefRelationshipOfficer
from .intelligence.chief_intelligence_officer.chief_intelligence_officer import ChiefIntelligenceOfficer
from .life_architecture.chief_life_architect.chief_life_architect import ChiefLifeArchitect


__all__ = [
    # Base classes
    "ChiefOfficer",
    "DomainSignal",
    "DomainStrategy",
    "DomainReport",
    
    # Domain Chief Officers
    "ChiefFinancialOfficer",
    "ChiefHealthOfficer",
    "ChiefCareerOfficer",
    "ChiefRelationshipOfficer",
    "ChiefIntelligenceOfficer",
    "ChiefLifeArchitect",
]
