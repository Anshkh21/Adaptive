# Adaptive Assessment Platform - Python Backend

A comprehensive web-based adaptive multiple-choice question (MCQ) testing system built with Python FastAPI backend and React frontend. The system delivers MCQ assessments over the internet and adapts questions based on user performance and abilities using advanced AI algorithms.

## 🚀 Features

### Core Assessment Features
- **Pre-Assessment Module**: Baseline knowledge evaluation to gauge user's initial proficiency
- **Adaptive Assessment**: Real-time question adaptation based on performance using Item Response Theory (IRT)
- **Final Assessment**: Comprehensive evaluation covering all learning objectives
- **AI-Powered Question Generation**: Intelligent question creation using Google Gemini Pro
- **Psychometric Analysis**: Advanced statistical analysis of question effectiveness and student performance
- **Aptitude Tests**: CAT-level difficulty aptitude tests with section-wise scoring

### User Management
- **Multi-Role System**: Student, Instructor, and Admin roles with appropriate permissions
- **User Authentication**: Secure JWT-based authentication system
- **Profile Management**: Comprehensive user profiles with learning preferences
- **Performance Tracking**: Detailed analytics and progress monitoring

### Adaptive Algorithm
- **Item Response Theory (IRT)**: Sophisticated ability estimation using IRT models
- **Maximum Information Criterion**: Optimal question selection for accurate ability measurement
- **Real-time Adaptation**: Dynamic difficulty adjustment based on performance
- **Termination Criteria**: Intelligent assessment completion based on confidence levels

### Analytics & Reporting
- **Performance Analytics**: Detailed insights into student performance patterns
- **Question Effectiveness**: Analysis of question quality and effectiveness
- **Adaptive Assessment Analytics**: Monitoring of adaptation success rates
- **Institutional Reporting**: Comprehensive reports for educational institutions

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **RESTful API**: Comprehensive API endpoints for all system functionality
- **MongoDB Database**: Scalable NoSQL database with Beanie ODM
- **JWT Authentication**: Secure token-based authentication
- **AI Integration**: Google Gemini Pro for intelligent question generation
- **Async Support**: High-performance asynchronous operations

### Frontend (React + TypeScript)
- **Modern React**: Built with React 18 and TypeScript for type safety
- **Material-UI**: Professional UI components with consistent design
- **State Management**: React Query for efficient data fetching and caching
- **Responsive Design**: Mobile-first approach with adaptive layouts

### Database Schema
- **Users**: Comprehensive user profiles with role-based access
- **Questions**: Rich question metadata with psychometric properties
- **Assessments**: Detailed assessment tracking with adaptive data
- **Aptitude Tests**: CAT-level aptitude tests with section-wise configuration
- **Performance Analytics**: Extensive performance and analytics data

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (v4.4 or higher)
- Google Gemini API Key (for AI question generation)
- Node.js (for frontend development)
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Aicte
```

### 2. Setup Python Backend
```bash
cd python-backend
pip install -r requirements.txt
```

### 3. Setup Frontend
```bash
cd client
npm install
cd ..
```

### 4. Environment Configuration
Create a `config.env` file in the `python-backend` directory:
```env
# Database Configuration
MONGODB_URI=mongodb://localhost:27017/adaptive_assessment

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here-change-this-in-production

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000
```

Create a `.env` file in the client directory:
```env
REACT_APP_API_URL=http://localhost:8001/api
REACT_APP_SOCKET_URL=http://localhost:8001
```

### 5. Start MongoDB
Make sure MongoDB is running on your system:
```bash
# On Windows
net start MongoDB

# On macOS/Linux
sudo systemctl start mongod
```

## 🚀 Running the Application

### Development Mode

1. **Start the Python Backend Server**:
```bash
cd python-backend
python run.py
```

2. **Start the Frontend Development Server** (in a new terminal):
```bash
cd client
npm start
```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api
   - API Documentation: http://localhost:8001/docs

### Production Mode

1. **Build the Frontend**:
```bash
cd client
npm run build
```

2. **Start the Production Server**:
```bash
cd python-backend
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `PUT /api/auth/change-password` - Change password

### Assessment Endpoints
- `POST /api/assessments/create` - Create new assessment
- `POST /api/assessments/{id}/start` - Start assessment
- `POST /api/assessments/{id}/answer` - Submit answer
- `GET /api/assessments/{id}/results` - Get assessment results
- `GET /api/assessments/history` - Get user's assessment history

### Aptitude Test Endpoints
- `GET /api/aptitude` - Get available aptitude tests
- `GET /api/aptitude/{test_id}` - Get specific aptitude test
- `POST /api/aptitude/{test_id}/start` - Start aptitude test
- `POST /api/aptitude/{test_id}/complete` - Complete aptitude test

### Question Management Endpoints
- `GET /api/questions` - Get questions with filtering
- `POST /api/questions` - Create new question
- `POST /api/questions/generate` - Generate AI question
- `PUT /api/questions/{id}` - Update question

### Analytics Endpoints
- `GET /api/analytics/performance` - User performance analytics
- `GET /api/analytics/assessments` - Assessment analytics
- `GET /api/analytics/questions` - Question analytics

### Admin Endpoints
- `GET /api/admin/dashboard` - Admin dashboard data
- `GET /api/admin/users` - User management
- `PUT /api/admin/users/{id}/status` - Update user status
- `GET /api/admin/questions/pending` - Pending questions for review

### Assignment Endpoints
- `GET /api/assignments/my-students` - Get assigned students (instructor)
- `GET /api/assignments/student/{id}/performance` - Get student performance
- `POST /api/assignments/assign-student` - Assign student to instructor
- `GET /api/assignments/batch-performance` - Get batch performance

## 🎯 Usage Guide

### For Students
1. **Registration**: Create an account with your institutional details
2. **Pre-Assessment**: Take the baseline assessment to establish your knowledge level
3. **Adaptive Assessment**: Engage with AI-powered adaptive testing
4. **Aptitude Tests**: Take CAT-level aptitude tests with section-wise scoring
5. **Progress Tracking**: Monitor your performance and improvement over time
6. **Analytics**: View detailed performance analytics and recommendations

### For Instructors
1. **Question Creation**: Create and manage question banks
2. **AI Question Generation**: Use AI to generate high-quality questions
3. **Assessment Monitoring**: Track student progress and performance
4. **Student Management**: Manage assigned students and their performance
5. **Analytics**: Access comprehensive analytics for your students

### For Administrators
1. **User Management**: Manage user accounts and permissions
2. **Question Review**: Review and approve AI-generated questions
3. **System Analytics**: Monitor overall system performance
4. **Institutional Reports**: Generate reports for educational institutions

## 🔧 Configuration

### Assessment Configuration
- **Pre-Assessment Questions**: Default 20 questions (configurable)
- **Final Assessment Questions**: Default 50 questions (configurable)
- **Time Limits**: Configurable per assessment type
- **Adaptive Parameters**: IRT model parameters can be adjusted

### AI Question Generation
- **Google Gemini Integration**: Uses Gemini Pro for question generation
- **Quality Validation**: Built-in quality checks for generated questions
- **Batch Generation**: Support for generating multiple questions at once
- **Customization**: Configurable prompts and parameters

### Aptitude Tests
- **CAT-Level Difficulty**: Advanced quantitative, logical, and verbal reasoning
- **Section-wise Scoring**: Separate scoring for different sections
- **Time Management**: Configurable time limits per section
- **Multiple Attempts**: Support for retaking tests with limitations

## 🧪 Testing

### Backend Testing
```bash
cd python-backend
pytest
```

### Frontend Testing
```bash
cd client
npm test
```

## 📊 Performance Monitoring

The system includes comprehensive performance monitoring:
- **Database Performance**: MongoDB query optimization and indexing
- **API Response Times**: Monitoring of API endpoint performance
- **Adaptive Algorithm Efficiency**: Tracking of adaptation success rates
- **User Experience Metrics**: Frontend performance monitoring

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions system
- **Rate Limiting**: Protection against abuse and DDoS attacks
- **Input Validation**: Comprehensive input sanitization and validation
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Password Hashing**: Secure password storage with bcrypt

## 🚀 Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t adaptive-assessment-platform .

# Run with Docker Compose
docker-compose up -d
```

### Cloud Deployment
The system is designed to be deployed on various cloud platforms:
- **AWS**: EC2, RDS, S3 integration
- **Google Cloud**: Compute Engine, Cloud SQL
- **Azure**: Virtual Machines, Azure Database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- **Email**: support@adaptive-assessment.org
- **Documentation**: [Project Wiki](wiki-url)
- **Issues**: [GitHub Issues](issues-url)

## 🙏 Acknowledgments

- **Google Gemini**: For AI question generation capabilities
- **MongoDB**: For robust database solutions
- **React Team**: For the excellent frontend framework
- **FastAPI Team**: For the high-performance Python web framework

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Core adaptive assessment system
- ✅ AI question generation
- ✅ User management and authentication
- ✅ Aptitude tests with CAT-level difficulty
- ✅ Basic analytics and reporting

### Phase 2 (Upcoming)
- 🔄 Advanced analytics dashboard
- 🔄 Mobile application
- 🔄 Offline assessment capabilities
- 🔄 Integration with LMS systems

### Phase 3 (Future)
- 📋 Machine learning model improvements
- 📋 Advanced psychometric analysis
- 📋 Multi-language support
- 📋 Advanced reporting and visualization

---

**Built with ❤️ for Adaptive Assessment Platform**