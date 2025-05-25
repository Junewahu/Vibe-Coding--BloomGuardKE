# BloomGuard - Modular Health Platform

BloomGuard is a modular, human-centred B2B healthtech platform targeting paediatric clinics and private doctors in Kenya. It automates follow-up reminders for vaccinations and developmental milestones through WhatsApp, SMS, USSD, and voice. The system enhances clinic efficiency, caregiver engagement, and child health outcomes while supporting offline functionality, multilingual delivery, tiered monetisation, and integration with national systems like NHIF.

## Features

### Core Modules

1. **Patient Registration & Profiling**
   - Manual entry and bulk import
   - Demographics and contact tracking
   - Caregiver linking
   - Medical history management
   - Biometric ID integration
   - Photo capture for patient cards

2. **Follow-Up Scheduling Engine**
   - Rule-based scheduling
   - Immunisation tracking
   - Milestone monitoring
   - Post-operative visit management
   - Chronic care scheduling
   - Drag-and-drop calendar interface

3. **Reminder Dispatch Hub**
   - Multi-channel delivery (SMS, WhatsApp, Voice, USSD)
   - Customisable message templates
   - Intelligent retry system
   - Multilingual support
   - SIM health monitoring

4. **Response Tracking & Confirmation**
   - Two-way communication
   - Appointment confirmation
   - Rescheduling interface
   - Non-responder flagging
   - FAQ chatbot

5. **Doctor & Staff Dashboard**
   - Real-time patient tracking
   - Appointment management
   - Workload forecasting
   - Analytics integration
   - AI risk scoring

6. **Offline Sync & Backup**
   - Android app support
   - Data caching
   - Sync queue management
   - Manual override options
   - Peer-to-peer sync

7. **Caregiver Engagement Interface**
   - WhatsApp broadcasts
   - Voice notes
   - Printable visit cards
   - Q&A system
   - Digital vaccination certificates

8. **CHW Field Tracker**
   - Visit assignment
   - Offline data entry
   - GPS tagging
   - Incentive tracking
   - Supervisor review

9. **Incentives & Adherence Module**
   - Visit-based rewards
   - Medication adherence tracking
   - Milestone completion rewards
   - Mobile money integration

10. **Modular API Gateway**
    - EMR integration
    - NHIF connection
    - Mobile money support
    - Public health reporting
    - Developer sandbox

## Technical Architecture

### Frontend Layer
- React/Vue.js web interface
- React Native mobile app
- Offline-first design
- Background sync
- Role-based UI

### Backend Layer
- FastAPI microservices
- PostgreSQL database
- Redis caching
- Docker containers
- RESTful APIs

### Data Layer
- PostgreSQL for primary storage
- Redis for caching
- S3 for media storage
- Local SQLite for offline

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bloomguard.git
cd bloomguard
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the development server:
```bash
uvicorn backend.main:app --reload
```

### Development

1. Run tests:
```bash
pytest
```

2. Format code:
```bash
black .
isort .
```

3. Type checking:
```bash
mypy .
```

4. Linting:
```bash
flake8
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
1. Set up PostgreSQL
2. Configure environment variables
3. Run migrations
4. Start the server with gunicorn

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@bloomguard.ke or join our Slack channel.

## Acknowledgments

- Ministry of Health, Kenya
- NHIF
- Africa's Talking
- Twilio
- OpenMRS 