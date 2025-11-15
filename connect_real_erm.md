3. Real CRM Mode (Actual HTTP Connection)
To connect to a real CRM system:Step 1: Add to your .env file:
env
CRM_MODE=real
CRM_REAL_ENDPOINT=https://your-crm-system.com/api/tickets
Step 2: Install requests library:
bash
pip install requests
Step 3: Run the application:
bash
python main.py --simple
The system will POST JSON data to your CRM endpoint with this structure:
json
{
  "ticket_id": "T001",
  "content": "ticket text",
  "category": "Billing",
  "confidence": 0.95,
  "timestamp": "2025-11-14T15:30:00",
  "requires_review": false,
  "reasoning": "explanation"
}