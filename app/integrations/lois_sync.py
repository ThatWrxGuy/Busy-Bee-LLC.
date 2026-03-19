# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""LOIS Sync Service - Real-time sync between Busy Bee and LOIS."""

import asyncio
import aiohttp
from typing import Optional, Callable
from datetime import datetime
import json

from app.product import ProductRecommendation
from app.integrations.lois_integration import busybee_to_lois_recommendation


class LOISSyncService:
    """Real-time sync service for LOIS integration.
    
    Handles:
    1. Pushing recommendations to LOIS
    2. Pulling updates from LOIS
    3. Bidirectional sync of recommendations
    """
    
    def __init__(
        self,
        lois_base_url: str = "https://lois-life-operating-intelligence-s-c8a842a9.base44.app",
        api_key: Optional[str] = None
    ):
        self.lois_base_url = lois_base_url
        self.api_key = api_key
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    async def push_recommendation(self, recommendation: ProductRecommendation) -> bool:
        """Push a recommendation to LOIS.
        
        Args:
            recommendation: ProductRecommendation to push
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Lois_data = busybee_to_lois_recommendation(recommendation)
            
            # Note: This would need actual LOIS API endpoint
            # For now, we'll log what would be pushed
            print(f"[LOIS SYNC] Would push recommendation: {lois_data['id']}")
            print(f"  Title: {lois_data['title']}")
            print(f"  Hive: {lois_data['hive']}")
            print(f"  Urgency: {lois_data['urgency']}")
            
            # In production, this would be:
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(
            #         f"{self.lois_base_url}/api/recommendations",
            #         json=lois_data,
            #         headers={"Authorization": f"Bearer {self.api_key}"}
            #     ) as resp:
            #         return resp.status == 200
            
            return True
            
        except Exception as e:
            print(f"[LOIS SYNC ERROR] {e}")
            return False
    
    async def push_executive_brief(self, brief_dict: dict) -> bool:
        """Push executive brief summary to LOIS.
        
        Args:
            brief_dict: Executive brief dictionary
            
        Returns:
            True if successful
        """
        try:
            # Extract key metrics for LOIS dashboard
            sv = brief_dict.get("system_view", {})
            
            # Map domain scores to LOIS format
            domain_scores = sv.get("domain_scores", {})
            
            print(f"[LOIS SYNC] Would push brief:")
            print(f"  System Status: {sv.get('system_status')}")
            print(f"  Strategic Posture: {sv.get('strategic_posture')}")
            print(f"  Confidence: {sv.get('confidence_score')}")
            print(f"  Domain Scores: {domain_scores}")
            print(f"  Recommendations: {len(sv.get('recommendations', []))}")
            
            return True
            
        except Exception as e:
            print(f"[LOIS SYNC ERROR] {e}")
            return False
    
    async def sync_approved_recommendations(
        self, 
        recommendations: list[ProductRecommendation]
    ) -> dict:
        """Sync all approved recommendations to LOIS.
        
        Args:
            recommendations: List of approved recommendations
            
        Returns:
            Sync status summary
        """
        results = {
            "total": len(recommendations),
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        
        for rec in recommendations:
            if rec.status in ("approved", "presented"):
                success = await self.push_recommendation(rec)
                if success:
                    results["succeeded"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to sync: {rec.id}")
        
        return results
    
    async def start_background_sync(
        self, 
        interval_seconds: int = 60,
        callback: Optional[Callable] = None
    ):
        """Start background sync loop.
        
        Args:
            interval_seconds: How often to sync
            callback: Optional callback function
        """
        self._running = True
        print(f"[LOIS SYNC] Starting background sync every {interval_seconds}s")
        
        while self._running:
            try:
                if callback:
                    await callback()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[LOIS SYNC ERROR] {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    def stop_background_sync(self):
        """Stop background sync."""
        self._running = False
        print("[LOIS SYNC] Stopped background sync")


class LOISWebhookHandler:
    """Webhook handler for receiving updates from LOIS."""
    
    def __init__(self, sync_service: LOISSyncService):
        self.sync_service = sync_service
    
    async def handle_recommendation_approved(self, data: dict) -> dict:
        """Handle recommendation approved webhook from LOIS.
        
        Args:
            data: Webhook payload from LOIS
            
        Returns:
            Acknowledgment response
        """
        rec_id = data.get("id")
        print(f"[LOIS WEBHOOK] Recommendation approved: {rec_id}")
        
        # Could update local database, trigger actions, etc.
        
        return {"status": "acknowledged", "id": rec_id}
    
    async def handle_recommendation_rejected(self, data: dict) -> dict:
        """Handle recommendation rejected webhook from LOIS."""
        rec_id = data.get("id")
        print(f"[LOIS WEBHOOK] Recommendation rejected: {rec_id}")
        
        return {"status": "acknowledged", "id": rec_id}
    
    async def handle_domain_score_update(self, data: dict) -> dict:
        """Handle domain score update from LOIS."""
        domain = data.get("domain")
        score = data.get("score")
        print(f"[LOIS WEBHOOK] Domain score updated: {domain} = {score}")
        
        return {"status": "acknowledged", "domain": domain}


# Singleton instances
lois_sync_service = LOISSyncService()


__all__ = [
    "LOISSyncService", 
    "LOISWebhookHandler",
    "lois_sync_service",
]
