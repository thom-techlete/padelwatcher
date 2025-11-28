from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.constants import PROVIDERS

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    tenant_id = Column(String, unique=True)  # Added unique constraint
    slug = Column(String, unique=True)  # Added unique constraint
    address = Column(JSONB)
    opening_hours = Column(JSONB)
    sport = Column(ARRAY(String))
    communications_language = Column(String)
    timezone = Column(String, default="Europe/Amsterdam")  # IANA timezone string

    # Relationship to Courts with cascade delete
    courts = relationship(
        "Court", back_populates="location", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint(provider.in_(PROVIDERS), name="provider_check"),)


class Court(Base):
    __tablename__ = "courts"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    resource_id = Column(String, unique=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    sport = Column(String)
    indoor = Column(Boolean, default=False)
    double = Column(Boolean, default=False)

    # Relationship to Location
    location = relationship("Location", back_populates="courts")
    # Relationship to Availabilities with cascade delete
    availabilities = relationship(
        "Availability", back_populates="court", cascade="all, delete-orphan"
    )
    # Relationship to SearchOrderNotifications with cascade delete
    notifications = relationship(
        "SearchOrderNotification", back_populates="court", cascade="all, delete-orphan"
    )


class Availability(Base):
    __tablename__ = "availabilities"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes
    price = Column(String, nullable=False)  # e.g., "27.5 EUR"
    available = Column(Boolean, default=True)

    # Relationship to Court
    court = relationship("Court", back_populates="availabilities")

    __table_args__ = (
        UniqueConstraint(
            "court_id", "date", "start_time", "duration", name="uq_availability_slot"
        ),
        CheckConstraint(duration > 0, name="duration_positive"),
    )


class SearchOrder(Base):
    __tablename__ = "search_orders"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    location_ids = Column(ARRAY(Integer), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    court_type = Column(String, default="all")  # 'all', 'indoor', 'outdoor'
    court_config = Column(String, default="all")  # 'all', 'single', 'double'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_check_at = Column(DateTime)  # When the order was last checked


class SearchOrderNotification(Base):
    __tablename__ = "search_order_notifications"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    search_order_id = Column(Integer, ForeignKey("search_orders.id"), nullable=False)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    availability_id = Column(Integer, ForeignKey("availabilities.id"), nullable=False)
    notified = Column(Boolean, default=False)
    notified_at = Column(DateTime)

    # Relationship to Court
    court = relationship("Court", back_populates="notifications")


class SearchRequest(Base):
    __tablename__ = "search_requests"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    search_hash = Column(
        String, unique=True, nullable=False
    )  # Hash of search parameters
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    court_type = Column(String, default="all")
    court_config = Column(String, default="all")  # 'all', 'single', 'double'
    location_id = Column(Integer, nullable=False)
    live_search = Column(Boolean, default=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
    slots_found = Column(Integer, default=0)


class User(Base):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    user_id = Column(String, unique=True, nullable=False)  # e.g., 'user_123'
    approved = Column(Boolean, default=False)
    active = Column(Boolean, default=True)  # Can be deactivated by admin
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    approved_by = Column(String)  # user_id of admin who approved


# Legacy DTOs - kept for backward compatibility but not recommended
# Best practice: Use database models directly, serialize using model.model_dump()
# API routes should handle JSON serialization/deserialization


class LocationDTO(BaseModel):
    """Legacy DTO - use Location model directly instead"""

    id: int | None
    name: str
    provider: str
    tenant_id: str | None
    slug: str | None
    address: dict | None
    opening_hours: dict | None
    sport: list[str] | None
    communications_language: str | None


class CourtDTO(BaseModel):
    """Legacy DTO - use Court model directly instead"""

    id: int | None
    name: str
    location_id: int
    sport: str | None
    indoor: bool = False
    double: bool = False


class AvailabilityDTO(BaseModel):
    """Legacy DTO - use Availability model directly instead"""

    id: int | None
    court_id: int
    date: date
    start_time: time
    end_time: time
    duration: int
    price: str
    available: bool = True


class SearchOrderDTO(BaseModel):
    """Legacy DTO - use SearchOrder model directly instead"""

    id: int | None
    user_id: str
    location_ids: list[int]
    date: date
    start_time: time
    end_time: time
    duration_minutes: int
    court_type: str = "all"
    court_config: str = "all"
    is_active: bool = True
    created_at: datetime | None
    updated_at: datetime | None
    last_check_at: datetime | None


class SearchOrderNotificationDTO(BaseModel):
    """Legacy DTO - use SearchOrderNotification model directly instead"""

    id: int | None
    search_order_id: int
    court_id: int
    availability_id: int
    notified: bool = False
    notified_at: datetime | None


class SearchRequestDTO(BaseModel):
    """Legacy DTO - use SearchRequest model directly instead"""

    id: int | None
    search_hash: str
    date: date
    start_time: time
    end_time: time
    duration_minutes: int
    court_type: str = "all"
    court_config: str = "all"
    location_id: int
    live_search: bool = False
    performed_at: datetime | None
    slots_found: int = 0


class UserDTO(BaseModel):
    """Legacy DTO - use User model directly instead"""

    id: int | None
    email: str
    user_id: str
    approved: bool = False
    active: bool = True
    is_admin: bool = False
    created_at: datetime | None
    approved_at: datetime | None
    approved_by: str | None


# Internal format DTO
class InternalAvailabilityDTO(BaseModel):
    """Internal DTO for provider API responses"""

    provider: str
    court: str
    location: str
    date: str
    timeslot: str
    price: str
    available: bool
