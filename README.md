# Railway Intelligent Decision Support System (RIDSS)

## Overview

An intelligent decision-support system designed for Indian Railway Department section controllers to make optimized, real-time decisions for train precedence and crossings. The system leverages AI, operations research, and modern web technologies to provide conflict-free scheduling and operational optimization.

## Features

### Core Capabilities
- **AI-Powered Optimization**: Advanced algorithms for train precedence and crossing decisions
- **Real-time Scheduling**: Dynamic conflict-free schedule generation with rapid re-optimization
- **Operations Research**: Mathematical optimization models for maximum throughput and minimum delays
- **What-if Simulation**: Scenario analysis for alternative routings and strategies
- **Performance Analytics**: Comprehensive KPIs and dashboards for continuous improvement

### Integration & Security
- **API Integration**: Secure connections with TMS, signaling systems, and timetables
- **Audit Trails**: Complete logging and tracking of all decisions and changes
- **User Management**: Role-based access control for different controller levels
- **Real-time Updates**: WebSocket-based live data streaming

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI/ML Engine  │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (TensorFlow)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   External APIs │
                       │   (TMS/Signals) │
                       └─────────────────┘
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd SIH-Sprit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ridss
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
TMS_API_URL=https://api.tms.indianrailways.gov.in
SIGNALING_API_URL=https://api.signaling.indianrailways.gov.in
API_KEY=your-api-key

# AI/ML Configuration
MODEL_PATH=./models/
OPTIMIZATION_TIMEOUT=30
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Train Management
- `GET /api/v1/trains/` - List all trains in section
- `POST /api/v1/trains/optimize` - Generate optimized schedule
- `PUT /api/v1/trains/{train_id}/priority` - Update train priority

#### Decision Support
- `POST /api/v1/decisions/precedence` - Get precedence recommendations
- `POST /api/v1/decisions/crossing` - Optimize crossing decisions
- `POST /api/v1/simulation/what-if` - Run scenario analysis

#### Analytics
- `GET /api/v1/analytics/kpis` - Get performance KPIs
- `GET /api/v1/analytics/dashboard` - Dashboard data
- `GET /api/v1/audit/trail` - Audit trail logs

## Usage

### For Section Controllers

1. **Login**: Access the system with your credentials
2. **Monitor**: View real-time train positions and schedules
3. **Optimize**: Use AI recommendations for precedence decisions
4. **Simulate**: Test different scenarios before implementation
5. **Track**: Monitor performance metrics and KPIs

### Key Workflows

#### Train Precedence Decision
1. System detects potential conflict
2. AI analyzes priorities, constraints, and operational rules
3. Recommendations presented to controller
4. Controller reviews and approves/modifies decision
5. System implements and monitors outcome

#### Emergency Re-optimization
1. Disruption detected (delay, incident, weather)
2. System triggers rapid re-optimization
3. Alternative schedules generated and evaluated
4. Best solution presented with impact analysis
5. Implementation with real-time monitoring

## Performance Metrics

### Key Performance Indicators (KPIs)
- **Punctuality Rate**: Percentage of on-time arrivals
- **Average Delay**: Mean delay across all trains
- **Section Throughput**: Trains processed per hour
- **Resource Utilization**: Track and platform usage efficiency
- **Conflict Resolution Time**: Speed of decision-making

### Benchmarks
- Target punctuality: >95%
- Average delay: <5 minutes
- Decision time: <30 seconds
- System availability: >99.9%

## Development

### Project Structure
```
SIH-Sprit/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Core configuration
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── ai/               # AI/ML modules
│   └── utils/            # Utilities
├── frontend/
│   ├── src/
│   ├── components/
│   └── pages/
├── tests/
├── docs/
└── deployment/
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend && npm test

# Run integration tests
pytest tests/integration/
```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Considerations
- Use HTTPS for all communications
- Implement proper backup strategies
- Set up monitoring and alerting
- Configure load balancing for high availability
- Regular security audits and updates

## Support

For technical support or questions:
- Email: support@ridss.indianrailways.gov.in
- Documentation: [Internal Wiki]
- Issue Tracker: [Internal System]

## License

This project is proprietary software developed for Indian Railway Department.
Unauthorized distribution or modification is prohibited.

---

**Version**: 1.0.0  
**Last Updated**: September 2024  
**Developed by**: Railway Innovation Team
