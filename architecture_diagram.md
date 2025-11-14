┌─────────────────────────────────────────────────────────────────┐
│                    SUPPORT TICKET PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘

INGESTION LAYER
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Email      │  │   Chat API   │  │   REST API   │
│  Integration │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                    ┌────▼─────┐
                    │  Ticket   │
                    │  Queue    │  (RabbitMQ/SQS)
                    │(Raw Input)│
                    └────┬─────┘
                         │
                         │
PROCESSING LAYER
       ┌─────────────────▼─────────────────┐
       │  Pre-processing Service           │
       │  • Deduplication                  │
       │  • Language detection             │
       │  • Text normalization             │
       │  • Priority scoring               │
       └─────────────────┬─────────────────┘
                         │
                    ┌────▼──────────┐
                    │ Processed     │
                    │ Ticket Queue  │
                    └────┬──────────┘
                         │
CLASSIFICATION LAYER
       ┌─────────────────▼──────────────────────┐
       │  Ticket Classifier Service             │
       │  • OpenAI API (batched calls)          │
       │  • Confidence scoring                  │
       │  • Response caching (Redis)            │
       │  • Retry logic + circuit breaker       │
       │  • Monitoring & alerting               │
       └─────────────────┬──────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌────▼────┐    ┌─────▼──────┐
   │ High      │    │ Medium  │    │ Low        │
   │Confidence │    │Confidence│   │Confidence/ │
   │(>0.85)    │    │(0.6-0.85)    │Ambiguous   │
   └────┬─────┘    └────┬─────┘    └─────┬──────┘
        │                │               │
        │                │               │
ROUTING LAYER
   ┌────▼──────────────────────────────────────────┐
   │  Decision Engine & Router                     │
   │  • Auto-route high confidence                │
   │  • Human review queue for medium/low          │
   │  • Escalation rules                           │
   └────┬──────────────────────────────────────────┘
        │
        ├─────────────┬─────────────┬─────────────┐
        │             │             │             │
        │             │             │             │
OUTPUT LAYER
┌──────▼────────┐ ┌──────▼────────┐ ┌──────▼────────┐
│  Billing      │ │  Technical    │ │  Sales        │
│  Team Inbox   │ │  Support Queue│ │  Inquiry      │
│               │ │               │ │  Follow-up    │
└───────────────┘ └───────────────┘ └───────────────┘

                CRM Integration
                (Salesforce/HubSpot)
                
                ┌──────────────────┐
                │ Analytics DB     │
                │ • Classification │
                │   metrics        │
                │ • Confidence     │
                │   distribution   │
                │ • User feedback  │
                └──────────────────┘
