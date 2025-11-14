"""Utility functions for the ticket classification system."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Ticket:
    """Represents a customer support ticket."""
    id: str
    content: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    requires_review: bool = False
    reasoning: Optional[str] = None
    alternative_category: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Ticket(id={self.id}, category={self.category}, confidence={self.confidence})"


def create_tickets_from_texts(texts: List[str]) -> List[Ticket]:
    """Create Ticket objects from a list of text strings."""
    return [
        Ticket(id=f"TKT-{i+1:04d}", content=text)
        for i, text in enumerate(texts)
    ]


def print_results(tickets: List[Ticket], crm_results: List[dict], output_format: str = "detailed") -> None:
    """Print formatted classification results.
    
    Args:
        tickets: List of classified tickets
        crm_results: List of CRM push results
        output_format: 'simple' or 'detailed'
    """
    if output_format == "simple":
        print_simple_results(tickets, crm_results)
    else:
        print_detailed_results(tickets, crm_results)


def print_simple_results(tickets: List[Ticket], crm_results: List[dict]) -> None:
    """Print results in simple format matching Problem Statement example."""
    for ticket, crm_result in zip(tickets, crm_results):
        print(f'Ticket: "{ticket.content}"')
        print(f"Category: {ticket.category}")
        status = "Success" if crm_result.get('status') == 'Success' else "Failed"
        print(f"Pushed to CRM endpoint: {status}")
        print()  # Empty line between tickets


def print_detailed_results(tickets: List[Ticket], crm_results: List[dict]) -> None:
    """Print results in detailed format with full information."""
    print("\n" + "="*70)
    print("TICKET CLASSIFICATION RESULTS".center(70))
    print("="*70)
    
    for ticket, crm_result in zip(tickets, crm_results):
        print(f"\nTicket ID: {ticket.id}")
        print(f"Content: {ticket.content[:60]}{'...' if len(ticket.content) > 60 else ''}")
        print(f"Category: {ticket.category}")
        print(f"Confidence: {ticket.confidence:.2%}" if ticket.confidence else "Confidence: N/A")
        
        # Show ambiguity information
        if ticket.requires_review:
            print(f"⚠️  Requires Human Review: Yes")
        if ticket.alternative_category:
            print(f"Alternative Category: {ticket.alternative_category}")
        if ticket.reasoning:
            print(f"Reasoning: {ticket.reasoning}")
        
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
