#!/usr/bin/env python3
"""
Script to create an admin user for the Padel Watcher API
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import AvailabilityService
from werkzeug.security import generate_password_hash


def create_admin_user():
    """Create an admin user"""
    service = AvailabilityService()

    # Check if admin already exists
    existing_admin = service.get_user_by_email("admin@padelwatcher.com")
    if existing_admin:
        print("Admin user already exists!")
        return

    # Create admin user
    admin_user = service.create_user(
        email="admin@padelwatcher.com",
        password_hash=generate_password_hash("admin123"),
        user_id="admin",
        is_admin=True,
    )

    # Auto-approve the admin
    service.approve_user(admin_user.id, "system")

    print("Admin user created successfully!")
    print("Email: admin@padelwatcher.com")
    print("Password: admin123")
    print("Please change the password after first login!")


if __name__ == "__main__":
    create_admin_user()
