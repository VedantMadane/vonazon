"""Unit tests for the ticket classification system."""

import unittest
from unittest.mock import Mock, patch

from utils import Ticket, create_tickets_from_texts
from ticket_classifier import MockClassifier, OpenAIClassifier
from crm_integration import CRMIntegration
import config


class TestTicket(unittest.TestCase):
    """Test cases for Ticket class."""
    
    def test_ticket_creation(self):
        """Test ticket object creation."""
        ticket = Ticket(id="TKT-001", content="Test content")
        self.assertEqual(ticket.id, "TKT-001")
        self.assertEqual(ticket.content, "Test content")
        self.assertIsNone(ticket.category)
        self.assertIsNone(ticket.confidence)
    
    def test_create_tickets_from_texts(self):
        """Test creating multiple tickets from text list."""
        texts = ["Issue 1", "Issue 2", "Issue 3"]
        tickets = create_tickets_from_texts(texts)
        
        self.assertEqual(len(tickets), 3)
        self.assertEqual(tickets[0].id, "TKT-0001")
        self.assertEqual(tickets[1].content, "Issue 2")


class TestMockClassifier(unittest.TestCase):
    """Test cases for MockClassifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = MockClassifier()
    
    def test_billing_classification(self):
        """Test billing keyword detection."""
        tickets = [
            Ticket(id="TKT-001", content="I was charged twice for my subscription"),
            Ticket(id="TKT-002", content="Please send me an invoice for last month")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Billing")
        self.assertEqual(results[1].category, "Billing")
        self.assertIsNotNone(results[0].confidence)
    
    def test_technical_classification(self):
        """Test technical issue detection."""
        tickets = [
            Ticket(id="TKT-001", content="The app crashes when I click submit"),
            Ticket(id="TKT-002", content="Getting an error message on login")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Technical Issue")
        self.assertEqual(results[1].category, "Technical Issue")
    
    def test_sales_classification(self):
        """Test sales inquiry detection."""
        tickets = [
            Ticket(id="TKT-001", content="I want to buy the Enterprise plan"),
            Ticket(id="TKT-002", content="Can I get a product demo?")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Sales Inquiry")
        self.assertEqual(results[1].category, "Sales Inquiry")
    
    def test_other_classification(self):
        """Test fallback to Other category."""
        tickets = [
            Ticket(id="TKT-001", content="Just saying hello")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Other")


class TestCRMIntegration(unittest.TestCase):
    """Test cases for CRMIntegration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.crm = CRMIntegration()
    
    def test_push_single_ticket(self):
        """Test pushing a single ticket."""
        ticket = Ticket(
            id="TKT-001",
            content="Test content",
            category="Billing",
            confidence=0.95
        )
        
        result = self.crm.push_ticket(ticket)
        
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["crm_id"], "CRM-TKT-001")
        self.assertEqual(len(self.crm.results), 1)
    
    def test_push_unclassified_ticket(self):
        """Test pushing an unclassified ticket."""
        ticket = Ticket(id="TKT-001", content="Test content")
        
        result = self.crm.push_ticket(ticket)
        
        self.assertEqual(result["status"], "Error")
    
    def test_push_batch(self):
        """Test pushing multiple tickets."""
        tickets = [
            Ticket(id="TKT-001", content="Test 1", category="Billing", confidence=0.9),
            Ticket(id="TKT-002", content="Test 2", category="Technical Issue", confidence=0.85)
        ]
        
        results = self.crm.push_batch(tickets)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "Success")
        self.assertEqual(results[1]["status"], "Success")
    
    def test_get_statistics(self):
        """Test statistics generation."""
        tickets = [
            Ticket(id="TKT-001", content="Test 1", category="Billing", confidence=0.9),
            Ticket(id="TKT-002", content="Test 2", category="Billing", confidence=0.85),
            Ticket(id="TKT-003", content="Test 3", category="Technical Issue", confidence=0.95)
        ]
        
        self.crm.push_batch(tickets)
        stats = self.crm.get_statistics()
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["by_category"]["Billing"], 2)
        self.assertEqual(stats["by_category"]["Technical Issue"], 1)


class TestOpenAIClassifier(unittest.TestCase):
    """Test cases for OpenAIClassifier."""
    
    def test_missing_api_key(self):
        """Test initialization without API key."""
        with patch.object(config, 'OPENAI_API_KEY', ''):
            with self.assertRaises(ValueError):
                OpenAIClassifier()
    
    @patch('ticket_classifier.openai.OpenAI')
    def test_classify_with_valid_response(self, mock_openai):
        """Test classification with mocked OpenAI response."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Billing"
        mock_client.chat.completions.create.return_value = mock_response
        
        classifier = OpenAIClassifier(api_key="test-key")
        tickets = [Ticket(id="TKT-001", content="Charge issue")]
        
        results = classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Billing")
        self.assertIsNotNone(results[0].confidence)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
"""Unit tests for the ticket classification system."""

import unittest
from unittest.mock import Mock, patch

from utils import Ticket, create_tickets_from_texts
from ticket_classifier import MockClassifier, OpenAIClassifier
from crm_integration import CRMIntegration
import config


class TestTicket(unittest.TestCase):
    """Test cases for Ticket class."""
    
    def test_ticket_creation(self):
        """Test ticket object creation."""
        ticket = Ticket(id="TKT-001", content="Test content")
        self.assertEqual(ticket.id, "TKT-001")
        self.assertEqual(ticket.content, "Test content")
        self.assertIsNone(ticket.category)
        self.assertIsNone(ticket.confidence)
    
    def test_create_tickets_from_texts(self):
        """Test creating multiple tickets from text list."""
        texts = ["Issue 1", "Issue 2", "Issue 3"]
        tickets = create_tickets_from_texts(texts)
        
        self.assertEqual(len(tickets), 3)
        self.assertEqual(tickets[0].id, "TKT-0001")
        self.assertEqual(tickets[1].content, "Issue 2")


class TestMockClassifier(unittest.TestCase):
    """Test cases for MockClassifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = MockClassifier()
    
    def test_billing_classification(self):
        """Test billing keyword detection."""
        tickets = [
            Ticket(id="TKT-001", content="I was charged twice for my subscription"),
            Ticket(id="TKT-002", content="Please send me an invoice for last month")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Billing")
        self.assertEqual(results[1].category, "Billing")
        self.assertIsNotNone(results[0].confidence)
    
    def test_technical_classification(self):
        """Test technical issue detection."""
        tickets = [
            Ticket(id="TKT-001", content="The app crashes when I click submit"),
            Ticket(id="TKT-002", content="Getting an error message on login")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Technical Issue")
        self.assertEqual(results[1].category, "Technical Issue")
    
    def test_sales_classification(self):
        """Test sales inquiry detection."""
        tickets = [
            Ticket(id="TKT-001", content="I want to buy the Enterprise plan"),
            Ticket(id="TKT-002", content="Can I get a product demo?")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Sales Inquiry")
        self.assertEqual(results[1].category, "Sales Inquiry")
    
    def test_other_classification(self):
        """Test fallback to Other category."""
        tickets = [
            Ticket(id="TKT-001", content="Just saying hello")
        ]
        
        results = self.classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Other")


class TestCRMIntegration(unittest.TestCase):
    """Test cases for CRMIntegration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.crm = CRMIntegration()
    
    def test_push_single_ticket(self):
        """Test pushing a single ticket."""
        ticket = Ticket(
            id="TKT-001",
            content="Test content",
            category="Billing",
            confidence=0.95
        )
        
        result = self.crm.push_ticket(ticket)
        
        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["crm_id"], "CRM-TKT-001")
        self.assertEqual(len(self.crm.results), 1)
    
    def test_push_unclassified_ticket(self):
        """Test pushing an unclassified ticket."""
        ticket = Ticket(id="TKT-001", content="Test content")
        
        result = self.crm.push_ticket(ticket)
        
        self.assertEqual(result["status"], "Error")
    
    def test_push_batch(self):
        """Test pushing multiple tickets."""
        tickets = [
            Ticket(id="TKT-001", content="Test 1", category="Billing", confidence=0.9),
            Ticket(id="TKT-002", content="Test 2", category="Technical Issue", confidence=0.85)
        ]
        
        results = self.crm.push_batch(tickets)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "Success")
        self.assertEqual(results[1]["status"], "Success")
    
    def test_get_statistics(self):
        """Test statistics generation."""
        tickets = [
            Ticket(id="TKT-001", content="Test 1", category="Billing", confidence=0.9),
            Ticket(id="TKT-002", content="Test 2", category="Billing", confidence=0.85),
            Ticket(id="TKT-003", content="Test 3", category="Technical Issue", confidence=0.95)
        ]
        
        self.crm.push_batch(tickets)
        stats = self.crm.get_statistics()
        
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["by_category"]["Billing"], 2)
        self.assertEqual(stats["by_category"]["Technical Issue"], 1)


class TestOpenAIClassifier(unittest.TestCase):
    """Test cases for OpenAIClassifier."""
    
    def test_missing_api_key(self):
        """Test initialization without API key."""
        with patch.object(config, 'OPENAI_API_KEY', ''):
            with self.assertRaises(ValueError):
                OpenAIClassifier()
    
    @patch('ticket_classifier.openai.OpenAI')
    def test_classify_with_valid_response(self, mock_openai):
        """Test classification with mocked OpenAI response."""
        # Mock the OpenAI client and response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Billing"
        mock_client.chat.completions.create.return_value = mock_response
        
        classifier = OpenAIClassifier(api_key="test-key")
        tickets = [Ticket(id="TKT-001", content="Charge issue")]
        
        results = classifier.classify(tickets)
        
        self.assertEqual(results[0].category, "Billing")
        self.assertIsNotNone(results[0].confidence)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
