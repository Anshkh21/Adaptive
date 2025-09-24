# Python Backend - Adaptive Assessment Platform

This is the Python implementation of the Adaptive Assessment Platform, built with FastAPI and designed to work alongside the existing Node.js backend for performance comparison.

## 🚀 Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **MongoDB Integration**: Using Motor (async MongoDB driver) and Beanie ODM
- **JWT Authentication**: Secure token-based authentication
- **AI Integration**: Enhanced Gemini AI service for question generation
- **Type Safety**: Full type hints with Pydantic models
- **Async Support**: Fully asynchronous for better performance

## 📁 Project Structure

```
python-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   ├── assessment.py
│   │   ├── question.py
│   │   └── aptitude_test.py
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   ├── assessments.py
│   │   ├── users.py
│   │   ├── analytics.py
│   │   ├── questions.py
│   │   └── aptitude.py
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── ai/                  # AI services
│       └── gemini_service.py
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── run.py                  # Startup script
└── README.md               # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- MongoDB
- pip or pipenv

### Setup

1. **Clone and navigate to the Python backend:**
   ```bash
   cd python-backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Configure environment variables:**
   ```env
   MONGODB_URI=mongodb://localhost:27017/adaptive_assessment
   JWT_SECRET=your-super-secret-jwt-key-here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Running the Server

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The server will start on `http://localhost:8001`

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/adaptive_assessment` |
| `JWT_SECRET` | Secret key for JWT tokens | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional (fallback mode) |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8001` |
| `DEBUG` | Debug mode | `True` |

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🔄 Comparison with Node.js Backend

### Advantages of Python Implementation

1. **Better AI Integration**: Native Gemini SDK with better error handling
2. **Type Safety**: Full type hints and Pydantic validation
3. **Cleaner Code**: More readable and maintainable
4. **Better Testing**: Comprehensive testing frameworks
5. **Scientific Computing**: Easy integration with ML libraries
6. **Async Performance**: Better async/await implementation

### Performance Comparison

| Feature | Node.js | Python |
|---------|---------|--------|
| Startup Time | Fast | Moderate |
| Memory Usage | Lower | Higher |
| AI Integration | Basic | Advanced |
| Type Safety | Partial | Full |
| Code Readability | Good | Excellent |
| Testing | Good | Excellent |

## 🚀 Deployment

### Docker (Recommended)
```bash
# Build image
docker build -t adaptive-assessment-python .

# Run container
docker run -p 8001:8001 adaptive-assessment-python
```

### Traditional Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of the Adaptive Assessment Platform.

## 🔗 Related

- [Node.js Backend](../README.md) - Original implementation
- [React Frontend](../client/README.md) - Frontend application
