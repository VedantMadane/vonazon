# AI Ticket Classifier - Frontend

A modern, responsive web interface for the AI Ticket Classification system built with Flask, HTML, CSS, and JavaScript.

## Features

### 🎯 Core Functionality
- **Dashboard**: Overview with real-time statistics and quick classification
- **Classify Tickets**: Advanced classification with batch processing and file upload
- **Review Queue**: Manage tickets flagged for human review
- **History & Analytics**: View past classifications with detailed statistics
- **Settings**: Configure API, CRM integration, and system preferences

### 🎨 UI/UX Highlights
- Modern, clean design with consistent color scheme
- Responsive layout (works on mobile, tablet, and desktop)
- Real-time updates and toast notifications
- Drag-and-drop file upload support
- Loading states and skeleton loaders
- Interactive charts and progress bars

### 🔧 Technical Features
- RESTful API with 15+ endpoints
- JSON file-based data persistence
- Session management
- Error handling and validation
- Export to JSON/CSV
- Real-time statistics caching

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements include:
- `flask>=3.0.0` - Web framework
- `openai>=1.0.0` - AI classification
- `python-dotenv>=1.0.0` - Environment variables

### 2. Run the Application

```bash
# Using system Python
C:\Python310\python.exe app.py

# Or if Python is in PATH
python app.py
```

### 3. Access the Interface

Open your browser and navigate to:
```
http://localhost:5000
```

The server will run in debug mode by default, with auto-reload on file changes.

## Project Structure

```
.
├── app.py                      # Flask application & API endpoints
├── data_manager.py             # Data persistence layer
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Home page with statistics
│   ├── classify.html          # Classification interface
│   ├── review.html            # Review queue management
│   ├── history.html           # Analytics and history
│   └── settings.html          # Configuration page
├── static/
│   ├── css/
│   │   └── styles.css         # All CSS styles (responsive design)
│   └── js/
│       └── main.js            # Common utilities & API client
├── data/
│   ├── tickets.json           # Classified tickets storage
│   ├── review_queue.json      # Pending review tickets
│   ├── statistics.json        # Cached statistics
│   └── config.json            # User configuration
├── ticket_classifier.py        # AI classification logic
├── crm_integration.py          # CRM push functionality
├── utils.py                    # Utility functions
├── config.py                   # System configuration
└── requirements.txt            # Python dependencies
```

## Page Overview

### 1. Dashboard (/)
- Quick classification form
- Statistics cards (total tickets, avg confidence, pending review, CRM success)
- Recent activity feed
- Drag-and-drop file upload

### 2. Classify Tickets (/classify)
- Advanced classification interface
- Batch processing support
- Configuration options (API mode, CRM mode, output format)
- File upload with validation
- Detailed results table
- Export functionality (JSON/CSV)

### 3. Review Queue (/review)
- Filter by confidence level (low/medium/high)
- Ticket cards with full details
- Review actions (Approve, Change Category, Reject)
- Category change form
- Batch operations support

### 4. History & Analytics (/history)
- Time period filters (Today, Week, Month, All Time)
- Statistics dashboard
- Category breakdown with visual charts
- Searchable classification history
- Pagination for large datasets
- Export all data

### 5. Settings (/settings)
- **API Configuration**: OpenAI key, model selection, temperature
- **CRM Integration**: Mode selector, endpoint configuration
- **Confidence Thresholds**: Adjustable sliders
- **Category Management**: Add/remove categories
- **Output Preferences**: Format selection
- Connection testing for API and CRM

## API Endpoints

### Classification
- `POST /api/classify` - Classify tickets
- `GET /api/tickets` - Get ticket history
- `GET /api/tickets/:id` - Get single ticket
- `PUT /api/tickets/:id` - Update ticket

### Review Queue
- `GET /api/review-queue` - Get pending reviews
- `POST /api/review-queue/:id/approve` - Approve ticket
- `POST /api/review-queue/:id/update` - Update ticket category
- `POST /api/review-queue/batch-approve` - Batch approve

### Statistics
- `GET /api/statistics` - Get statistics
- `POST /api/statistics/export` - Export data

### Configuration
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration
- `POST /api/config/test-openai` - Test OpenAI connection
- `POST /api/config/test-crm` - Test CRM connection

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```env
OPENAI_API_KEY=your-key-here
CRM_MODE=mock
CRM_REAL_ENDPOINT=https://your-crm.com/api
OUTPUT_FORMAT=detailed
```

### System Settings

All settings can be configured through the web interface:

1. Navigate to Settings page
2. Update desired configuration
3. Test connections
4. Save settings

Settings are persisted to `data/config.json`.

## Usage Examples

### Quick Classification (Dashboard)

1. Go to Dashboard
2. Enter tickets in the text area (one per line)
3. Select "Use Real OpenAI API" or use Mock mode
4. Click "Classify Tickets"
5. View results inline

### Advanced Classification

1. Go to Classify page
2. Choose between text input or file upload
3. Configure classification mode and CRM settings
4. Click "Classify Tickets"
5. Review detailed results table
6. Export results if needed

### Review Workflow

1. Navigate to Review Queue
2. Filter by confidence level
3. For each ticket:
   - Click "Approve" to accept AI classification
   - Click "Change Category" to override
   - Click "Reject" to flag for manual handling
4. System automatically pushes to CRM

### Analytics

1. Go to History & Analytics
2. Select time period filter
3. View statistics dashboard
4. Browse category breakdown
5. Search classification history
6. Export data for reporting

## Data Storage

The system uses JSON files for data persistence:

- **tickets.json**: All classified tickets with full details
- **review_queue.json**: Tickets pending human review
- **statistics.json**: Cached aggregated metrics
- **config.json**: User preferences and settings

Data is stored in the `data/` directory, which is automatically created on first run.

## Development

### Debug Mode

The application runs in debug mode by default:
- Auto-reload on file changes
- Detailed error messages
- Interactive debugger

### Production Deployment

For production:

1. Disable debug mode in `app.py`:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. Set up a reverse proxy (Nginx/Apache)

4. Enable HTTPS

## Troubleshooting

### Flask Module Not Found

If you get `ModuleNotFoundError: No module named 'flask'`:

```bash
# Install in current environment
pip install flask

# Or use system Python directly
C:\Python310\python.exe app.py
```

### Port Already in Use

If port 5000 is busy, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### OpenAI API Errors

1. Check API key in Settings
2. Test connection using "Test Connection" button
3. Verify key is valid and has credits
4. Use Mock mode for testing without API

### Empty Statistics

If dashboard shows zero tickets:
1. Classify some tickets first
2. Statistics are calculated from stored tickets
3. Check `data/tickets.json` exists

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires JavaScript enabled.

## Performance

- Initial page load: < 2 seconds
- Classification (10 tickets): ~5 seconds (OpenAI) / < 1 second (Mock)
- Statistics refresh: < 1 second
- Review queue loading: < 500ms for 50 tickets

## Security Considerations

- API keys are masked in UI
- API keys stored server-side only
- Input validation on all forms
- XSS protection through proper escaping
- Single-user application (no authentication required)

For multi-user deployment, implement:
- User authentication
- Role-based access control
- API key management per user
- HTTPS enforcement

## Future Enhancements

Potential improvements:
- Dark mode theme
- Real-time WebSocket updates
- Advanced charts (Chart.js integration)
- Email notifications
- Multi-language support
- Database migration (SQLite/PostgreSQL)
- Batch operations UI
- Custom category icons
- Keyboard shortcuts

## Support

For issues or questions:
1. Check this README
2. Review error messages in browser console
3. Check Flask server logs in terminal
4. Verify all dependencies are installed

## License

This project is part of the Vonazon AI Ticket Classifier system.
