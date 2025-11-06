"""CRM integration module for pushing classified tickets."""

from typing import Dict, List
import json
from datetime import datetime

from utils import Ticket
import config


class CRMIntegration:
    """Handles integration with CRM system (mock implementation)."""
    
    def __init__(self, endpoint: str = None):
        """Initialize CRM integration.
        
        Args:
            endpoint: CRM endpoint URL (defaults to config)
        """
        self.endpoint = endpoint or config.MOCK_CRM_ENDPOINT
        self.results = []
    
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
        
        # Mock CRM call - in production, this would be an HTTP request
        self.results.append(payload)
        
        return {
            "status": "Success",
            "crm_id": f"CRM-{ticket.id}",
            "endpoint": self.endpoint,
            "ticket_id": ticket.id
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
            return {"total": 0, "by_category": {}}
        
        category_counts = {}
        for result in self.results:
            category = result.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total": len(self.results),
            "by_category": category_counts,
            "success_rate": sum(1 for r in self.results if r) / len(self.results) * 100
        }
"""CRM integration module for pushing classified tickets."""

from typing import Dict, List
import json
from datetime import datetime

from utils import Ticket
import config


class CRMIntegration:
    """Handles integration with CRM system (mock implementation)."""
    
    def __init__(self, endpoint: str = None):
        """Initialize CRM integration.
        
        Args:
            endpoint: CRM endpoint URL (defaults to config)
        """
        self.endpoint = endpoint or config.MOCK_CRM_ENDPOINT
        self.results = []
    
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
        
        # Mock CRM call - in production, this would be an HTTP request
        self.results.append(payload)
        
        return {
            "status": "Success",
            "crm_id": f"CRM-{ticket.id}",
            "endpoint": self.endpoint,
            "ticket_id": ticket.id
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
            return {"total": 0, "by_category": {}}
        
        category_counts = {}
        for result in self.results:
            category = result.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total": len(self.results),
            "by_category": category_counts,
            "success_rate": sum(1 for r in self.results if r) / len(self.results) * 100
        }
