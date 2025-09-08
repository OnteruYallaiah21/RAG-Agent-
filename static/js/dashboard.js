/**
 * AI Agents Dashboard - Real-time Email Processing
 * Handles leads table, notifications, and email processing
 */

class DashboardApp {
    constructor() {
        this.leads = [];
        this.notifications = [];
        this.emailsProcessed = 0;
        
        this.initializeApp();
    }

    initializeApp() {
        this.setupEventListeners();
        this.loadLeads();
        this.loadNotifications();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Process button
        document.getElementById('processEmailBtn').addEventListener('click', () => {
            this.processEmail();
        });

        // Refresh leads button
        document.getElementById('refreshLeadsBtn').addEventListener('click', () => {
            this.loadLeads();
        });

        // Notification button
        document.getElementById('notificationBtn').addEventListener('click', () => {
            this.toggleNotifications();
        });
    }

    async processEmail() {
        const emailContent = document.getElementById('emailBody').value.trim();

        if (!emailContent) {
            this.showNotification('Please enter email content', 'error');
            return;
        }

        try {
            this.showLoading('Processing email...');
            
            // Create proper payload structure
            const emailData = {
                email: {
                    from: "user@example.com", // This would come from actual email parsing
                    name: "User", // This would come from actual email parsing
                    subject: "Email Subject", // This would come from actual email parsing
                    Email_Content: emailContent
                }
            };

            const response = await fetch('/api/email/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            });

            const result = await response.json();
            this.hideLoading();

            if (result.status === 'processed') {
                this.displayEmailOutput(result);
                this.emailsProcessed++;
                this.updateStats();
                this.loadLeads(); // Refresh leads table
                this.addNotification(`Email processed for ${result.to}`, 'success');
                this.showNotification(`Email processed successfully! Intent: ${result.intent}`, 'success');
            } else {
                this.showNotification(result.error || 'Processing failed', 'error');
            }
        } catch (error) {
            this.hideLoading();
            this.showNotification(`API Error: ${error.message}`, 'error');
        }
    }

    displayEmailOutput(result) {
        const emailOutput = document.getElementById('emailOutput');
        emailOutput.innerHTML = `
            <div class="space-y-4">
                <div class="border-b pb-3">
                    <h4 class="font-semibold text-gray-900 mb-2">Generated Reply</h4>
                    <div class="text-sm text-gray-600">
                        <p><strong>To:</strong> ${result.to}</p>
                        <p><strong>Intent:</strong> <span class="capitalize text-blue-600">${result.intent}</span></p>
                        <p><strong>Customer Type:</strong> ${result.customer_type || 'Unknown'}</p>
                        <p><strong>Lead Status:</strong> <span class="${result.is_new_lead ? 'text-green-600' : 'text-blue-600'}">${result.is_new_lead ? 'New Lead' : 'Existing Customer'}</span></p>
                    </div>
                </div>
                <div>
                    <h5 class="font-medium text-gray-900 mb-2">Subject:</h5>
                    <p class="text-gray-700 bg-white p-2 rounded border">${this.escapeHtml(result.reply_subject)}</p>
                </div>
                <div>
                    <h5 class="font-medium text-gray-900 mb-2">Body:</h5>
                    <div class="text-gray-700 bg-white p-3 rounded border whitespace-pre-wrap">${this.escapeHtml(result.reply_body)}</div>
                </div>
            </div>
        `;
    }

    async loadLeads() {
        try {
            const response = await fetch('/api/crm/leads');
            const result = await response.json();
            
            if (result.success) {
                this.leads = result.leads;
                this.updateStats();
                this.renderLeadsTable();
            }
        } catch (error) {
            console.error('Error loading leads:', error);
            this.showNotification('Error loading leads data', 'error');
        }
    }

    renderLeadsTable() {
        const tbody = document.getElementById('leadsTableBody');
        
        if (this.leads.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                        No leads found
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.leads.map(lead => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                <span class="text-sm font-medium text-gray-700">${lead.name.charAt(0)}</span>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${lead.name}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${lead.email}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="status-badge ${lead.status === 'New Lead' ? 'status-new' : 'status-existing'}">
                        ${lead.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${lead.account_id || '-'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${new Date(lead.last_contact).toLocaleDateString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button class="text-blue-600 hover:text-blue-900 mr-3">
                        <i class="fas fa-envelope"></i>
                    </button>
                    <button class="text-green-600 hover:text-green-900">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const result = await response.json();
            
            if (result.success) {
                this.notifications = result.notifications;
                this.updateNotificationBadge(result.unread_count);
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    renderNotifications() {
        const container = document.getElementById('notificationsList');
        
        if (this.notifications.length === 0) {
            container.innerHTML = '<p class="text-center text-gray-500">No notifications</p>';
            return;
        }

        container.innerHTML = this.notifications.map(notification => `
            <div class="notification-item ${notification.read ? '' : 'notification-unread'} p-3 rounded-md">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <p class="text-sm text-gray-900">${notification.message}</p>
                        <p class="text-xs text-gray-500 mt-1">${new Date(notification.timestamp).toLocaleString()}</p>
                    </div>
                    <div class="ml-2">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            notification.type === 'new_lead' ? 'bg-green-100 text-green-800' :
                            notification.type === 'existing_lead' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                        }">
                            ${notification.type.replace('_', ' ')}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    addNotification(message, type) {
        const notification = {
            id: Date.now(),
            message: message,
            type: type,
            timestamp: new Date().toISOString(),
            read: false
        };
        
        this.notifications.unshift(notification);
        this.renderNotifications();
        this.updateNotificationBadge(this.notifications.filter(n => !n.read).length);
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }

    updateStats() {
        document.getElementById('totalLeads').textContent = this.leads.length;
        document.getElementById('newLeads').textContent = this.leads.filter(l => l.status === 'New Lead').length;
        document.getElementById('existingLeads').textContent = this.leads.filter(l => l.status === 'Existing Lead').length;
        document.getElementById('emailsProcessed').textContent = this.emailsProcessed;
    }

    showLoading(message) {
        document.getElementById('loadingMessage').textContent = message;
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showNotification(message, type) {
        // Create a notification at the top of the screen
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 ${
            type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
        }`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle'} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    clearInputs() {
        document.getElementById('emailBody').value = '';
        document.getElementById('emailOutput').innerHTML = '<p class="text-center text-gray-500">Processed email will appear here...</p>';
    }

    toggleNotifications() {
        // This could open a notification panel or modal
        this.showNotification('Notifications panel would open here', 'info');
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadLeads();
            this.loadNotifications();
        }, 30000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();
});
