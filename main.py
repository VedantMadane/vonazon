"""Main entry point for the ticket classification system."""

from typing import List
import sys

from ticket_classifier import OpenAIClassifier, MockClassifier
from crm_integration import CRMIntegration
from utils import create_tickets_from_texts, print_results
import config


def main(ticket_texts: List[str], use_real_api: bool = True, export_results: bool = False):
    """Main workflow orchestration for ticket classification.
    
    Args:
        ticket_texts: List of ticket content strings
        use_real_api: Whether to use real OpenAI API (True) or mock classifier (False)
        export_results: Whether to export results to JSON file
    """
    print("\n🎫 Starting Ticket Classification System...")
    print(f"Mode: {'OpenAI API' if use_real_api else 'Mock Classifier'}")
    print(f"Tickets to process: {len(ticket_texts)}\n")
    
    # Step 1: Create ticket objects
    tickets = create_tickets_from_texts(ticket_texts)
    print(f"✓ Created {len(tickets)} ticket objects")
    
    # Step 2: Classify tickets
    try:
        if use_real_api:
            classifier = OpenAIClassifier()
            print("✓ Initialized OpenAI classifier")
        else:
            classifier = MockClassifier()
            print("✓ Initialized Mock classifier")
        
        print("⏳ Classifying tickets...")
        classified_tickets = classifier.classify(tickets)
        print(f"✓ Classified {len(classified_tickets)} tickets")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTo use OpenAI API, set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'  # Linux/Mac")
        print("  $env:OPENAI_API_KEY='your-key-here'   # Windows PowerShell")
        print("\nOr run with mock mode: python main.py --mock")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Classification Error: {e}")
        sys.exit(1)
    
    # Step 3: Push to CRM
    print("⏳ Pushing to CRM...")
    crm = CRMIntegration()
    crm_results = crm.push_batch(classified_tickets)
    print(f"✓ Pushed {len(crm_results)} tickets to CRM")
    
    # Step 4: Display results
    print_results(classified_tickets, crm_results)
    
    # Step 5: Export if requested
    if export_results:
        crm.export_results()
    
    # Step 6: Show statistics
    stats = crm.get_statistics()
    print(f"📊 Success Rate: {stats['success_rate']:.1f}%")
    
    return classified_tickets, crm_results


# Sample ticket data for testing
SAMPLE_TICKETS = [
    "I was charged twice for my subscription this month. Can I get a refund?",
    "The application crashes every time I try to upload a file larger than 10MB.",
    "I'm interested in upgrading to the Enterprise plan. What features are included?",
    "My dashboard is showing incorrect data and I can't export reports.",
    "Can you provide a demo of your product for our team?",
    "I haven't received my invoice for last month's payment.",
    "The API is returning 500 errors when I make POST requests.",
    "What's the difference between your Professional and Business plans?",
    "I need help resetting my password, the email link isn't working.",
    "When will the new features announced last quarter be available?"
]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Customer Support Ticket Classification System")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock classifier instead of OpenAI API"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to JSON file"
    )
    parser.add_argument(
        "--tickets",
        nargs="+",
        help="Custom ticket texts to classify"
    )
    
    args = parser.parse_args()
    
    # Use custom tickets if provided, otherwise use samples
    tickets_to_process = args.tickets if args.tickets else SAMPLE_TICKETS
    
    # Run the main workflow
    main(
        ticket_texts=tickets_to_process,
        use_real_api=not args.mock,
        export_results=args.export
    )
"""Main entry point for the ticket classification system."""

from typing import List
import sys

from ticket_classifier import OpenAIClassifier, MockClassifier
from crm_integration import CRMIntegration
from utils import create_tickets_from_texts, print_results
import config


def main(ticket_texts: List[str], use_real_api: bool = True, export_results: bool = False):
    """Main workflow orchestration for ticket classification.
    
    Args:
        ticket_texts: List of ticket content strings
        use_real_api: Whether to use real OpenAI API (True) or mock classifier (False)
        export_results: Whether to export results to JSON file
    """
    print("\n🎫 Starting Ticket Classification System...")
    print(f"Mode: {'OpenAI API' if use_real_api else 'Mock Classifier'}")
    print(f"Tickets to process: {len(ticket_texts)}\n")
    
    # Step 1: Create ticket objects
    tickets = create_tickets_from_texts(ticket_texts)
    print(f"✓ Created {len(tickets)} ticket objects")
    
    # Step 2: Classify tickets
    try:
        if use_real_api:
            classifier = OpenAIClassifier()
            print("✓ Initialized OpenAI classifier")
        else:
            classifier = MockClassifier()
            print("✓ Initialized Mock classifier")
        
        print("⏳ Classifying tickets...")
        classified_tickets = classifier.classify(tickets)
        print(f"✓ Classified {len(classified_tickets)} tickets")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTo use OpenAI API, set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'  # Linux/Mac")
        print("  $env:OPENAI_API_KEY='your-key-here'   # Windows PowerShell")
        print("\nOr run with mock mode: python main.py --mock")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Classification Error: {e}")
        sys.exit(1)
    
    # Step 3: Push to CRM
    print("⏳ Pushing to CRM...")
    crm = CRMIntegration()
    crm_results = crm.push_batch(classified_tickets)
    print(f"✓ Pushed {len(crm_results)} tickets to CRM")
    
    # Step 4: Display results
    print_results(classified_tickets, crm_results)
    
    # Step 5: Export if requested
    if export_results:
        crm.export_results()
    
    # Step 6: Show statistics
    stats = crm.get_statistics()
    print(f"📊 Success Rate: {stats['success_rate']:.1f}%")
    
    return classified_tickets, crm_results


# Sample ticket data for testing
SAMPLE_TICKETS = [
    "I was charged twice for my subscription this month. Can I get a refund?",
    "The application crashes every time I try to upload a file larger than 10MB.",
    "I'm interested in upgrading to the Enterprise plan. What features are included?",
    "My dashboard is showing incorrect data and I can't export reports.",
    "Can you provide a demo of your product for our team?",
    "I haven't received my invoice for last month's payment.",
    "The API is returning 500 errors when I make POST requests.",
    "What's the difference between your Professional and Business plans?",
    "I need help resetting my password, the email link isn't working.",
    "When will the new features announced last quarter be available?"
]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Customer Support Ticket Classification System")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock classifier instead of OpenAI API"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to JSON file"
    )
    parser.add_argument(
        "--tickets",
        nargs="+",
        help="Custom ticket texts to classify"
    )
    
    args = parser.parse_args()
    
    # Use custom tickets if provided, otherwise use samples
    tickets_to_process = args.tickets if args.tickets else SAMPLE_TICKETS
    
    # Run the main workflow
    main(
        ticket_texts=tickets_to_process,
        use_real_api=not args.mock,
        export_results=args.export
    )
