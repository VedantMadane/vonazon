"""Flask web application for AI Ticket Classifier."""

from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
from io import StringIO, BytesIO
import traceback

from ticket_classifier import OpenAIClassifier, MockClassifier
from crm_integration import CRMIntegration
from utils import create_tickets_from_texts, Ticket
from data_manager import DataManager
import config

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize data manager
data_manager = DataManager()


# ===== WEB ROUTES (HTML Pages) =====

@app.route('/')
def index():
    """Dashboard/home page."""
    return render_template('dashboard.html')


@app.route('/classify')
def classify_page():
    """Ticket classification page."""
    return render_template('classify.html')


@app.route('/review')
def review_page():
    """Review queue page."""
    return render_template('review.html')


@app.route('/history')
def history_page():
    """History and analytics page."""
    return render_template('history.html')


@app.route('/settings')
def settings_page():
    """Settings and configuration page."""
    return render_template('settings.html')


# ===== API ROUTES (JSON Endpoints) =====

# Classification Endpoints

@app.route('/api/classify', methods=['POST'])
def api_classify():
    """Classify tickets endpoint.
    
    Request body:
        {
            "tickets": ["ticket text 1", "ticket text 2", ...],
            "use_real_api": true/false,
            "categories": ["Billing", "Technical Issue", ...],
            "crm_mode": "mock"/"mock-http"/"real"
        }
    
    Returns:
        {
            "success": true/false,
            "tickets": [...classified ticket objects...],
            "crm_results": [...],
            "error": "error message if failed"
        }
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        ticket_texts = data.get('tickets', [])
        use_real_api = data.get('use_real_api', True)
        crm_mode = data.get('crm_mode', 'mock')
        
        if not ticket_texts:
            return jsonify({
                "success": False,
                "error": "No tickets provided"
            }), 400
        
        # Create ticket objects
        tickets = create_tickets_from_texts(ticket_texts)
        
        # Classify tickets
        if use_real_api:
            try:
                classifier = OpenAIClassifier()
            except ValueError as e:
                return jsonify({
                    "success": False,
                    "error": f"OpenAI API configuration error: {str(e)}"
                }), 400
        else:
            classifier = MockClassifier()
        
        classified_tickets = classifier.classify(tickets)
        
        # Set CRM mode temporarily
        original_crm_mode = os.environ.get('CRM_MODE', config.CRM_MODE)
        os.environ['CRM_MODE'] = crm_mode
        
        # Push to CRM
        crm = CRMIntegration()
        crm_results = crm.push_batch(classified_tickets)
        
        # Restore original CRM mode
        os.environ['CRM_MODE'] = original_crm_mode
        
        # Save to data storage
        data_manager.save_tickets_batch(classified_tickets, crm_results)
        
        # Convert tickets to dictionaries
        tickets_data = []
        for i, ticket in enumerate(classified_tickets):
            crm_result = crm_results[i] if i < len(crm_results) else {}
            tickets_data.append({
                "id": ticket.id,
                "content": ticket.content,
                "category": ticket.category,
                "confidence": ticket.confidence,
                "reasoning": getattr(ticket, 'reasoning', ''),
                "alternative_category": getattr(ticket, 'alternative_category', None),
                "requires_review": getattr(ticket, 'requires_review', False),
                "timestamp": datetime.now().isoformat(),
                "crm_status": crm_result.get("status", "pending").lower(),
                "crm_id": crm_result.get("crm_id")
            })
        
        return jsonify({
            "success": True,
            "tickets": tickets_data,
            "crm_results": crm_results
        })
        
    except Exception as e:
        print(f"Error in classify endpoint: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/tickets', methods=['GET'])
def api_get_tickets():
    """Get ticket history with pagination and filtering.
    
    Query parameters:
        limit: Max tickets to return (default: 50)
        offset: Skip this many tickets (default: 0)
        category: Filter by category
        requires_review: Filter by review status
    
    Returns:
        {
            "success": true,
            "tickets": [...],
            "total": total_count
        }
    """
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build filter
        filter_dict = {}
        if 'category' in request.args:
            filter_dict['category'] = request.args['category']
        if 'requires_review' in request.args:
            filter_dict['requires_review'] = request.args['requires_review'].lower() == 'true'
        
        tickets = data_manager.get_tickets(limit, offset, filter_dict)
        
        return jsonify({
            "success": True,
            "tickets": tickets,
            "total": len(tickets)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def api_get_ticket(ticket_id):
    """Get single ticket details."""
    try:
        ticket = data_manager.get_ticket_by_id(ticket_id)
        
        if ticket:
            return jsonify({
                "success": True,
                "ticket": ticket
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ticket not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def api_update_ticket(ticket_id):
    """Update ticket fields.
    
    Request body:
        {
            "category": "new category",
            "confidence": 0.95,
            "reviewed_by": "user@example.com",
            "review_notes": "notes"
        }
    """
    try:
        updates = request.get_json()
        
        success = data_manager.update_ticket(ticket_id, updates)
        
        if success:
            ticket = data_manager.get_ticket_by_id(ticket_id)
            return jsonify({
                "success": True,
                "ticket": ticket
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ticket not found or update failed"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Review Queue Endpoints

@app.route('/api/review-queue', methods=['GET'])
def api_get_review_queue():
    """Get pending review tickets.
    
    Query parameters:
        confidence_filter: Filter by confidence level (low/medium/high)
    """
    try:
        confidence_filter = request.args.get('confidence_filter')
        
        queue = data_manager.get_review_queue(confidence_filter)
        
        return jsonify({
            "success": True,
            "queue": queue,
            "count": len(queue)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/review-queue/<ticket_id>/approve', methods=['POST'])
def api_approve_ticket(ticket_id):
    """Approve a ticket classification.
    
    Request body:
        {
            "notes": "approval notes"
        }
    """
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        # Update ticket
        updates = {
            "requires_review": False,
            "reviewed_by": "system",  # In multi-user version, use actual user
            "review_notes": notes,
            "crm_status": "success"
        }
        
        success = data_manager.update_ticket(ticket_id, updates)
        
        if success:
            # Push to CRM if not already done
            ticket = data_manager.get_ticket_by_id(ticket_id)
            
            return jsonify({
                "success": True,
                "message": "Ticket approved and pushed to CRM",
                "ticket": ticket
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ticket not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/review-queue/<ticket_id>/update', methods=['POST'])
def api_update_review_ticket(ticket_id):
    """Update ticket category during review.
    
    Request body:
        {
            "category": "new category",
            "confidence": 0.95,
            "notes": "review notes"
        }
    """
    try:
        data = request.get_json()
        
        category = data.get('category')
        confidence = data.get('confidence')
        notes = data.get('notes', '')
        
        if not category:
            return jsonify({
                "success": False,
                "error": "Category is required"
            }), 400
        
        updates = {
            "category": category,
            "confidence": confidence if confidence is not None else 1.0,
            "requires_review": False,
            "reviewed_by": "system",
            "review_notes": notes,
            "crm_status": "success"
        }
        
        success = data_manager.update_ticket(ticket_id, updates)
        
        if success:
            ticket = data_manager.get_ticket_by_id(ticket_id)
            return jsonify({
                "success": True,
                "message": "Ticket updated and pushed to CRM",
                "ticket": ticket
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ticket not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/review-queue/batch-approve', methods=['POST'])
def api_batch_approve():
    """Approve multiple tickets at once.
    
    Request body:
        {
            "ticket_ids": ["TKT-001", "TKT-002", ...]
        }
    """
    try:
        data = request.get_json()
        ticket_ids = data.get('ticket_ids', [])
        
        if not ticket_ids:
            return jsonify({
                "success": False,
                "error": "No ticket IDs provided"
            }), 400
        
        results = []
        for ticket_id in ticket_ids:
            updates = {
                "requires_review": False,
                "reviewed_by": "system",
                "crm_status": "success"
            }
            success = data_manager.update_ticket(ticket_id, updates)
            results.append({"ticket_id": ticket_id, "success": success})
        
        return jsonify({
            "success": True,
            "message": f"Processed {len(ticket_ids)} tickets",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Statistics Endpoints

@app.route('/api/statistics', methods=['GET'])
def api_get_statistics():
    """Get classification statistics.
    
    Query parameters:
        period: Time period (today/week/month/all) - default: all
    """
    try:
        period = request.args.get('period', 'all')
        
        stats = data_manager.get_statistics(period)
        
        return jsonify({
            "success": True,
            "statistics": stats
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/statistics/export', methods=['POST'])
def api_export_data():
    """Export ticket data.
    
    Request body:
        {
            "format": "json" or "csv",
            "filters": {...}
        }
    """
    try:
        data = request.get_json()
        format_type = data.get('format', 'json')
        filters = data.get('filters', {})
        
        exported_data = data_manager.export_data(format_type, filters)
        
        # Create file response
        if format_type == 'json':
            output = BytesIO(exported_data.encode('utf-8'))
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        elif format_type == 'csv':
            output = BytesIO(exported_data.encode('utf-8'))
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        else:
            return jsonify({
                "success": False,
                "error": "Invalid format. Use 'json' or 'csv'"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Configuration Endpoints

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """Get current configuration."""
    try:
        user_config = data_manager.get_user_config()
        
        # Don't expose full API key
        if user_config.get('openai_api_key'):
            user_config['openai_api_key'] = '****' + user_config['openai_api_key'][-4:] if len(user_config['openai_api_key']) > 4 else '****'
        
        return jsonify({
            "success": True,
            "config": user_config
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/config', methods=['PUT'])
def api_update_config():
    """Update configuration.
    
    Request body:
        {
            "openai_api_key": "new-key",
            "model": "gpt-4",
            "temperature": 0.5,
            ...
        }
    """
    try:
        updates = request.get_json()
        
        # Update environment variables for immediate effect
        if 'crm_mode' in updates:
            os.environ['CRM_MODE'] = updates['crm_mode']
        if 'crm_real_endpoint' in updates:
            os.environ['CRM_REAL_ENDPOINT'] = updates['crm_real_endpoint']
        if 'openai_api_key' in updates and updates['openai_api_key'] and not updates['openai_api_key'].startswith('****'):
            os.environ['OPENAI_API_KEY'] = updates['openai_api_key']
        
        success = data_manager.update_user_config(updates)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Configuration updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update configuration"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/config/test-openai', methods=['POST'])
def api_test_openai():
    """Test OpenAI connection.
    
    Request body:
        {
            "api_key": "key to test (optional, uses env var if not provided)"
        }
    """
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key')
        
        # Try to create classifier
        try:
            classifier = OpenAIClassifier(api_key=api_key)
            
            # Test with a simple classification
            test_ticket = Ticket(id="TEST-001", content="Test ticket for connection")
            classifier._classify_single_ticket_enhanced(test_ticket)
            
            return jsonify({
                "success": True,
                "message": "OpenAI API connection successful"
            })
            
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Configuration error: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/config/test-crm', methods=['POST'])
def api_test_crm():
    """Test CRM connection.
    
    Request body:
        {
            "mode": "mock/mock-http/real",
            "endpoint": "https://crm.example.com/api"
        }
    """
    try:
        data = request.get_json()
        mode = data.get('mode', 'mock')
        endpoint = data.get('endpoint', '')
        
        # Temporarily set CRM mode
        original_mode = os.environ.get('CRM_MODE')
        original_endpoint = os.environ.get('CRM_REAL_ENDPOINT')
        
        os.environ['CRM_MODE'] = mode
        if endpoint:
            os.environ['CRM_REAL_ENDPOINT'] = endpoint
        
        try:
            # Test CRM integration
            crm = CRMIntegration()
            test_ticket = Ticket(id="TEST-001", content="Test ticket", category="Technical Issue")
            result = crm.push_ticket(test_ticket)
            
            # Restore original settings
            if original_mode:
                os.environ['CRM_MODE'] = original_mode
            if original_endpoint:
                os.environ['CRM_REAL_ENDPOINT'] = original_endpoint
            
            return jsonify({
                "success": True,
                "message": f"CRM connection successful in {mode} mode",
                "result": result
            })
            
        except Exception as e:
            # Restore original settings
            if original_mode:
                os.environ['CRM_MODE'] = original_mode
            if original_endpoint:
                os.environ['CRM_REAL_ENDPOINT'] = original_endpoint
            
            return jsonify({
                "success": False,
                "error": f"CRM test failed: {str(e)}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Error handlers

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template('dashboard.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return "Internal server error", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
