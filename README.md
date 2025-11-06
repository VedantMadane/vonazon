Quick Start
1. Install Dependencies
bash
pip install -r requirements.txt
2. Run with Mock Classifier (No API Key Needed)
bash
python main.py --mock
3. Run with OpenAI API
bash
# Set your API key first
$env:OPENAI_API_KEY='your-key-here'
python main.py
4. Run Tests
bash
python tests.py


Project Structure
config.py - Configuration settings (API keys, categories, model parameters)
utils.py - Ticket data class and utility functions
ticket_classifier.py - Classification logic (OpenAI & Mock classifiers)
crm_integration.py - CRM integration with mock endpoint
main.py - Main orchestration and entry point
tests.py - Comprehensive unit tests
requirements.txt - Python dependencies
.env.example - Environment variable template
.gitignore - Git ignore rules

 Features
Modular OOP Design - Clean separation of concerns
Dual Mode - Real OpenAI API or mock classifier for testing
Error Handling - Graceful handling of API failures and edge cases
Batch Processing - Efficient handling of multiple tickets
Statistics - Category distribution and success metrics
Export - JSON export capability (--export flag)
Custom Tickets - Pass your own tickets via CLI
Comprehensive Tests - Unit tests for all components