"""Ticket classification logic using AI APIs."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import random
import json

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
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
        """Classify tickets using OpenAI API with enhanced ambiguity handling.
        
        Args:
            tickets: List of Ticket objects to classify
            
        Returns:
            List of classified Ticket objects with confidence scores and reasoning
        """
        results = []
        
        for ticket in tickets:
            try:
                self._classify_single_ticket_enhanced(ticket)
                self._apply_confidence_thresholds(ticket)
                results.append(ticket)
                
            except Exception as e:
                print(f"Error classifying ticket {ticket.id}: {str(e)}")
                ticket.category = "Other"
                ticket.confidence = 0.0
                ticket.requires_review = True
                ticket.reasoning = f"Classification failed: {str(e)}"
                results.append(ticket)
        
        return results
    
    def _classify_single_ticket_enhanced(self, ticket: Ticket) -> None:
        """Classify a single ticket using enhanced OpenAI API with structured output.
        
        Args:
            ticket: Ticket to classify (modified in place)
        """
        # Enhanced prompt requesting structured information
        prompt = f"""Analyze this customer support ticket and provide a classification.

Ticket: "{ticket.content}"

Categories: {', '.join(self.categories)}

Provide your response in JSON format with these fields:
- category: The most appropriate category from the list above
- confidence: Your confidence level (0.0 to 1.0) in this classification
- reasoning: Brief explanation (1-2 sentences) for why you chose this category
- alternative_category: If confidence is below 0.85, suggest an alternative category (or null)

Example response:
{{
  "category": "Billing",
  "confidence": 0.92,
  "reasoning": "The ticket mentions charges and refunds, clearly indicating a billing issue.",
  "alternative_category": null
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.TEMPERATURE,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
            result = json.loads(content)
            
            # Extract and validate category
            category = result.get("category", "Other")
            if category not in self.categories:
                # Try to match partial category name
                category_lower = category.lower()
                for valid_category in self.categories:
                    if valid_category.lower() in category_lower or category_lower in valid_category.lower():
                        category = valid_category
                        break
                else:
                    category = "Other"
            
            # Extract confidence and reasoning
            confidence = float(result.get("confidence", 0.7))
            reasoning = result.get("reasoning", "")
            alternative = result.get("alternative_category")
            
            # Update ticket
            ticket.category = category
            ticket.confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            ticket.reasoning = reasoning
            if alternative and alternative in self.categories:
                ticket.alternative_category = alternative
                
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to simple classification if JSON parsing fails
            print(f"Warning: JSON parsing failed for ticket {ticket.id}, using fallback: {e}")
            self._classify_simple_fallback(ticket)
    
    def _classify_simple_fallback(self, ticket: Ticket) -> None:
        """Fallback to simple classification if enhanced method fails."""
        prompt = f"""Classify this customer support ticket into ONE of these categories: {', '.join(self.categories)}

Ticket: "{ticket.content}"

Respond with ONLY the category name."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        category = content.strip()
        
        # Validate category
        if category not in self.categories:
            category_lower = category.lower()
            for valid_category in self.categories:
                if valid_category.lower() in category_lower or category_lower in valid_category.lower():
                    category = valid_category
                    break
            else:
                category = "Other"
        
        ticket.category = category
        ticket.confidence = 0.75  # Lower confidence for fallback method
    
    def _apply_confidence_thresholds(self, ticket: Ticket) -> None:
        """Apply confidence thresholds to determine if human review is needed.
        
        Args:
            ticket: Ticket with confidence score (modified in place)
        """
        if ticket.confidence is None:
            ticket.requires_review = True
            return
        
        if ticket.confidence < config.CONFIDENCE_LOW:
            ticket.requires_review = True
        elif ticket.confidence < config.CONFIDENCE_MEDIUM:
            # Medium confidence - flag for review but allow automatic processing
            ticket.requires_review = True
        # High confidence tickets don't need review


class MockClassifier(TicketClassifier):
    """Mock classifier for testing without API calls."""
    
    def __init__(self):
        """Initialize the mock classifier."""
        self.categories = config.CATEGORIES
    
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Mock classification with enhanced ambiguity handling.
        
        Args:
            tickets: List of Ticket objects to classify
            
        Returns:
            List of classified Ticket objects
        """
        results = []
        
        for ticket in tickets:
            category, confidence, reasoning = self._mock_classify_enhanced(ticket.content)
            ticket.category = category
            ticket.confidence = confidence
            ticket.reasoning = reasoning
            
            # Apply confidence thresholds
            if confidence < config.CONFIDENCE_LOW:
                ticket.requires_review = True
                # Suggest alternative for very low confidence
                alternatives = [c for c in self.categories if c != category]
                if alternatives:
                    ticket.alternative_category = random.choice(alternatives)
            elif confidence < config.CONFIDENCE_MEDIUM:
                ticket.requires_review = True
            
            results.append(ticket)
        
        return results
    
    def _mock_classify_enhanced(self, content: str) -> Tuple[str, float, str]:
        """Enhanced keyword-based classification with reasoning.
        
        Returns:
            Tuple of (category, confidence, reasoning)
        """
    def _mock_classify_enhanced(self, content: str) -> Tuple[str, float, str]:
        """Enhanced keyword-based classification with reasoning.
        
        Returns:
            Tuple of (category, confidence, reasoning)
        """
        content_lower = content.lower()
        
        # Billing keywords with reasoning
        billing_keywords = ['bill', 'charge', 'payment', 'invoice', 'refund', 'pricing', 'cost']
        billing_matches = [word for word in billing_keywords if word in content_lower]
        if billing_matches:
            confidence = min(0.95, 0.70 + len(billing_matches) * 0.10)
            reasoning = f"Detected billing-related keywords: {', '.join(billing_matches[:3])}"
            return "Billing", confidence, reasoning
        
        # Technical keywords with reasoning
        technical_keywords = ['error', 'bug', 'crash', 'not working', 'broken', 'issue', 'problem', 'technical']
        technical_matches = [word for word in technical_keywords if word in content_lower]
        if technical_matches:
            confidence = min(0.95, 0.70 + len(technical_matches) * 0.10)
            reasoning = f"Detected technical issue keywords: {', '.join(technical_matches[:3])}"
            return "Technical Issue", confidence, reasoning
        
        # Sales keywords with reasoning
        sales_keywords = ['buy', 'purchase', 'product', 'demo', 'sales', 'pricing plan', 'features']
        sales_matches = [word for word in sales_keywords if word in content_lower]
        if sales_matches:
            confidence = min(0.95, 0.70 + len(sales_matches) * 0.10)
            reasoning = f"Detected sales inquiry keywords: {', '.join(sales_matches[:3])}"
            return "Sales Inquiry", confidence, reasoning
        
        # Default to Other with low confidence
        return "Other", 0.45, "No strong keyword matches found for any category"
