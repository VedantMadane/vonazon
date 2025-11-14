# AI Ticket Classifier - Customer Support Automation

An intelligent ticket classification system that uses AI to categorize customer support tickets and integrates with CRM systems.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run with Mock Classifier (No API Key Needed)
```bash
# Simple output format (matches Problem Statement example)
python main.py --mock --simple

# Detailed output format with confidence scores and reasoning
python main.py --mock
```

### 3. Run with OpenAI API
```bash
# Set your API key first
$env:OPENAI_API_KEY='your-key-here'  # Windows PowerShell
export OPENAI_API_KEY='your-key-here'  # Linux/Mac

# Run with simple output
python main.py --simple

# Run with detailed output (default)
python main.py
```

### 4. Run Tests
```bash
python tests.py
```

## Command Line Options

| Flag | Description |
|------|-------------|
| `--mock` | Use mock classifier instead of OpenAI API (no API key required) |
| `--simple` | Use simple output format matching Problem Statement example |
| `--export` | Export classification results to JSON file |
| `--tickets "ticket1" "ticket2"` | Classify custom tickets instead of sample data |

## Example Usage

### Simple Output (Interview Format)
```bash
python main.py --mock --simple
```

Output:
```
Ticket: "My invoice shows an extra charge that I didn't authorize."
Category: Billing
Pushed to CRM endpoint: Success

Ticket: "I can't log in to my account — the system says my password is invalid."
Category: Technical Issue
Pushed to CRM endpoint: Success
```

### Detailed Output (Production Format)
```bash
python main.py --mock
```

Shows:
- Full ticket details with IDs
- Confidence scores for each classification
- Reasoning explaining the classification decision
- Human review flags for ambiguous tickets
- Alternative category suggestions
- Category distribution statistics

## Project Structure

| File | Purpose |
|------|----------|
| `config.py` | Configuration settings (API keys, categories, model parameters, thresholds) |
| `utils.py` | Ticket data class and output formatting utilities |
| `ticket_classifier.py` | Classification logic (OpenAI & Mock classifiers with confidence scoring) |
| `crm_integration.py` | CRM integration with multiple simulation modes |
| `main.py` | Main orchestration and CLI entry point |
| `tests.py` | Comprehensive unit tests |
| `requirements.txt` | Python dependencies |

## Features

### Core Functionality
- **Modular OOP Design** - Clean separation of concerns with abstract base classes
- **Dual Mode** - Real OpenAI API or mock classifier for testing
- **Multiple Output Formats** - Simple (Problem Statement) or Detailed (Production)
- **Error Handling** - Graceful handling of API failures and edge cases
- **Batch Processing** - Efficient handling of multiple tickets

### Advanced Features (Phase 1 Improvements)
- **Enhanced Ambiguity Handling** - Confidence-based classification with thresholds:
  - High confidence (>0.85): Automatic routing
  - Medium confidence (0.70-0.85): Automatic with review flag
  - Low confidence (0.50-0.70): Queue for human verification
  - Very low (<0.50): Direct to human triage with alternative suggestions
  
- **Structured Reasoning** - AI provides explanation for each classification decision
  
- **CRM Simulation Modes**:
  - `mock` - In-memory simulation (default, fast)
  - `mock-http` - Realistic HTTP simulation with delays and error scenarios
  - `real` - Actual HTTP POST to configured CRM endpoint

- **Statistics & Export** - Category distribution, success rates, JSON export

- **Custom Input** - Pass your own tickets via CLI arguments

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required for API mode) | Your OpenAI API key |
| `OUTPUT_FORMAT` | `detailed` | Output format: `simple` or `detailed` |
| `CRM_MODE` | `mock` | CRM simulation mode: `mock`, `mock-http`, or `real` |
| `CRM_REAL_ENDPOINT` | - | URL for real CRM HTTP endpoint |
| `CRM_SIMULATE_DELAY` | `0.1` | Simulated delay in seconds for `mock-http` mode |
| `CRM_FAILURE_RATE` | `0.0` | Failure rate (0.0-1.0) for testing error handling |

### Confidence Thresholds

Defined in `config.py`:
- `CONFIDENCE_HIGH = 0.85` - Automatic processing threshold
- `CONFIDENCE_MEDIUM = 0.70` - Review flagging threshold  
- `CONFIDENCE_LOW = 0.50` - Human verification required threshold

## Problem Statement Alignment

This implementation addresses all requirements from the Vonazon AI Product Engineer interview:

✅ Accepts a list of customer support tickets  
✅ Classifies into predefined categories using AI  
✅ Simulates CRM endpoint push with multiple modes  
✅ Clean, readable output matching example format  
✅ Modular, well-documented code  
✅ Proper AI API integration with error handling  
✅ Testing and validation logic  
✅ **Stretch Goal**: Command-line interface ✓  
✅ **Stretch Goal**: Handles ambiguous tickets gracefully ✓  

## Architecture Decisions

### Why Two Output Formats?
- **Simple**: Matches Problem Statement example perfectly for interview demonstration
- **Detailed**: Production-ready format with full observability and debugging info

### Why Multiple CRM Modes?
- **Mock**: Fast unit testing without network overhead
- **Mock-HTTP**: Demonstrates realistic integration patterns and error handling
- **Real**: Production deployment with actual CRM systems

### Why Structured AI Responses?
- Provides confidence scores for better decision-making
- Enables reasoning transparency for auditing
- Supports alternative suggestions for ambiguous cases
- Allows data-driven improvements to classification accuracy

## Discussion Points for Interview

### Scalability Considerations
- Current: Sequential processing suitable for moderate volumes
- Improvement: Batch API calls to reduce latency and costs
- Production: Queue-based architecture with parallel workers
- Rate limiting and exponential backoff for API resilience

### Production Readiness Enhancements
- Replace print statements with structured logging (JSON format)
- Add metrics collection and monitoring dashboards
- Implement retry logic with exponential backoff
- Add authentication and authorization for CRM endpoints
- Containerize for cloud deployment

### AI Integration Evolution
- Multi-provider support (OpenAI, Anthropic, Azure, etc.)
- Fine-tuning on historical ticket data for improved accuracy
- Active learning loop to continuously improve classifications
- Category expansion and hierarchical classification
- Multi-language support for global operations

## License

This project was created as part of the Vonazon AI Product Engineer interview process.