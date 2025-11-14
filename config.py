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

# Output Configuration
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "detailed")  # "simple" or "detailed"

# CRM Simulation Mode
CRM_MODE = os.getenv("CRM_MODE", "mock")  # "mock", "mock-http", or "real"
CRM_REAL_ENDPOINT = os.getenv("CRM_REAL_ENDPOINT", "")
CRM_SIMULATE_DELAY = float(os.getenv("CRM_SIMULATE_DELAY", "0.1"))  # seconds
CRM_FAILURE_RATE = float(os.getenv("CRM_FAILURE_RATE", "0.0"))  # 0.0 to 1.0

# Confidence Thresholds for Ambiguous Handling
CONFIDENCE_HIGH = 0.85
CONFIDENCE_MEDIUM = 0.70
CONFIDENCE_LOW = 0.50
