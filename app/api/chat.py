# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Chat API - Conversational interface for LOIS."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import re

from app.product import ProductRecommendation
from app.integrations.lois_integration import lois_integration


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response to user."""
    response: str
    type: str  # recommendation, brief, question, error
    data: Optional[dict] = None


# Simple intent detection patterns
INTENT_PATTERNS = {
    "recommendation": [
        r"recommend\w*",
        r"what should i do",
        r"advice",
        r"suggest\w*",
        r"strategy",
        r"plan",
    ],
    "brief": [
        r"executive brief",
        r"show me.*brief",
        r"summary",
        r"status",
        r"how am i doing",
    ],
    "finance": [
        r"money",
        r"financ",
        r"invest",
        r"stock",
        r"trading",
        r"budget",
        r"savings",
        r"vacation",
        r"paycheck",
    ],
    "health": [
        r"health",
        r"workout",
        r"exercise",
        r"muscle",
        r"fitness",
        r"sleep",
        r"diet",
        r"nutrition",
        r"meal",
    ],
    "career": [
        r"career",
        r"work",
        r"job",
        r"presentation",
        r"study",
        r"focus",
    ],
    "approve": [
        r"approve",
        r"yes.*do it",
        r"go ahead",
        r"accepted",
    ],
    "reject": [
        r"reject",
        r"no.*don",
        r"not now",
        r"declined",
    ],
}


def detect_intent(message: str) -> tuple[str, list[str]]:
    """Detect user intent from message.
    
    Returns:
        Tuple of (primary_intent, list of matched intents)
    """
    message_lower = message.lower()
    matched = []
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                matched.append(intent)
                break
    
    # Default to recommendation if no match
    primary = matched[0] if matched else "recommendation"
    return primary, matched


def extract_topic(message: str) -> str:
    """Extract specific topic from message."""
    message_lower = message.lower()
    
    topics = {
        "finance": ["money", "finance", "investment", "stock", "trading", "budget", "vacation", "paycheck"],
        "health": ["health", "workout", "exercise", "muscle", "fitness", "sleep", "diet", "nutrition", "meal"],
        "career": ["career", "work", "job", "presentation", "study", "focus"],
    }
    
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in message_lower:
                return topic
    
    return "general"


@router.post("/message", response_model=ChatResponse)
async def chat_message(message: ChatMessage) -> ChatResponse:
    """Handle chat message from LOIS.
    
    This is the main conversational endpoint that:
    1. Parses user intent
    2. Generates appropriate response
    3. Returns formatted chat response
    """
    user_message = message.message
    
    # Detect intent
    intent, matched_intents = detect_intent(user_message)
    topic = extract_topic(user_message)
    
    # Generate response based on intent
    try:
        if intent == "brief" or "brief" in matched_intents:
            return await handle_brief_request(user_message)
        
        elif intent == "recommendation" or "recommendation" in matched_intents:
            return await handle_recommendation_request(user_message, topic, matched_intents)
        
        elif intent == "approve" or intent == "reject":
            return handle_decision(user_message, intent)
        
        elif "finance" in matched_intents:
            return await handle_finance_request(user_message)
        
        elif "health" in matched_intents:
            return await handle_health_request(user_message)
        
        elif "career" in matched_intents:
            return await handle_career_request(user_message)
        
        else:
            return ChatResponse(
                response="I'm your Busy Bee Chief of Staff. I can help with:\n\n- **Recommendations** - 'What should I do about...'\n- **Executive Brief** - 'Show me my brief'\n- **Finance** - 'Can I afford vacation?'\n- **Health** - 'Create a workout plan'\n- **Career** - 'Help with presentation'\n\nWhat would you like help with?",
                type="question"
            )
    
    except Exception as e:
        return ChatResponse(
            response=f"I encountered an issue processing your request: {str(e)}",
            type="error"
        )


async def handle_brief_request(message: str) -> ChatResponse:
    """Handle request for executive brief."""
    # Generate brief
    from app.api.main import orchestrator
    
    brief = orchestrator.generate_executive_brief(
        period="Daily",
        title="Executive Brief"
    )
    
    # Format as chat
    formatted = lois_integration.format_executive_brief_chat(brief.to_dict())
    
    return ChatResponse(
        response=formatted,
        type="brief",
        data=brief.to_dict()
    )


async def handle_recommendation_request(message: str, topic: str, intents: list[str]) -> ChatResponse:
    """Handle recommendation request."""
    # Check for specific topics
    if "vacation" in message.lower():
        topic = "vacation"
    elif "paycheck" in message.lower():
        topic = "paycheck"
    elif "workout" in message.lower() or "exercise" in message.lower():
        topic = "workout"
    elif "presentation" in message.lower():
        topic = "presentation"
    elif "sleep" in message.lower():
        topic = "sleep"
    elif "muscle" in message.lower() or "shoulder" in message.lower():
        topic = "muscle"
    elif "trading" in message.lower() or "spy" in message.lower() or "options" in message.lower():
        topic = "trading"
    
    # Generate recommendation based on topic
    response_text = f"I need more information to give you a recommendation about {topic}. "
    response_text += "Could you provide more details about your situation?"
    
    return ChatResponse(
        response=response_text,
        type="question",
        data={"topic": topic, "intents": intents}
    )


async def handle_finance_request(message: str) -> ChatResponse:
    """Handle finance-related requests."""
    msg = message.lower()
    
    if "vacation" in msg or "afford" in msg:
        response = """I can't give a definitive answer without your financial details:

**Please provide:**
1. Monthly income: $______
2. Monthly expenses: $______
3. Current savings: $______
4. Vacation budget: $______

**Quick check:** Can you pay for vacation in cash without going into debt?"""
    
    elif "paycheck" in msg or "allocate" in msg:
        response = """Here's my standard paycheck allocation:

**Priority Order:**
1. **Essentials** (50-60%): Rent, utilities, groceries
2. **Emergency Fund** (10-20%): Until you have 3-6 months
3. **High-Interest Debt** (10-20%): Credit cards first
4. **Retirement** (10-15%): Get 401k match first
5. **Goals** (5-10%): Vacation, investments

Share your specific situation for personalized advice!"""
    
    elif "trading" in msg or "spy" in msg or "options" in msg:
        response = """For trading recommendations, I need:
1. Your risk tolerance
2. Position size limit
3. Time horizon

**Note:** I can provide general strategy based on market data, but always verify with your own analysis. Trading involves substantial risk."""
    
    else:
        response = """I can help with:
- Vacation affordability analysis
- Paycheck allocation strategy  
- Budget planning
- Investment basics

What specific financial question do you have?"""
    
    return ChatResponse(
        response=response,
        type="recommendation"
    )


async def handle_health_request(message: str) -> ChatResponse:
    """Handle health-related requests."""
    msg = message.lower()
    
    if "workout" in msg or "exercise" in msg or "muscle" in msg:
        response = """Here's a lean muscle + recovery plan:

**Weekly Schedule:**
- Mon: Upper Push (light) - incline press, lateral raises
- Tue: Lower + Core - squats, lunges, planks
- Wed: Rest / Mobility - shoulder circles, stretching
- Thu: Upper Pull - rows, pull-ups, rear delt flyes
- Fri: Lower + Core - deadlifts, leg press
- Sat: Full body light
- Sun: Rest

**Nutrition:** 180-200g protein, 2400-2600 cal daily

⚠️ Consult a physical therapist for shoulder-specific exercises."""
    
    elif "sleep" in msg:
        response = """Sleep optimization for peak performance:

**Tonight:**
- 9:30 PM: Start wind-down
- 10:00 PM: Lights out
- Sleep: 10 PM - 6 AM (8 hours)

**Routine:**
- 9:00 PM: Close laptop
- 9:15 PM: Light stretch/meditation
- 9:30 PM: Warm shower
- 9:45 PM: Read fiction
- 10:00 PM: Sleep

**Avoid:** Caffeine after 2 PM, screens before bed"""
    
    else:
        response = """I can help with:
- Workout plans (muscle building, recovery)
- Sleep optimization
- Nutrition plans
- Health recommendations

What do you need?"""
    
    return ChatResponse(
        response=response,
        type="recommendation"
    )


async def handle_career_request(message: str) -> ChatResponse:
    """Handle career-related requests."""
    msg = message.lower()
    
    if "presentation" in msg or "study" in msg or "focus" in msg:
        response = """**Presentation Prep Plan:**

**Focus Block:** 6:00 - 7:30 PM
- 6:00-6:20: Review materials
- 6:20-6:50: Deep work on weak areas
- 6:50-7:10: Full run-through
- 7:10-7:30: Final polish

**Environment:**
- Phone on airplane mode
- Close notifications
- Tell others not to disturb

**Tonight's Sleep:**
- 10 PM bedtime (critical for memory)
- 6:30 AM wake
- Avoid screens before bed

You've got this! 🎯"""
    
    else:
        response = """I can help with:
- Presentation preparation
- Focus time scheduling
- Career strategy

What do you need?"""
    
    return ChatResponse(
        response=response,
        type="recommendation"
    )


def handle_decision(message: str, decision: str) -> ChatResponse:
    """Handle approval/rejection decisions."""
    if decision == "approve":
        response = """✅ **APPROVED**

Your decision has been recorded. 

Would you like me to:
- Add this to your tracking?
- Set a reminder?
- Generate the next recommendation?"""
    else:
        response = """❌ **REJECTED**

Decision recorded. 

Would you like me to:
- Generate an alternative recommendation?
- Defer this for later?
- Get more information?"""
    
    return ChatResponse(
        response=response,
        type=decision,
        data={"decision": decision}
    )


@router.get("/health")
async def chat_health():
    """Health check for chat endpoint."""
    return {"status": "ok", "intents": list(INTENT_PATTERNS.keys())}
