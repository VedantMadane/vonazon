"""Data management module for JSON file operations."""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import threading

from utils import Ticket
import config


class DataManager:
    """Handles all data persistence operations using JSON files."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the data manager.
        
        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.tickets_file = self.data_dir / "tickets.json"
        self.review_queue_file = self.data_dir / "review_queue.json"
        self.statistics_file = self.data_dir / "statistics.json"
        self.config_file = self.data_dir / "config.json"
        
        # Thread lock for file operations
        self._lock = threading.Lock()
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Create empty data files if they don't exist."""
        if not self.tickets_file.exists():
            self._write_json(self.tickets_file, [])
        if not self.review_queue_file.exists():
            self._write_json(self.review_queue_file, [])
        if not self.statistics_file.exists():
            self._write_json(self.statistics_file, {
                "last_updated": datetime.now().isoformat(),
                "total_tickets": 0,
                "category_distribution": {},
                "average_confidence": 0.0
            })
        if not self.config_file.exists():
            self._write_json(self.config_file, {
                "openai_api_key": "",
                "model": config.DEFAULT_MODEL,
                "temperature": config.TEMPERATURE,
                "categories": config.CATEGORIES,
                "confidence_high": config.CONFIDENCE_HIGH,
                "confidence_medium": config.CONFIDENCE_MEDIUM,
                "confidence_low": config.CONFIDENCE_LOW,
                "crm_mode": config.CRM_MODE,
                "crm_real_endpoint": config.CRM_REAL_ENDPOINT,
                "output_format": config.OUTPUT_FORMAT
            })
    
    def _read_json(self, file_path: Path) -> any:
        """Read and parse JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        with self._lock:
            if not file_path.exists():
                return [] if file_path.name in ["tickets.json", "review_queue.json"] else {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _write_json(self, file_path: Path, data: any):
        """Write data to JSON file.
        
        Args:
            file_path: Path to JSON file
            data: Data to write
        """
        with self._lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_ticket(self, ticket: Ticket) -> bool:
        """Save a classified ticket to storage.
        
        Args:
            ticket: Ticket object to save
            
        Returns:
            True if successful
        """
        try:
            tickets = self._read_json(self.tickets_file)
            
            # Convert ticket to dict
            ticket_dict = {
                "id": ticket.id,
                "content": ticket.content,
                "category": ticket.category,
                "confidence": ticket.confidence,
                "reasoning": getattr(ticket, 'reasoning', ''),
                "alternative_category": getattr(ticket, 'alternative_category', None),
                "requires_review": getattr(ticket, 'requires_review', False),
                "timestamp": datetime.now().isoformat(),
                "crm_status": "success",  # Default status
                "crm_id": None,
                "reviewed_by": None,
                "review_notes": None
            }
            
            tickets.append(ticket_dict)
            self._write_json(self.tickets_file, tickets)
            
            # Add to review queue if needed
            if ticket_dict["requires_review"]:
                self.add_to_review_queue(ticket_dict)
            
            return True
        except Exception as e:
            print(f"Error saving ticket: {e}")
            return False
    
    def save_tickets_batch(self, tickets: List[Ticket], crm_results: List[Dict] = None) -> bool:
        """Save multiple tickets at once.
        
        Args:
            tickets: List of Ticket objects
            crm_results: Optional CRM push results
            
        Returns:
            True if successful
        """
        try:
            existing_tickets = self._read_json(self.tickets_file)
            
            for i, ticket in enumerate(tickets):
                crm_result = crm_results[i] if crm_results and i < len(crm_results) else {}
                
                ticket_dict = {
                    "id": ticket.id,
                    "content": ticket.content,
                    "category": ticket.category,
                    "confidence": ticket.confidence,
                    "reasoning": getattr(ticket, 'reasoning', ''),
                    "alternative_category": getattr(ticket, 'alternative_category', None),
                    "requires_review": getattr(ticket, 'requires_review', False),
                    "timestamp": datetime.now().isoformat(),
                    "crm_status": crm_result.get("status", "pending").lower(),
                    "crm_id": crm_result.get("crm_id"),
                    "reviewed_by": None,
                    "review_notes": None
                }
                
                existing_tickets.append(ticket_dict)
                
                # Add to review queue if needed
                if ticket_dict["requires_review"]:
                    self.add_to_review_queue(ticket_dict)
            
            self._write_json(self.tickets_file, existing_tickets)
            
            # Regenerate statistics
            self.regenerate_statistics()
            
            return True
        except Exception as e:
            print(f"Error saving tickets batch: {e}")
            return False
    
    def get_tickets(self, limit: int = 50, offset: int = 0, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve tickets with pagination and filtering.
        
        Args:
            limit: Maximum number of tickets to return
            offset: Number of tickets to skip
            filter_dict: Optional filters (category, date range, etc.)
            
        Returns:
            List of ticket dictionaries
        """
        tickets = self._read_json(self.tickets_file)
        
        # Apply filters
        if filter_dict:
            if "category" in filter_dict:
                tickets = [t for t in tickets if t["category"] == filter_dict["category"]]
            if "requires_review" in filter_dict:
                tickets = [t for t in tickets if t["requires_review"] == filter_dict["requires_review"]]
        
        # Sort by timestamp (most recent first)
        tickets.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        return tickets[offset:offset + limit]
    
    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict]:
        """Get a single ticket by ID.
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Ticket dictionary or None
        """
        tickets = self._read_json(self.tickets_file)
        for ticket in tickets:
            if ticket["id"] == ticket_id:
                return ticket
        return None
    
    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """Update a ticket's fields.
        
        Args:
            ticket_id: Ticket ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            tickets = self._read_json(self.tickets_file)
            
            for ticket in tickets:
                if ticket["id"] == ticket_id:
                    ticket.update(updates)
                    self._write_json(self.tickets_file, tickets)
                    
                    # If no longer requires review, remove from queue
                    if not ticket.get("requires_review", True):
                        self.remove_from_review_queue(ticket_id)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Error updating ticket: {e}")
            return False
    
    def add_to_review_queue(self, ticket_dict: Dict):
        """Add a ticket to the review queue.
        
        Args:
            ticket_dict: Ticket dictionary
        """
        try:
            queue = self._read_json(self.review_queue_file)
            
            # Check if already in queue
            if not any(t["id"] == ticket_dict["id"] for t in queue):
                queue.append(ticket_dict)
                self._write_json(self.review_queue_file, queue)
        except Exception as e:
            print(f"Error adding to review queue: {e}")
    
    def remove_from_review_queue(self, ticket_id: str):
        """Remove a ticket from the review queue.
        
        Args:
            ticket_id: Ticket ID
        """
        try:
            queue = self._read_json(self.review_queue_file)
            queue = [t for t in queue if t["id"] != ticket_id]
            self._write_json(self.review_queue_file, queue)
        except Exception as e:
            print(f"Error removing from review queue: {e}")
    
    def get_review_queue(self, confidence_filter: str = None) -> List[Dict]:
        """Get tickets in review queue.
        
        Args:
            confidence_filter: Filter by confidence level (low, medium, high)
            
        Returns:
            List of tickets needing review
        """
        queue = self._read_json(self.review_queue_file)
        
        if confidence_filter:
            if confidence_filter == "low":
                queue = [t for t in queue if t.get("confidence", 0) < config.CONFIDENCE_LOW]
            elif confidence_filter == "medium":
                queue = [t for t in queue if config.CONFIDENCE_LOW <= t.get("confidence", 0) < config.CONFIDENCE_MEDIUM]
            elif confidence_filter == "high":
                queue = [t for t in queue if t.get("confidence", 0) >= config.CONFIDENCE_MEDIUM]
        
        return queue
    
    def get_statistics(self, period: str = "all") -> Dict:
        """Get classification statistics.
        
        Args:
            period: Time period (today, week, month, all)
            
        Returns:
            Statistics dictionary
        """
        tickets = self._read_json(self.tickets_file)
        
        # Filter by period
        if period != "all":
            now = datetime.now()
            if period == "today":
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                cutoff = now - timedelta(days=7)
            elif period == "month":
                cutoff = now - timedelta(days=30)
            else:
                cutoff = datetime.min
            
            tickets = [t for t in tickets if datetime.fromisoformat(t.get("timestamp", "2000-01-01")) >= cutoff]
        
        # Calculate statistics
        total_tickets = len(tickets)
        
        if total_tickets == 0:
            return {
                "total_tickets": 0,
                "period": period,
                "category_distribution": {},
                "average_confidence": 0.0,
                "review_rate": 0.0,
                "crm_success_rate": 0.0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0
            }
        
        # Category distribution
        category_dist = {}
        for ticket in tickets:
            cat = ticket.get("category", "Other")
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Confidence metrics
        confidences = [t.get("confidence", 0) for t in tickets if t.get("confidence") is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        high_conf = len([c for c in confidences if c >= config.CONFIDENCE_HIGH])
        medium_conf = len([c for c in confidences if config.CONFIDENCE_MEDIUM <= c < config.CONFIDENCE_HIGH])
        low_conf = len([c for c in confidences if c < config.CONFIDENCE_MEDIUM])
        
        # Review rate
        needs_review = len([t for t in tickets if t.get("requires_review", False)])
        review_rate = (needs_review / total_tickets * 100) if total_tickets > 0 else 0.0
        
        # CRM success rate
        crm_success = len([t for t in tickets if t.get("crm_status") == "success"])
        crm_success_rate = (crm_success / total_tickets * 100) if total_tickets > 0 else 0.0
        
        return {
            "total_tickets": total_tickets,
            "period": period,
            "category_distribution": category_dist,
            "average_confidence": round(avg_confidence, 3),
            "review_rate": round(review_rate, 1),
            "crm_success_rate": round(crm_success_rate, 1),
            "high_confidence_count": high_conf,
            "medium_confidence_count": medium_conf,
            "low_confidence_count": low_conf
        }
    
    def regenerate_statistics(self):
        """Regenerate and cache statistics."""
        stats = self.get_statistics("all")
        stats["last_updated"] = datetime.now().isoformat()
        self._write_json(self.statistics_file, stats)
    
    def get_user_config(self) -> Dict:
        """Get user configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._read_json(self.config_file)
    
    def update_user_config(self, updates: Dict) -> bool:
        """Update user configuration.
        
        Args:
            updates: Configuration updates
            
        Returns:
            True if successful
        """
        try:
            current_config = self._read_json(self.config_file)
            current_config.update(updates)
            self._write_json(self.config_file, current_config)
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def export_data(self, format: str = "json", filters: Dict = None) -> str:
        """Export ticket data.
        
        Args:
            format: Export format (json or csv)
            filters: Optional filters
            
        Returns:
            Exported data as string
        """
        tickets = self.get_tickets(limit=10000, filter_dict=filters)
        
        if format == "json":
            return json.dumps(tickets, indent=2)
        elif format == "csv":
            if not tickets:
                return ""
            
            # CSV format
            headers = ["ID", "Content", "Category", "Confidence", "Timestamp", "CRM Status"]
            lines = [",".join(headers)]
            
            for ticket in tickets:
                row = [
                    ticket.get("id", ""),
                    f'"{ticket.get("content", "").replace(chr(34), chr(34)+chr(34))}"',  # Escape quotes
                    ticket.get("category", ""),
                    str(ticket.get("confidence", "")),
                    ticket.get("timestamp", ""),
                    ticket.get("crm_status", "")
                ]
                lines.append(",".join(row))
            
            return "\n".join(lines)
        
        return ""
