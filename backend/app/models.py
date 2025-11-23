from datetime import date, datetime, time

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    tenant_id = Column(String)
    slug = Column(String, unique=True)  # Added unique constraint
    address = Column(String)
    opening_hours = Column(String)  # JSON string
    sport_ids = Column(String)  # JSON string
    communications_language = Column(String)

    # Relationship to Provider
    provider = relationship("Provider")


class Court(Base):
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    sport = Column(String)
    indoor = Column(Boolean, default=False)
    double = Column(Boolean, default=False)


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes
    price = Column(String, nullable=False)  # e.g., "27.5 EUR"
    available = Column(Boolean, default=True)


class SearchOrder(Base):
    __tablename__ = "search_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    location_ids = Column(String, nullable=False)  # JSON string of location IDs
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

    id = Column(Integer, primary_key=True)
    search_order_id = Column(Integer, ForeignKey("search_orders.id"), nullable=False)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    availability_id = Column(Integer, ForeignKey("availabilities.id"), nullable=False)
    notified = Column(Boolean, default=False)
    notified_at = Column(DateTime)


class SearchRequest(Base):
    __tablename__ = "search_requests"

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
    location_ids = Column(String, nullable=False)  # JSON string of location IDs
    live_search = Column(Boolean, default=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
    slots_found = Column(Integer, default=0)


class User(Base):
    __tablename__ = "users"

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


# DTOs
class ProviderDTO(BaseModel):
    id: int | None
    name: str


class LocationDTO(BaseModel):
    id: int | None
    name: str
    provider_id: int
    tenant_id: str | None
    slug: str | None
    address: str | None
    opening_hours: str | None
    sport_ids: str | None
    communications_language: str | None


class CourtDTO(BaseModel):
    id: int | None
    name: str
    location_id: int
    sport: str | None
    indoor: bool = False
    double: bool = False


class AvailabilityDTO(BaseModel):
    id: int | None
    court_id: int
    date: date
    start_time: time
    end_time: time
    duration: int
    price: str
    available: bool = True


class SearchOrderDTO(BaseModel):
    id: int | None
    user_id: str
    location_ids: str  # JSON string of location IDs
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
    id: int | None
    search_order_id: int
    court_id: int
    availability_id: int
    notified: bool = False
    notified_at: datetime | None


class SearchRequestDTO(BaseModel):
    id: int | None
    search_hash: str
    date: date
    start_time: time
    end_time: time
    duration_minutes: int
    court_type: str = "all"
    court_config: str = "all"
    location_ids: str
    live_search: bool = False
    performed_at: datetime | None
    slots_found: int = 0


class UserDTO(BaseModel):
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
    provider: str
    court: str
    location: str
    date: str
    timeslot: str
    price: str
    available: bool
