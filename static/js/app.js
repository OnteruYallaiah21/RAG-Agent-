/**
 * AI Agents Web Application - Frontend JavaScript
 * Handles API calls and real-time updates
 */

class AIAgentsApp {
    constructor() {
        this.processedCount = 0;
        this.availableModels = [];
        
        this.initializeApp();
    }

    initializeApp() {
        this.setupEventListeners();
        this.loadAvailableModels();
        this.updateStats();
    }

    setupEventListeners() {
        // Process button
        document.getElementById('processBtn').addEventListener('click', () => {
            this.processEmail();
        });

        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearInputs();
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Settings button
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showSettings();
        });
    }

    async processEmail() {
        const emailContent = document.getElementById('emailContent').value.trim();
        const provider = document.getElementById('providerSelect').value;

        if (!emailContent) {
            this.showError('Please enter email content');
            return;
        }

        try {
            this.showLoading('Processing email...');
            await this.processEmailAPI(emailContent, provider);
        } catch (error) {
            this.showError(`Error processing email: ${error.message}`);
        }
    }

    async processEmailAPI(emailContent, provider) {
        try {
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
                this.displayWorkflowResults(result);
                this.processedCount++;
                this.updateStats();
                this.showSuccess(`Email processed successfully! Intent: ${result.intent}`);
            } else {
                this.showError(result.error || 'Processing failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showError(`API Error: ${error.message}`);
        }
    }

    displayWorkflowResults(result) {
        // Display AI response
        const responseContent = document.getElementById('responseContent');
        responseContent.innerHTML = `
            <div class="space-y-4">
                <div class="bg-white p-4 rounded-md border">
                    <h4 class="font-semibold text-gray-900 mb-2">Generated Reply</h4>
                    <div class="mb-3">
                        <span class="font-medium text-gray-600">Subject:</span>
                        <p class="text-gray-700">${this.escapeHtml(result.reply_subject)}</p>
                    </div>
                    <div>
                        <span class="font-medium text-gray-600">Body:</span>
                        <p class="text-gray-700 mt-1">${this.escapeHtml(result.reply_body)}</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="font-medium text-gray-600">To:</span>
                        <span class="ml-2 text-gray-900">${result.to}</span>
                    </div>
                    <div>
                        <span class="font-medium text-gray-600">Intent:</span>
                        <span class="ml-2 text-blue-600 capitalize">${result.intent}</span>
                    </div>
                    <div>
                        <span class="font-medium text-gray-600">Customer Type:</span>
                        <span class="ml-2 text-gray-900">${result.customer_type || 'Unknown'}</span>
                    </div>
                    <div>
                        <span class="font-medium text-gray-600">Lead Status:</span>
                        <span class="ml-2 ${result.is_new_lead ? 'text-green-600' : 'text-blue-600'}">${result.is_new_lead ? 'New Lead' : 'Existing Customer'}</span>
                    </div>
                </div>
            </div>
        `;

        // Display analysis
        const analysisContent = document.getElementById('analysisContent');
        analysisContent.innerHTML = `
            <div class="space-y-4">
                <div class="bg-white p-4 rounded-md border">
                    <h4 class="font-semibold text-gray-900 mb-2">Email Analysis</h4>
                    <div class="text-sm text-gray-700 space-y-2">
                        <p><strong>Intent:</strong> <span class="capitalize text-blue-600">${result.intent}</span></p>
                        <p><strong>Customer Type:</strong> ${result.customer_type || 'Unknown'}</p>
                        <p><strong>User ID:</strong> ${result.user_id || 'N/A'}</p>
                        <p><strong>Lead Status:</strong> <span class="${result.is_new_lead ? 'text-green-600' : 'text-blue-600'}">${result.is_new_lead ? 'New Lead' : 'Existing Customer'}</span></p>
                        <p><strong>Processed At:</strong> ${new Date(result.processed_at).toLocaleString()}</p>
                        <p><strong>Log File:</strong> ${result.log_file ? 'Saved' : 'Not saved'}</p>
                    </div>
                </div>
            </div>
        `;

        // Display metrics
        const metricsContent = document.getElementById('metricsContent');
        metricsContent.innerHTML = `
            <div class="space-y-4">
                <div class="bg-white p-4 rounded-md border">
                    <h4 class="font-semibold text-gray-900 mb-2">Workflow Metrics</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium text-gray-600">Total Processed:</span>
                            <span class="ml-2 text-gray-900">${this.processedCount}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Status:</span>
                            <span class="ml-2 text-green-600">${result.status}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Available Models:</span>
                            <span class="ml-2 text-gray-900">${this.availableModels.length}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Data Storage:</span>
                            <span class="ml-2 text-gray-900">${result.is_new_lead ? 'New Leads' : 'Existing Leads'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    displayResults(result) {
        // Display AI response
        const responseContent = document.getElementById('responseContent');
        if (result.reply) {
            responseContent.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-md border">
                        <h4 class="font-semibold text-gray-900 mb-2">Generated Response</h4>
                        <p class="text-gray-700">${this.escapeHtml(result.reply)}</p>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium text-gray-600">Sender:</span>
                            <span class="ml-2 text-gray-900">${result.sender_name || 'Unknown'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Status:</span>
                            <span class="ml-2 text-green-600">Success</span>
                        </div>
                    </div>
                </div>
            `;
        }

        // Display analysis
        const analysisContent = document.getElementById('analysisContent');
        analysisContent.innerHTML = `
            <div class="space-y-4">
                <div class="bg-white p-4 rounded-md border">
                    <h4 class="font-semibold text-gray-900 mb-2">Email Analysis</h4>
                    <div class="text-sm text-gray-700">
                        <p><strong>Sender Name:</strong> ${result.sender_name || 'Not detected'}</p>
                        <p><strong>Content Length:</strong> ${emailContent.length} characters</p>
                        <p><strong>Processing Status:</strong> Completed successfully</p>
                    </div>
                </div>
            </div>
        `;

        // Display metrics
        const metricsContent = document.getElementById('metricsContent');
        metricsContent.innerHTML = `
            <div class="space-y-4">
                <div class="bg-white p-4 rounded-md border">
                    <h4 class="font-semibold text-gray-900 mb-2">Performance Metrics</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium text-gray-600">Total Processed:</span>
                            <span class="ml-2 text-gray-900">${this.processedCount}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Status:</span>
                            <span class="ml-2 text-green-600">Success</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Available Models:</span>
                            <span class="ml-2 text-gray-900">${this.availableModels.length}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600">Cache:</span>
                            <span class="ml-2 text-gray-900">LangChain InMemory</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'text-blue-600');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        
        const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
        activeBtn.classList.add('active', 'border-blue-500', 'text-blue-600');
        activeBtn.classList.remove('border-transparent', 'text-gray-500');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        document.getElementById(`${tabName}Tab`).classList.remove('hidden');
    }

    async loadAvailableModels() {
        try {
            const response = await fetch('/api/models');
            const result = await response.json();
            
            if (result.success) {
                this.availableModels = result.models;
                this.updateProviderSelect();
                this.displayProviderStatus();
            }
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    updateProviderSelect() {
        const select = document.getElementById('providerSelect');
        select.innerHTML = '';
        
        this.availableModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model.charAt(0).toUpperCase() + model.slice(1);
            select.appendChild(option);
        });
    }

    displayProviderStatus() {
        const statusContainer = document.getElementById('providerStatus');
        statusContainer.innerHTML = '';
        
        this.availableModels.forEach(model => {
            const card = document.createElement('div');
            card.className = 'bg-gray-50 rounded-lg p-4';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-semibold text-gray-900 capitalize">${model}</h4>
                        <p class="text-sm text-gray-600">Available</p>
                    </div>
                    <div class="text-right">
                        <span class="status-indicator status-healthy"></span>
                        <p class="text-xs text-gray-500">Ready</p>
                    </div>
                </div>
            `;
            statusContainer.appendChild(card);
        });
    }

    updateStats() {
        document.getElementById('processedCount').textContent = this.processedCount;
        document.getElementById('cacheHitRate').textContent = 'LangChain';
        document.getElementById('avgResponseTime').textContent = 'Fast';
        document.getElementById('activeConnections').textContent = this.availableModels.length;
    }

    showLoading(message) {
        document.getElementById('loadingMessage').textContent = message;
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showError(message) {
        // Create a notification at the top of the screen
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        // Create a success notification at the top of the screen
        this.showNotification(message, 'success');
    }

    showNotification(message, type) {
        // Remove existing notifications
        const existingNotification = document.getElementById('notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.id = 'notification';
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
        document.getElementById('emailContent').value = '';
        document.getElementById('responseContent').innerHTML = '<p class="text-center">Process an email to see the AI response here...</p>';
        document.getElementById('analysisContent').innerHTML = '<p class="text-center">Analysis results will appear here...</p>';
        document.getElementById('metricsContent').innerHTML = '<p class="text-center">Performance metrics will appear here...</p>';
    }

    showSettings() {
        // Simple settings modal
        const settings = `
Available Models: ${this.availableModels.join(', ')}
Processed Emails: ${this.processedCount}
Cache: LangChain InMemory
        `;
        alert(settings);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AIAgentsApp();
});
