from pydantic import BaseModel


class StrategicRecommendation(BaseModel):
    id: str
    domain: str
    title: str
    rationale: str
    requires_human_approval: bool = False


class ExecutiveBrief(BaseModel):
    system_status: str
    strategic_posture: str
    top_priorities: list[str]
    recommendations: list[StrategicRecommendation]
