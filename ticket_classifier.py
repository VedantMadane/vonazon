"""Ticket classification logic using AI APIs."""

from abc import ABC, abstractmethod
from typing import List
import random

from utils import Ticket
import config


class TicketClassifier(ABC):
    """Abstract base class for ticket classifiers."""
    
    @abstractmethod
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Classify a list of tickets into predefined categories."""
        pass


class OpenAIClassifier(TicketClassifier):
    """Ticket classifier using OpenAI's API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize the OpenAI classifier.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Model to use (defaults to config)
        """
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model or config.DEFAULT_MODEL
        self.categories = config.CATEGORIES
    
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Classify tickets using OpenAI API.
        
        Args:
            tickets: List of Ticket objects to classify
            
        Returns:
            List of classified Ticket objects
        """
        results = []
        
        for ticket in tickets:
            try:
                category, confidence = self._classify_single_ticket(ticket)
                ticket.category = category
                ticket.confidence = confidence
                results.append(ticket)
                
            except Exception as e:
                print(f"Error classifying ticket {ticket.id}: {str(e)}")
                ticket.category = "Other"
                ticket.confidence = 0.0
                results.append(ticket)
        
        return results
    
    def _classify_single_ticket(self, ticket: Ticket) -> tuple[str, float]:
        """Classify a single ticket using the API.
        
        Args:
            ticket: Ticket to classify
            
        Returns:
            Tuple of (category, confidence)
        """
        prompt = f"""Classify this customer support ticket into ONE of these categories: {', '.join(self.categories)}

Ticket: "{ticket.content}"

Respond with ONLY the category name. Choose the most appropriate category based on the ticket content."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
            max_tokens=50
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validate category
        if category not in self.categories:
            # Try to match partial category name
            category_lower = category.lower()
            for valid_category in self.categories:
                if valid_category.lower() in category_lower or category_lower in valid_category.lower():
                    category = valid_category
                    break
            else:
                category = "Other"
        
        # Estimate confidence (OpenAI doesn't provide this directly)
        confidence = 0.95 if category != "Other" else 0.7
        
        return category, confidence


class MockClassifier(TicketClassifier):
    """Mock classifier for testing without API calls."""
    
    def __init__(self):
        """Initialize the mock classifier."""
        self.categories = config.CATEGORIES
    
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Mock classification using keyword matching.
        
        Args:
            tickets: List of Ticket objects to classify
            
        Returns:
            List of classified Ticket objects
        """
        results = []
        
        for ticket in tickets:
            category = self._mock_classify(ticket.content)
            ticket.category = category
            ticket.confidence = random.uniform(0.75, 0.95)
            results.append(ticket)
        
        return results
    
    def _mock_classify(self, content: str) -> str:
        """Simple keyword-based classification for testing."""
        content_lower = content.lower()
        
        # Billing keywords
        if any(word in content_lower for word in ['bill', 'charge', 'payment', 'invoice', 'refund', 'pricing', 'cost']):
            return "Billing"
        
        # Technical keywords
        if any(word in content_lower for word in ['error', 'bug', 'crash', 'not working', 'broken', 'issue', 'problem', 'technical']):
            return "Technical Issue"
        
        # Sales keywords
        if any(word in content_lower for word in ['buy', 'purchase', 'product', 'demo', 'sales', 'pricing plan', 'features']):
            return "Sales Inquiry"
        
        return "Other"
