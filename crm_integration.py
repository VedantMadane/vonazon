"""CRM integration module for pushing classified tickets."""

from typing import Dict, List, Optional
import json
import time
import random
from datetime import datetime

from utils import Ticket
import config


class CRMIntegration:
    """Handles integration with CRM system with multiple simulation modes."""
    
    def __init__(self, endpoint: Optional[str] = None, mode: Optional[str] = None):
        """Initialize CRM integration.
        
        Args:
            endpoint: CRM endpoint URL (defaults to config)
            mode: Simulation mode - 'mock', 'mock-http', or 'real' (defaults to config)
        """
        self.endpoint = endpoint or config.MOCK_CRM_ENDPOINT
        self.mode = mode or config.CRM_MODE
        self.results = []
        self.simulate_delay = config.CRM_SIMULATE_DELAY
        self.failure_rate = config.CRM_FAILURE_RATE
    
    def push_ticket(self, ticket: Ticket) -> Dict:
        """Push a single classified ticket to the CRM.
        
        Args:
            ticket: Classified Ticket object
            
        Returns:
            Dictionary with push result status
        """
        if not ticket.category:
            return {
                "status": "Error",
                "message": "Ticket not classified",
                "ticket_id": ticket.id
            }
        
        payload = {
            "ticket_id": ticket.id,
            "content": ticket.content,
            "category": ticket.category,
            "confidence": ticket.confidence,
            "timestamp": datetime.now().isoformat(),
            "endpoint": self.endpoint
        }
        
        # Add additional fields for enhanced ambiguity handling
        if ticket.requires_review:
            payload["requires_review"] = True
        if ticket.alternative_category:
            payload["alternative_category"] = ticket.alternative_category
        if ticket.reasoning:
            payload["reasoning"] = ticket.reasoning
        
        # Execute based on mode
        if self.mode == "mock-http":
            return self._mock_http_push(ticket, payload)
        elif self.mode == "real":
            return self._real_http_push(ticket, payload)
        else:  # mock mode
            return self._mock_push(ticket, payload)
    
    def _mock_push(self, ticket: Ticket, payload: Dict) -> Dict:
        """Simple mock push without HTTP simulation."""
        self.results.append(payload)
        
        return {
            "status": "Success",
            "crm_id": f"CRM-{ticket.id}",
            "endpoint": self.endpoint,
            "ticket_id": ticket.id
        }
    
    def _mock_http_push(self, ticket: Ticket, payload: Dict) -> Dict:
        """Mock HTTP push with realistic delays and error simulation."""
        # Simulate network delay
        if self.simulate_delay > 0:
            time.sleep(self.simulate_delay)
        
        # Simulate random failures
        if random.random() < self.failure_rate:
            error_scenarios = [
                {"status": "Failed", "message": "HTTP 500: Internal Server Error", "http_code": 500},
                {"status": "Failed", "message": "HTTP 503: Service Unavailable", "http_code": 503},
                {"status": "Failed", "message": "HTTP 429: Rate Limit Exceeded", "http_code": 429},
                {"status": "Failed", "message": "Timeout: Request timed out", "http_code": 408},
            ]
            error = random.choice(error_scenarios)
            return {
                "status": error["status"],
                "message": error["message"],
                "http_code": error["http_code"],
                "ticket_id": ticket.id,
                "endpoint": self.endpoint
            }
        
        # Successful mock HTTP request
        self.results.append(payload)
        
        return {
            "status": "Success",
            "crm_id": f"CRM-{ticket.id}",
            "endpoint": self.endpoint,
            "ticket_id": ticket.id,
            "http_code": 201,
            "message": "Created"
        }
    
    def _real_http_push(self, ticket: Ticket, payload: Dict) -> Dict:
        """Real HTTP POST to actual CRM endpoint."""
        try:
            import requests
            
            if not config.CRM_REAL_ENDPOINT:
                raise ValueError("CRM_REAL_ENDPOINT not configured")
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Vonazon-TicketClassifier/1.0"
            }
            
            response = requests.post(
                config.CRM_REAL_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            self.results.append(payload)
            
            return {
                "status": "Success",
                "crm_id": response.json().get("id", f"CRM-{ticket.id}"),
                "endpoint": config.CRM_REAL_ENDPOINT,
                "ticket_id": ticket.id,
                "http_code": response.status_code
            }
            
        except ImportError:
            raise ImportError("requests library required for real HTTP mode. Run: pip install requests")
        except Exception as e:
            return {
                "status": "Failed",
                "message": str(e),
                "ticket_id": ticket.id,
                "endpoint": config.CRM_REAL_ENDPOINT
            }
    
    def push_batch(self, tickets: List[Ticket]) -> List[Dict]:
        """Push multiple tickets to the CRM in batch.
        
        Args:
            tickets: List of classified Ticket objects
            
        Returns:
            List of push result dictionaries
        """
        return [self.push_ticket(ticket) for ticket in tickets]
    
    def get_results(self) -> str:
        """Get all pushed results as formatted JSON.
        
        Returns:
            JSON string of all results
        """
        return json.dumps(self.results, indent=2)
    
    def export_results(self, filepath: str = "crm_results.json") -> None:
        """Export results to a JSON file.
        
        Args:
            filepath: Path to output file
        """
        with open(filepath, 'w') as f:
            f.write(self.get_results())
        print(f"Results exported to {filepath}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about pushed tickets.
        
        Returns:
            Dictionary with statistics
        """
        if not self.results:
            return {"total": 0, "by_category": {}, "success_rate": 0.0}
        
        category_counts = {}
        for result in self.results:
            category = result.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total": len(self.results),
            "by_category": category_counts,
            "success_rate": sum(1 for r in self.results if r) / len(self.results) * 100
        }
