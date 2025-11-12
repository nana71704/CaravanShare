# Caravan Rental System

## Overview
This is a Python-based caravan (RV/camper) rental/sharing platform that demonstrates clean architecture principles and various software design patterns. The system allows hosts to list their caravans and guests to search, book, and review them.

**Current State**: Fully functional demo application with in-memory data storage

## Recent Changes
- **2025-11-12**: Initial Replit setup completed
  - Created main.py demo application
  - Configured Python 3.12 environment
  - Set up workflow for running the demo
  - Added .gitignore for Python projects

## Project Structure

```
.
├── src/
│   ├── models/           # Data models (User, Caravan, Reservation, Payment, Review)
│   ├── repositories/     # Repository pattern implementations (in-memory storage)
│   ├── services/         # Business logic services
│   │   ├── caravan_service.py
│   │   ├── user_service.py
│   │   ├── reservation_service.py
│   │   ├── payment_service.py
│   │   ├── review_service.py
│   │   ├── validators.py     # Input validation
│   │   ├── strategies.py     # Pricing strategies
│   │   ├── factories.py      # Object factories
│   │   └── observers.py      # Notification system
│   ├── exceptions/       # Custom exception classes
│   └── constants.py      # Application constants
├── tests/                # Unit tests using pytest
├── main.py              # Demo application entry point
└── replit.md            # This file
```

## Features

### User Management
- User registration with roles (Host/Guest)
- Username validation
- Trust score tracking

### Caravan Management
- Hosts can register caravans with capacity and amenities
- Caravan search by minimum capacity
- Status tracking (Available, Reserved, Maintenance)

### Reservation System
- Guests can create reservations
- Date validation and conflict detection
- Automatic pricing with discount strategies:
  - **Long-stay discount**: 10% off for 7+ days
  - **No discount**: For shorter stays
- Reservation status workflow: Pending → Confirmed → Completed

### Payment Processing
- Payment creation and tracking
- Payment status management
- Integration with reservation workflow

### Review System
- Guests can leave reviews after completed reservations
- Rating system (1-5 stars)
- One review per reservation

### Notifications
- Observer pattern for real-time notifications
- Alerts for guests and hosts on key events

## Design Patterns Used

1. **Repository Pattern**: Abstracts data access layer, currently using in-memory storage but easily switchable to database
2. **Strategy Pattern**: Flexible pricing calculations with different discount strategies
3. **Observer Pattern**: Notification system for user alerts
4. **Factory Pattern**: Consistent object creation for reservations
5. **Dependency Injection**: Loose coupling between services and repositories

## Technology Stack

- **Language**: Python 3.12
- **Testing**: pytest (tests available in `tests/` directory)
- **Data Storage**: In-memory (can be extended to PostgreSQL or other databases)
- **Design**: Clean architecture with separation of concerns

## Running the Application

### Demo Application
The main.py file contains a comprehensive demo that showcases all features:

```bash
python main.py
```

The demo will:
1. Register users (host and guest)
2. Register caravans
3. Search for available caravans
4. Create reservations (both long-term with discount and short-term)
5. Process payments
6. Leave reviews
7. Display system summary

### Running Tests
```bash
pytest tests/
```

Available test files:
- `test_user_service.py` - User registration tests
- `test_caravan_service.py` - Caravan registration tests
- `test_reservation_service.py` - Reservation creation tests
- `test_payment_service.py` - Payment processing tests
- `test_review_service.py` - Review system tests
- `test_validators.py` - Validation logic tests

## Development Notes

### Adding a New Feature
1. Create model in `src/models/` if needed
2. Define repository interface in `src/repositories/base.py`
3. Implement repository in `src/repositories/memory_repository.py`
4. Create service in `src/services/`
5. Add tests in `tests/`

### Extending to Use a Database
The repository pattern makes it easy to switch to a real database:
1. Create new repository implementations (e.g., `PostgresReservationRepository`)
2. Replace in-memory repositories in the application initialization
3. No changes needed to services or business logic

### Current Limitations
- Uses in-memory storage (data is lost on restart)
- No web API (command-line demo only)
- No authentication/authorization
- Payment processing is simulated

## Future Enhancement Ideas
- Add REST API using Flask or FastAPI
- Implement persistent storage with PostgreSQL
- Add user authentication and JWT tokens
- Implement real payment gateway integration
- Add email/SMS notifications
- Create web frontend
- Add admin dashboard
- Implement booking calendar
- Add image uploads for caravans
- Multi-currency support

## Korean Comments
Note: The codebase contains Korean comments (한글) as this project appears to have been originally developed in a Korean-speaking environment. The comments provide context for educational purposes about design patterns and clean architecture principles.

## License
Not specified
