# AI Agents - Advanced Email Processing System

An intelligent, multi-provider AI system for email processing and response generation, built with LangChain, FastAPI, and modern web technologies.

## 🚀 Features

### Core Capabilities
- **Multi-AI Provider Support**: OpenAI, Groq (Llama), Google Gemini, Anthropic Claude
- **LangChain Integration**: Advanced agents with tools and prompt engineering
- **Async Processing**: High-performance concurrent email processing
- **Real-time Streaming**: WebSocket-based streaming responses
- **Advanced Caching**: Redis + disk cache with multiple strategies
- **Structured Output**: Pydantic models for consistent JSON responses

### Web Interface
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Updates**: Live processing status and metrics
- **Provider Management**: Health monitoring and provider selection
- **Streaming Support**: Real-time response generation
- **Performance Metrics**: System monitoring and analytics

### Advanced Features
- **Prompt Engineering**: Optimized prompts for better AI responses
- **Agent Orchestration**: Multi-agent workflows for complex tasks
- **Batch Processing**: Concurrent processing of multiple emails
- **Error Handling**: Robust error recovery and fallback mechanisms
- **Security**: JWT authentication and rate limiting

## 🏗️ Architecture

```
AI_AGENTS/
├── main.py                 # Entry point with async workflow
├── web_server.py          # FastAPI server with WebSocket support
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
│
├── config/
│   └── settings.py        # Pydantic-based configuration
│
├── models/
│   └── schemas.py         # Pydantic models for structured data
│
├── agents/
│   ├── ai_provider_manager.py  # Multi-provider AI management
│   └── langchain_agents.py     # LangChain agents with tools
│
├── services/
│   ├── cache_service.py   # Advanced caching (Redis + disk)
│   ├── sheets_service.py  # Google Sheets integration
│   └── file_logger.py     # File-based logging
│
├── utils/
│   ├── email_parser.py    # Email parsing utilities
│   └── logger.py          # Logging configuration
│
├── templates/
│   └── index.html         # Web interface template
│
├── static/
│   └── js/
│       └── app.js         # Frontend JavaScript
│
└── data/
    ├── logs.txt           # Application logs
    └── senders.csv        # CSV data storage
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis (optional, for caching)
- Node.js (for development)

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd AI_AGENTS
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Set up API keys in `.env`:**
   ```env
   # Required: At least one AI provider
   OPENAI_API_KEY=your_openai_key
   GROQ_API_KEY=your_groq_key
   GOOGLE_API_KEY=your_google_key
   ANTHROPIC_API_KEY=your_anthropic_key
   
   # Optional: Google Sheets integration
   GOOGLE_SHEETS_CREDENTIALS=credentials.json
   SHEET_ID=your_sheet_id
   
   # Optional: Redis for caching
   REDIS_URL=redis://localhost:6379
   ```

5. **Start Redis (optional):**
   ```bash
   redis-server
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

7. **Access the web interface:**
   Open http://localhost:8000 in your browser

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `GROQ_API_KEY` | Groq API key | Optional |
| `GOOGLE_API_KEY` | Google API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` |
| `ENABLE_STREAMING` | Enable WebSocket streaming | `true` |

### AI Provider Configuration

Each provider can be configured with:
- Model selection
- Temperature settings
- Max tokens
- Custom parameters

## 📡 API Endpoints

### REST API

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/providers` - List available AI providers
- `GET /api/providers/health` - Provider health status
- `POST /api/process-email` - Process single email
- `POST /api/process-batch` - Process multiple emails
- `GET /api/cache/stats` - Cache statistics
- `DELETE /api/cache/clear` - Clear cache
- `GET /api/metrics` - System metrics

### WebSocket

- `WS /ws` - Real-time communication
  - `process_email` - Process email with streaming
  - `stream_response` - Stream AI responses

## 🤖 AI Providers

### Supported Providers

1. **OpenAI** - GPT models
2. **Groq** - Llama models (fast inference)
3. **Google** - Gemini models
4. **Anthropic** - Claude models

### Provider Selection

The system automatically selects the best available provider or allows manual selection through the web interface.

## 🔄 Async Processing

### Concurrent Email Processing

```python
# Process multiple emails concurrently
emails = [email1, email2, email3]
results = await ai_provider_manager.batch_process_emails(emails)
```

### Streaming Responses

```python
# Stream AI responses in real-time
async for chunk in ai_provider_manager.generate_response_stream(prompt, provider):
    print(chunk.content)
```

## 🎯 LangChain Integration

### Agents with Tools

The system includes specialized agents:

- **Email Processing Agent**: Handles email analysis and response generation
- **Prompt Engineering Agent**: Optimizes prompts for better performance
- **Multi-Agent Orchestrator**: Coordinates multiple agents for complex tasks

### Custom Tools

- **Email Analyzer**: Extracts key information from emails
- **Sender Extractor**: Identifies sender details
- **Response Generator**: Creates contextual replies

## 💾 Caching Strategy

### Multi-Level Caching

1. **Redis Cache**: Fast in-memory caching
2. **Disk Cache**: Persistent local caching
3. **AI Response Caching**: Cached AI responses
4. **Email Result Caching**: Cached processing results

### Cache Management

- Automatic cache invalidation
- TTL-based expiration
- Cache statistics and monitoring
- Manual cache clearing

## 📊 Monitoring & Metrics

### Real-time Metrics

- Active connections
- Cache hit rate
- Average response time
- Error rates
- Memory and CPU usage

### Provider Health

- Individual provider status
- Response time monitoring
- Error tracking
- Automatic failover

## 🔒 Security

### Authentication

- JWT token-based authentication
- Configurable token expiration
- Secure API endpoints

### Rate Limiting

- Per-minute request limits
- Configurable rate limits
- Automatic throttling

## 🚀 Performance

### Optimization Features

- Async/await throughout
- Concurrent processing
- Intelligent caching
- Connection pooling
- Memory management

### Scalability

- Horizontal scaling support
- Load balancing ready
- LangChain caching support

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Test Coverage

- Unit tests for all components
- Integration tests for API endpoints
- WebSocket communication tests
- AI provider integration tests

## 📈 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Considerations

- Use environment-specific configurations
- Set up proper logging
- Configure monitoring
- Set up health checks
- Use production-grade Redis
- Configure load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the API examples

## 🔮 Roadmap

- [ ] Additional AI providers
- [ ] Advanced analytics dashboard
- [ ] Email template management
- [ ] Multi-language support
- [ ] Advanced prompt templates
- [ ] Integration with more email services
- [ ] Machine learning model training
- [ ] Advanced caching strategies