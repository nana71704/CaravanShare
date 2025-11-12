#!/usr/bin/env python3
"""
Caravan Rental System Demo
A demonstration of the caravan sharing/rental platform
"""

from datetime import date, timedelta
from src.models.user import User
from src.models.caravan import Caravan
from src.models.common import UserRole, ReservationStatus
from src.models.payment import PaymentStatus
from src.repositories.memory_repository import (
    InMemoryReservationRepository,
    InMemoryPaymentRepository,
    InMemoryReviewRepository,
    InMemoryCaravanRepository,
    InMemoryUserRepository
)
from src.services.validators import ReservationValidator
from src.services.factories import ReservationFactory
from src.services.strategies import PriceCalculator, NoDiscountStrategy
from src.services.observers import NotificationService
from src.services.reservation_service import ReservationService
from src.services.payment_service import PaymentService
from src.services.review_service import ReviewService
from src.services.caravan_service import CaravanService
from src.services.user_service import UserService


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")


def main():
    """Main demo application"""
    print_header("🚐 CARAVAN RENTAL SYSTEM DEMO 🚐")
    
    # Initialize repositories (in-memory storage)
    print_section("Initializing System")
    reservation_repo = InMemoryReservationRepository()
    payment_repo = InMemoryPaymentRepository()
    review_repo = InMemoryReviewRepository()
    caravan_repo = InMemoryCaravanRepository()
    user_repo = InMemoryUserRepository()
    
    # Initialize services
    notification_service = NotificationService()
    validator = ReservationValidator(reservation_repo)
    factory = ReservationFactory()
    price_calculator = PriceCalculator(strategy=NoDiscountStrategy())
    
    reservation_service = ReservationService(
        validator=validator,
        repository=reservation_repo,
        factory=factory,
        price_calculator=price_calculator,
        notification_service=notification_service
    )
    
    payment_service = PaymentService(
        payment_repo=payment_repo,
        reservation_repo=reservation_repo,
        notification_service=notification_service
    )
    
    review_service = ReviewService(
        review_repo=review_repo,
        reservation_repo=reservation_repo
    )
    
    caravan_service = CaravanService(caravan_repo=caravan_repo)
    user_service = UserService(user_repo=user_repo)
    
    print("✓ All services initialized successfully!")
    
    # Step 1: Register users
    print_section("Step 1: Registering Users")
    
    host = user_service.register_user(username="alice_host", role=UserRole.HOST)
    print(f"✓ Registered HOST: {host.username} (ID: {host.user_id})")
    
    guest = user_service.register_user(username="bob_guest", role=UserRole.GUEST)
    print(f"✓ Registered GUEST: {guest.username} (ID: {guest.user_id})")
    
    # Step 2: Register caravans
    print_section("Step 2: Registering Caravans")
    
    caravan1 = caravan_service.register_caravan(
        host=host,
        name="Luxury Airstream",
        capacity=4
    )
    caravan1.daily_rate = 150000
    caravan1.amenities = ["Wi-Fi", "Kitchen", "Bathroom", "Solar Panels"]
    print(f"✓ Registered caravan: {caravan1.name}")
    print(f"  - Capacity: {caravan1.capacity} people")
    print(f"  - Daily Rate: ₩{caravan1.daily_rate:,}")
    print(f"  - Amenities: {', '.join(caravan1.amenities)}")
    
    caravan2 = caravan_service.register_caravan(
        host=host,
        name="Cozy Camper Van",
        capacity=2
    )
    caravan2.daily_rate = 80000
    caravan2.amenities = ["Bed", "Mini Fridge"]
    print(f"✓ Registered caravan: {caravan2.name}")
    print(f"  - Capacity: {caravan2.capacity} people")
    print(f"  - Daily Rate: ₩{caravan2.daily_rate:,}")
    
    # Step 3: Search for caravans
    print_section("Step 3: Searching for Caravans")
    available_caravans = caravan_service.search_caravans(guest=guest, min_capacity=2)
    print(f"Found {len(available_caravans)} caravans with capacity ≥ 2:")
    for cv in available_caravans:
        print(f"  - {cv.name} (₩{cv.daily_rate:,}/day)")
    
    # Step 4: Create a reservation (7+ days for discount)
    print_section("Step 4: Creating Long-term Reservation (7 days)")
    
    start_date = date.today() + timedelta(days=7)
    end_date = date.today() + timedelta(days=13)  # 7 days total
    
    print(f"Reservation Details:")
    print(f"  - Caravan: {caravan1.name}")
    print(f"  - Check-in: {start_date}")
    print(f"  - Check-out: {end_date}")
    print(f"  - Duration: 7 days (qualifies for long-stay discount!)")
    
    reservation = reservation_service.create_reservation(
        guest=guest,
        caravan=caravan1,
        start_date=start_date,
        end_date=end_date
    )
    
    if reservation:
        print(f"✓ Reservation created successfully!")
        print(f"  - Reservation ID: {reservation.reservation_id}")
        print(f"  - Total Price: ₩{reservation.total_price:,}")
        print(f"  - Status: {reservation.status.value}")
        
        # Step 5: Approve reservation (manually update status)
        print_section("Step 5: Approving Reservation")
        reservation.status = ReservationStatus.CONFIRMED
        print(f"✓ Reservation approved!")
        print(f"  - Status: {reservation.status.value}")
        
        # Step 6: Process payment
        print_section("Step 6: Processing Payment")
        payment = payment_service.process_payment(
            reservation_id=reservation.reservation_id,
            amount=reservation.total_price
        )
        
        if payment:
            print(f"✓ Payment processed successfully!")
            print(f"  - Payment ID: {payment.payment_id}")
            print(f"  - Amount: ₩{payment.amount:,}")
            print(f"  - Status: {payment.status.value}")
        
        # Step 7: Complete reservation and leave review
        print_section("Step 7: Completing Reservation & Leaving Review")
        
        # Complete the reservation
        reservation.status = ReservationStatus.COMPLETED
        print(f"✓ Reservation completed!")
        print(f"  - Status: {reservation.status.value}")
        
        # Leave a review
        review = review_service.create_review(
            reservation_id=reservation.reservation_id,
            guest_id=guest.user_id,
            host_id=caravan1.host_id,
            rating=5,
            comment="Amazing experience! The Airstream was spotless and had everything we needed. Highly recommend!"
        )
        
        if review:
            print(f"✓ Review submitted successfully!")
            print(f"  - Rating: {'⭐' * review.rating}")
            print(f"  - Comment: \"{review.comment}\"")
    
    # Step 8: Create a short-term reservation (no discount)
    print_section("Step 8: Creating Short-term Reservation (3 days)")
    
    start_date2 = date.today() + timedelta(days=20)
    end_date2 = date.today() + timedelta(days=22)  # 3 days
    
    print(f"Reservation Details:")
    print(f"  - Caravan: {caravan2.name}")
    print(f"  - Duration: 3 days (no discount)")
    
    reservation2 = reservation_service.create_reservation(
        guest=guest,
        caravan=caravan2,
        start_date=start_date2,
        end_date=end_date2
    )
    
    if reservation2:
        print(f"✓ Reservation created successfully!")
        print(f"  - Total Price: ₩{reservation2.total_price:,}")
    
    # Summary
    print_header("📊 SYSTEM SUMMARY")
    print(f"Total Users: {len(user_repo._users_by_id)}")
    print(f"Total Hosts: 1")
    print(f"Total Guests: 1")
    print(f"Total Caravans: {len(caravan_repo._caravans)}")
    print(f"Total Reservations: {len(reservation_repo._reservations)}")
    print(f"Total Payments: {len(payment_repo._payments)}")
    print(f"Total Reviews: {len(review_repo._reviews)}")
    
    print_header("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("\nThis demo showcased:")
    print("  ✓ User registration (Hosts and Guests)")
    print("  ✓ Caravan listing and search")
    print("  ✓ Reservation creation with pricing strategies")
    print("  ✓ Reservation approval workflow")
    print("  ✓ Payment processing")
    print("  ✓ Reservation completion")
    print("  ✓ Review system")
    print("\nThe system uses design patterns:")
    print("  • Repository Pattern (data access abstraction)")
    print("  • Strategy Pattern (pricing strategies)")
    print("  • Observer Pattern (notifications)")
    print("  • Factory Pattern (object creation)")
    print("  • Dependency Injection (loose coupling)")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
