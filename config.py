"""Configuration settings for the ticket classification system."""

import os
from typing import List

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Classification Categories
CATEGORIES: List[str] = [
    "Billing",
    "Technical Issue",
    "Sales Inquiry",
    "Other"
]

# CRM Configuration
MOCK_CRM_ENDPOINT = "mock://crm.vonazon.com/api/tickets"

# Model Configuration
DEFAULT_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3
CONFIDENCE_THRESHOLD = 0.7
