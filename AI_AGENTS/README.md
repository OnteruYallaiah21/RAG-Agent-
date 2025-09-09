# Intelligent System Lead Conversion AI Powered Solutions

An advanced AI-powered contact form processing system that generates dynamic, personalized email responses using LLM integration, CRM management, and intelligent lead conversion workflows.

## 🚀 Features

### Core Capabilities
- **AI-Powered Email Generation**: Dynamic, long, and engaging email responses using Groq LLM
- **Contact Form Processing**: Professional contact submission form with real-time validation
- **CRM Integration**: Automatic lead management and customer status tracking
- **LLM Fallback System**: Robust error handling with fallback responses
- **Real-time Debugging**: Comprehensive console logging for development
- **Loading Effects**: Professional loading spinners during AI processing

### Web Interface
- **Modern Contact Form**: Professional UI with Tailwind CSS
- **Real-time Payload Display**: Shows JSON data being sent to backend
- **AI Response Display**: Structured display of generated email responses
- **Success Notifications**: User-friendly feedback system
- **Responsive Design**: Works on all device sizes
- **Loading Animations**: Smooth loading effects during processing

### AI Agent Pipeline
- **Dynamic Email Generation**: Creates personalized, context-aware responses
- **Lead Status Detection**: Identifies new vs existing customers
- **Structured Output**: Consistent JSON response format
- **Error Recovery**: Graceful fallback when LLM fails
- **Debug Logging**: Complete visibility into processing pipeline

## 🏗️ Project Structure

```
AI_AGENTS/
├── main.py                    # FastAPI server with contact form API
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── start.sh                   # Startup script
│
├── config/
│   └── settings.py            # Application configuration
│
├── agents/
│   ├── ai_provider_manager.py # Multi-provider AI management
│   ├── email_agent.py         # Email processing agent
│   ├── email_workflow.py      # Email workflow orchestration
│   ├── langchain_agents.py    # LangChain agent implementations
│   ├── llm_manager.py         # LLM provider management
│   ├── notification_agent.py  # Notification handling
│   └── validation_agent.py    # Data validation agent
│
├── services/
│   ├── agent_tool_call.py     # AI agent with LLM integration
│   ├── cache_service.py       # Caching service
│   ├── crm_service.py         # CRM management service
│   ├── email_service.py       # Email sending service
│   ├── file_logger.py         # File-based logging service
│   └── sheets_service.py      # Google Sheets integration
│
├── templates/
│   ├── index.html             # Contact form interface
│   ├── dashboard.html         # Dashboard interface
│   └── welcome.html           # Welcome page
│
├── static/
│   └── js/
│       ├── app.js             # Main application JavaScript
│       └── dashboard.js       # Dashboard JavaScript
│
├── utils/
│   ├── checking_email_verification.py # Email verification utilities
│   ├── email_parser.py        # Email parsing utilities
│   ├── logger.py              # Logging configuration
│   └── prompt_builder.py      # Prompt engineering utilities
│
└── data/
    ├── crm/
    │   └── customers.json     # CRM customer database
    ├── existing_leads/        # Existing lead data files
    ├── new_leads/             # New lead data files
    ├── existing_leads.json    # Existing leads summary
    ├── new_leads.json         # New leads summary
    ├── outbox.json            # Email outbox
    ├── senders.csv            # Sender data
    └── logs.txt               # Application logs
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Groq API key (for LLM integration)

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd AI_AGENTS
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

5. **Access the contact form:**
   Open http://localhost:5000 in your browser

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `HOST` | Server host | No (default: 0.0.0.0) |
| `PORT` | Server port | No (default: 5000) |
| `DEBUG` | Debug mode | No (default: false) |

### AI Provider Configuration

The system uses Groq's Llama-3.1-8b-instant model for:
- Dynamic email generation
- Lead status analysis
- Response personalization

## 📡 API Endpoints

### REST API

- `GET /` - Contact form interface
- `POST /api/email/process` - Process contact form submission
- `GET /api/crm/leads` - Get CRM leads data

### Request Format

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "Acme Corp",
  "subject": "Product Demo",
  "message": "I'm interested in your AI solutions",
  "tag": "contact, submission, form, inquiry"
}
```

### Response Format

```json
{
  "status": "processed",
  "name": "John Doe",
  "email": "john@example.com",
  "company": "Acme Corp",
  "subject": "Product Demo",
  "message": "I'm interested in your AI solutions",
  "reply_subject": "Thank you for your Product Demo inquiry - Intelligent System Lead Conversion AI",
  "reply_body": "Hi John!\n\nThank you for contacting Intelligent System Lead Conversion AI...",
  "intent": "contact_submission",
  "customer_type": "new_lead",
  "is_new_lead": true,
  "sent": true,
  "message_id": "agent_response_john_example_com"
}
```

## 🤖 AI Agent Pipeline

### Processing Flow

1. **Contact Form Submission**: User fills out contact form
2. **Payload Validation**: Frontend validates and sends JSON payload
3. **Loading Effect**: Professional loading spinner appears
4. **AI Agent Processing**: 
   - Check if lead exists in CRM
   - Generate personalized email using LLM
   - Create structured response
5. **Response Delivery**: Send AI-generated response to frontend
6. **CRM Update**: Add new leads to customer database

### LLM Integration

The system uses Groq's Llama-3.1-8b-instant model to generate:
- **New Lead Emails**: 4-5 paragraph welcome emails with:
  - Enthusiastic greeting
  - Intelligent System Lead Conversion AI capabilities overview
  - Specific value propositions
  - Next steps and call-to-action
  - Professional closing

- **Existing Customer Emails**: 3-4 paragraph acknowledgment emails with:
  - Warm appreciation
  - Personalized inquiry acknowledgment
  - Valuable insights
  - Clear next steps

## 🔄 Contact Form Features

### Form Fields
- **Full Name**: Customer's complete name
- **Email**: Valid email address
- **Company**: Company name (optional)
- **Subject**: Dropdown with predefined options:
  - Product Demo
  - Support Request
  - Partnership
  - Pricing
  - General Inquiry
- **Message**: Detailed inquiry text

### Real-time Features
- **Payload Display**: Shows JSON data being sent
- **Loading Animation**: Professional spinner during processing
- **AI Response**: Displays generated email content
- **Success Notification**: Confirms form submission
- **Error Handling**: Graceful fallback responses

## 💾 CRM Integration

### Lead Management
- **Automatic Detection**: Identifies new vs existing customers
- **Data Storage**: JSON-based customer database
- **Lead Tracking**: Monitors customer interactions
- **Status Updates**: Tracks lead progression
- **File Organization**: Separate directories for new and existing leads

### Data Structure
```json
{
  "name": "Customer Name",
  "email": "customer@example.com",
  "company": "Company Name",
  "status": "new_lead",
  "created_at": "2024-01-01T00:00:00Z",
  "last_contact": "2024-01-01T00:00:00Z"
}
```

## 🚀 Performance

### Optimization Features
- **Async Processing**: Non-blocking email generation
- **LLM Caching**: Intelligent response caching
- **Error Recovery**: Robust fallback mechanisms
- **Debug Logging**: Comprehensive development insights
- **Loading Effects**: Professional user experience

### Scalability
- **Stateless Design**: Easy horizontal scaling
- **JSON Storage**: Lightweight data persistence
- **Modular Architecture**: Easy feature additions
- **Service Separation**: Independent service components

## 🧪 Testing


### Manual Testing
1. **Start the application**: `python run.py`
2. **Open browser**: Navigate to http://localhost:5000
3. **Fill contact form**: Submit with test data
4. **Check console**: Verify debug output
5. **Review response**: Confirm AI-generated email

### Debug Output
The system provides comprehensive logging:
```
JSON PAYLOAD RECEIVED FROM FRONTEND
CALLING AI AGENT...
AI AGENT STARTED - Processing: [Name] ([email])
Lead Status: New Lead
CALLING LLM FOR EMAIL GENERATION...
GENERATED EMAIL CONTENT:
AI AGENT COMPLETED
AI AGENT RESPONSE SENT TO FRONTEND
```

## 📈 Deployment

### Production Setup
1. **Environment Configuration**: Set production environment variables
2. **API Key Security**: Secure storage of Groq API key
3. **Logging**: Configure production logging levels
4. **Monitoring**: Set up health checks and metrics

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the debug console output
- Review the API documentation

## 🔮 Roadmap

- [ ] Additional LLM providers (OpenAI, Claude)
- [ ] Email template management
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Email scheduling
- [ ] Advanced CRM features
- [ ] Integration with email services
- [ ] Machine learning enhancements

---

**Developer**: Yallaiah Onteru  
**Contact**: yonteru414@gmail.com  
**GitHub**: https://yonteru414.github.io/Yallaiah-AI-ML-Engineer/  
**Support**: yonteru.ai.engineer@gmail.com
