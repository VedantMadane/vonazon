# 1. Mock Mode (Default - No Real Connection
python main.py --simple
# or explicitly
python main.py --simple

#2. Mock HTTP Mode (Simulated HTTP with delays/errors)
CRM_MODE=mock-http
CRM_SIMULATE_DELAY=0.5
CRM_FAILURE_RATE=0.1

python main.py --simple

