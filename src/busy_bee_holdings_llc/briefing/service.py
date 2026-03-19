from __future__ import annotations
from datetime import datetime, UTC

class ExecutiveBriefService:
    def generate(self, payload: dict) -> dict:
        focus = payload.get("focus_areas", [])
        founder = payload.get("founder") or payload.get("user_name")
        goal = payload.get("goal")
        summary = payload.get("summary") or (f"Primary objective: {goal}" if goal else "Initial strategic cycle")
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "system_status": "Healthy",
            "founder": founder,
            "strategic_cycle_id": payload.get("strategic_cycle_id"),
            "posture": payload.get("posture"),
            "summary": summary,
            "top_priorities": [
                "Protect Busy Bee intellectual property inside HoldCo.",
                "Complete Wyoming and Florida filings and bank setup.",
                f"Advance execution in focus areas: {', '.join(focus) if focus else 'core operations'}."
            ],
            "human_approval_required": True,
        }
