"""Utility functions for the ticket classification system."""

from typing import List
from dataclasses import dataclass


@dataclass
class Ticket:
    """Represents a customer support ticket."""
    id: str
    content: str
    category: str = None
    confidence: float = None
    
    def __repr__(self) -> str:
        return f"Ticket(id={self.id}, category={self.category}, confidence={self.confidence})"


def create_tickets_from_texts(texts: List[str]) -> List[Ticket]:
    """Create Ticket objects from a list of text strings."""
    return [
        Ticket(id=f"TKT-{i+1:04d}", content=text)
        for i, text in enumerate(texts)
    ]


def print_results(tickets: List[Ticket], crm_results: List[dict]) -> None:
    """Print formatted classification results."""
    print("\n" + "="*70)
    print("TICKET CLASSIFICATION RESULTS".center(70))
    print("="*70)
    
    for ticket, crm_result in zip(tickets, crm_results):
        print(f"\nTicket ID: {ticket.id}")
        print(f"Content: {ticket.content[:60]}{'...' if len(ticket.content) > 60 else ''}")
        print(f"Category: {ticket.category}")
        print(f"Confidence: {ticket.confidence:.2%}" if ticket.confidence else "Confidence: N/A")
        print(f"CRM Status: {crm_result.get('status', 'Unknown')}")
        print(f"CRM ID: {crm_result.get('crm_id', 'N/A')}")
    
    print("\n" + "="*70)
    print(f"Total Processed: {len(tickets)}")
    
    # Category distribution
    category_counts = {}
    for ticket in tickets:
        category_counts[ticket.category] = category_counts.get(ticket.category, 0) + 1
    
    print("\nCategory Distribution:")
    for category, count in sorted(category_counts.items()):
        percentage = (count / len(tickets)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")
    
    print("="*70 + "\n")
