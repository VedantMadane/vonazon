/**
 * Common JavaScript utilities for AI Ticket Classifier
 */

// ===== API Client =====
const API = {
    /**
     * Make an API request
     */
    async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(endpoint, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    /**
     * Classify tickets
     */
    async classify(tickets, useRealApi = true, crmMode = 'mock') {
        return this.request('/api/classify', {
            method: 'POST',
            body: JSON.stringify({
                tickets,
                use_real_api: useRealApi,
                crm_mode: crmMode
            })
        });
    },
    
    /**
     * Get ticket history
     */
    async getTickets(limit = 50, offset = 0, filters = {}) {
        const params = new URLSearchParams({
            limit,
            offset,
            ...filters
        });
        return this.request(`/api/tickets?${params}`);
    },
    
    /**
     * Get single ticket
     */
    async getTicket(ticketId) {
        return this.request(`/api/tickets/${ticketId}`);
    },
    
    /**
     * Update ticket
     */
    async updateTicket(ticketId, updates) {
        return this.request(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    },
    
    /**
     * Get review queue
     */
    async getReviewQueue(confidenceFilter = null) {
        const params = confidenceFilter ? `?confidence_filter=${confidenceFilter}` : '';
        return this.request(`/api/review-queue${params}`);
    },
    
    /**
     * Approve ticket
     */
    async approveTicket(ticketId, notes = '') {
        return this.request(`/api/review-queue/${ticketId}/approve`, {
            method: 'POST',
            body: JSON.stringify({ notes })
        });
    },
    
    /**
     * Update review ticket
     */
    async updateReviewTicket(ticketId, category, confidence, notes = '') {
        return this.request(`/api/review-queue/${ticketId}/update`, {
            method: 'POST',
            body: JSON.stringify({ category, confidence, notes })
        });
    },
    
    /**
     * Batch approve tickets
     */
    async batchApprove(ticketIds) {
        return this.request('/api/review-queue/batch-approve', {
            method: 'POST',
            body: JSON.stringify({ ticket_ids: ticketIds })
        });
    },
    
    /**
     * Get statistics
     */
    async getStatistics(period = 'all') {
        return this.request(`/api/statistics?period=${period}`);
    },
    
    /**
     * Export data
     */
    async exportData(format = 'json', filters = {}) {
        const response = await fetch('/api/statistics/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ format, filters })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tickets_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },
    
    /**
     * Get configuration
     */
    async getConfig() {
        return this.request('/api/config');
    },
    
    /**
     * Update configuration
     */
    async updateConfig(updates) {
        return this.request('/api/config', {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    },
    
    /**
     * Test OpenAI connection
     */
    async testOpenAI(apiKey = null) {
        return this.request('/api/config/test-openai', {
            method: 'POST',
            body: JSON.stringify({ api_key: apiKey })
        });
    },
    
    /**
     * Test CRM connection
     */
    async testCRM(mode, endpoint = '') {
        return this.request('/api/config/test-crm', {
            method: 'POST',
            body: JSON.stringify({ mode, endpoint })
        });
    }
};

// ===== Toast Notifications =====
const Toast = {
    container: null,
    
    init() {
        this.container = document.getElementById('toastContainer');
    },
    
    show(message, type = 'info', duration = 3000) {
        if (!this.container) this.init();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        this.container.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => {
                toast.remove();
            }, duration);
        }
    },
    
    success(message, duration) {
        this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        this.show(message, 'error', duration);
    },
    
    warning(message, duration) {
        this.show(message, 'warning', duration);
    },
    
    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// ===== Loading Overlay =====
const Loading = {
    overlay: null,
    
    init() {
        this.overlay = document.getElementById('loadingOverlay');
    },
    
    show(message = 'Processing...') {
        if (!this.overlay) this.init();
        if (this.overlay) {
            const text = this.overlay.querySelector('p');
            if (text) text.textContent = message;
            this.overlay.style.display = 'flex';
        }
    },
    
    hide() {
        if (!this.overlay) this.init();
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
};

// ===== Utility Functions =====

/**
 * Format date to readable string
 */
function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format confidence as percentage
 */
function formatConfidence(confidence) {
    return `${(confidence * 100).toFixed(1)}%`;
}

/**
 * Get confidence badge class
 */
function getConfidenceBadge(confidence) {
    if (confidence >= 0.85) return 'badge-success';
    if (confidence >= 0.70) return 'badge-warning';
    if (confidence >= 0.50) return 'badge-neutral';
    return 'badge-danger';
}

/**
 * Get confidence color for progress bar
 */
function getConfidenceColor(confidence) {
    if (confidence >= 0.85) return 'success';
    if (confidence >= 0.70) return 'warning';
    return 'danger';
}

/**
 * Get category badge class
 */
function getCategoryBadge(category) {
    const badges = {
        'Billing': 'badge-primary',
        'Technical Issue': 'badge-danger',
        'Sales Inquiry': 'badge-success',
        'Other': 'badge-neutral'
    };
    return badges[category] || 'badge-neutral';
}

/**
 * Truncate text
 */
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Parse CSV file
 */
function parseCSV(text) {
    const lines = text.split('\n').filter(line => line.trim());
    return lines;
}

/**
 * Parse text tickets (one per line)
 */
function parseTickets(text) {
    return text
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Create empty state message
 */
function createEmptyState(message, iconHtml = '📋') {
    return `
        <div class="empty-state" style="text-align: center; padding: 4rem 2rem; color: var(--neutral-500);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">${iconHtml}</div>
            <p style="font-size: 1.125rem;">${message}</p>
        </div>
    `;
}

/**
 * Validate ticket input
 */
function validateTickets(tickets) {
    if (!Array.isArray(tickets) || tickets.length === 0) {
        return { valid: false, error: 'Please enter at least one ticket' };
    }
    
    const empty = tickets.filter(t => !t || t.trim().length === 0);
    if (empty.length > 0) {
        return { valid: false, error: 'Some tickets are empty' };
    }
    
    const tooLong = tickets.filter(t => t.length > 5000);
    if (tooLong.length > 0) {
        return { valid: false, error: 'Some tickets exceed maximum length (5000 characters)' };
    }
    
    return { valid: true };
}

/**
 * Handle file upload
 */
async function handleFileUpload(file, callback) {
    if (!file) return;
    
    const validTypes = ['text/plain', 'text/csv', 'application/csv'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.txt') && !file.name.endsWith('.csv')) {
        Toast.error('Invalid file type. Please upload a TXT or CSV file.');
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
        Toast.error('File too large. Maximum size is 5MB.');
        return;
    }
    
    try {
        const text = await file.text();
        const tickets = parseTickets(text);
        callback(tickets);
    } catch (error) {
        Toast.error('Failed to read file: ' + error.message);
    }
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        Toast.success('Copied to clipboard');
    } catch (error) {
        Toast.error('Failed to copy to clipboard');
    }
}

/**
 * Simple client-side table sort
 */
function sortTable(tableId, columnIndex, ascending = true) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }
        
        // Compare as strings
        return ascending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Toast.init();
    Loading.init();
});

// Export for use in other scripts
window.API = API;
window.Toast = Toast;
window.Loading = Loading;
window.formatDate = formatDate;
window.formatConfidence = formatConfidence;
window.getConfidenceBadge = getConfidenceBadge;
window.getConfidenceColor = getConfidenceColor;
window.getCategoryBadge = getCategoryBadge;
window.truncateText = truncateText;
window.parseTickets = parseTickets;
window.parseCSV = parseCSV;
window.debounce = debounce;
window.createEmptyState = createEmptyState;
window.validateTickets = validateTickets;
window.handleFileUpload = handleFileUpload;
window.copyToClipboard = copyToClipboard;
window.sortTable = sortTable;
