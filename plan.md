## Vonazon AI Product Engineer - Project Round Overview \& Implementation Guide

Congratulations on advancing to **Round 3 (Project Round)** at Vonazon! Here's a comprehensive breakdown of the project requirements and a strategic implementation approach:

***

### Project Overview

**Objective:** Build a Python application that uses AI APIs to categorize customer support tickets and simulate CRM integration.

**Core Requirements:**

- Accept a list of customer support tickets (plain text)
- Classify each ticket into predefined categories (Billing, Technical Issue, Sales Inquiry, Other)
- Simulate sending results to a mock CRM endpoint
- Use any AI API/library (OpenAI, Anthropic, Hugging Face, etc.)

**Format:** Live Coding Exercise (60–90 minutes)

***

### Strategic Implementation Approach

#### Phase 1: Project Structure (Clean \& Modular)

Given your experience with Python development and RAG systems, here's a recommended architecture:

```python
# Structure your project as follows:
# project/
# ├── main.py                    # Entry point
# ├── ticket_classifier.py       # Core classification logic
# ├── crm_integration.py         # Mock CRM handler
# ├── config.py                  # API keys and settings
# ├── utils.py                   # Helper functions
# ├── tests.py                   # Validation logic
# └── requirements.txt           # Dependencies
```


#### Phase 2: Core Implementation

**Step 1: Basic Ticket Classifier**

```python
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Ticket:
    id: str
    content: str
    category: str = None
    confidence: float = None

class TicketClassifier(ABC):
    @abstractmethod
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Classify a list of tickets"""
        pass

class OpenAIClassifier(TicketClassifier):
    def __init__(self, api_key: str):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.categories = ["Billing", "Technical Issue", "Sales Inquiry", "Other"]
    
    def classify(self, tickets: List[Ticket]) -> List[Ticket]:
        """Classify tickets using OpenAI"""
        results = []
        for ticket in tickets:
            prompt = f"""Classify this customer support ticket into ONE category: {', '.join(self.categories)}
            
Ticket: "{ticket.content}"

Respond with ONLY the category name."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # or gpt-3.5-turbo for cost efficiency
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            category = response.choices[^1_0].message.content.strip()
            ticket.category = category if category in self.categories else "Other"
            ticket.confidence = 0.95  # Could extract this from API
            results.append(ticket)
        
        return results
```

**Step 2: CRM Integration (Mock)**

```python
from typing import Dict, List
import json
from datetime import datetime

class CRMIntegration:
    def __init__(self, endpoint: str = "mock://crm"):
        self.endpoint = endpoint
        self.results = []
    
    def push_ticket(self, ticket: Ticket) -> Dict:
        """Push classified ticket to CRM"""
        payload = {
            "ticket_id": ticket.id,
            "content": ticket.content,
            "category": ticket.category,
            "confidence": ticket.confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Mock CRM call
        self.results.append(payload)
        return {
            "status": "Success",
            "crm_id": f"CRM-{ticket.id}",
            "endpoint": self.endpoint
        }
    
    def push_batch(self, tickets: List[Ticket]) -> List[Dict]:
        """Push multiple tickets"""
        return [self.push_ticket(t) for t in tickets]
    
    def get_results(self) -> str:
        """Return results (could write to file)"""
        return json.dumps(self.results, indent=2)
```

**Step 3: Main Orchestration**

```python
def main(ticket_texts: List[str], use_real_api: bool = True):
    """Main workflow orchestration"""
    
    # Create ticket objects
    tickets = [
        Ticket(id=f"TKT-{i+1}", content=text)
        for i, text in enumerate(ticket_texts)
    ]
    
    # Classify tickets
    if use_real_api:
        classifier = OpenAIClassifier(api_key="your-api-key")
    else:
        classifier = MockClassifier()  # For testing
    
    classified_tickets = classifier.classify(tickets)
    
    # Push to CRM
    crm = CRMIntegration()
    crm.push_batch(classified_tickets)
    
    # Output results
    print_results(classified_tickets, crm)

def print_results(tickets: List[Ticket], crm: CRMIntegration):
    """Print formatted output"""
    print("\n" + "="*60)
    print("TICKET CLASSIFICATION RESULTS")
    print("="*60)
    
    for ticket in tickets:
        print(f"\nTicket ID: {ticket.id}")
        print(f"Content: {ticket.content[:50]}...")
        print(f"Category: {ticket.category}")
        print(f"Confidence: {ticket.confidence:.2%}")
        print(f"CRM Status: Pushed")
    
    print("\n" + "="*60)
    print(f"Total Processed: {len(tickets)}")
    print("="*60 + "\n")
```


***

### What They're Evaluating

| Evaluation Area | What Matters | Your Strategy |
| :-- | :-- | :-- |
| **Code Quality** | Modular, readable, follows conventions | Use OOP principles, type hints, clear naming |
| **AI API Integration** | Proper prompt engineering, error handling | Use structured prompts, handle edge cases |
| **Logic \& Workflow** | Data pipeline, classification accuracy | Test with diverse tickets, validate categories |
| **Testing \& Validation** | Correctness verification, edge cases | Include test cases, mock data, assertions |
| **Communication** | Clear explanation of approach | Comment code, explain design decisions verbally |


***

### Implementation Recommendations for You

**Given your background with RAG and LLM systems:**

1. **Use OpenAI or Claude API** (you likely have experience) rather than Hugging Face for faster development
2. **Implement structured output handling** - you know how to work with LLM responses
3. **Add basic error handling** - network failures, rate limiting, malformed responses
4. **Use mock mode for testing** - avoid excessive API calls during development
5. **Consider prompt optimization** - leverage your RAG experience with few-shot examples

***

### Stretch Goals (If Time Permits)

**Recommended priority order:**

1. **Handle ambiguous cases gracefully** - Add "Unclear" category with confidence threshold
2. **Simple tests** - Unit tests for classifier logic
3. **FastAPI endpoint** - You're comfortable with FastAPI; a simple POST endpoint would impress
4. **Batch processing stats** - Accuracy metrics, category distribution

***

### Post-Coding Discussion Preparation

Be ready to discuss:

- **Architecture choices**: Why modular design? Why this OOP structure?
- **API strategy**: Why OpenAI/Anthropic? Rate limiting considerations?
- **Production improvements**: Batching, caching, fine-tuning, classification confidence thresholds
- **Scalability**: How would you handle 10K+ tickets? Async processing? Database integration?
- **Accuracy**: How would you measure and improve classification accuracy?

***

### Timeline Suggestion

- **Research \& Setup** (10 min): Set up environment, API keys
- **Core Implementation** (35-40 min): Build classifier and CRM integration
- **Testing \& Refinement** (10-15 min): Validate with example tickets, fix issues
- **Polish \& Documentation** (5-10 min): Clean code, add comments, prepare explanation

**Total: ~60 minutes** (within the 60-90 minute window)

***

Given your expertise with AI/ML systems and Python, this should be well within your wheelhouse. Focus on **clean code**, **thoughtful design**, and **clear communication** about your approach. Let me know if you need help with any specific part of the implementation or want to discuss the architecture further!
<span style="display:none">[^1_1]</span>

<div align="center">⁂</div>

[^1_1]: Vonazon-AI-Product-Engineer-Interview-Project-V.-1-REV-10.2025.pdf

