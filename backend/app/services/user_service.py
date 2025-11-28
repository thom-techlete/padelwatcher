from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import User

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class UserService:
    """Service for managing user database operations.

    Returns User database objects. Serialization to JSON/DTOs
    should be handled by the API routes.
    """

    def __init__(self):
        self.session = Session()

    def create_user(
        self, email: str, password_hash: str, user_id: str, is_admin: bool = False
    ) -> User:
        """Create a new user account (unapproved by default).

        Args:
            email: User's email address
            password_hash: Hashed password
            user_id: Unique user identifier
            is_admin: Whether user is an admin (default False)

        Returns:
            User: The created User database object
        """
        user = User(
            email=email,
            password_hash=password_hash,
            user_id=user_id,
            approved=False,  # New users need approval
            is_admin=is_admin,
            created_at=datetime.now(UTC),
        )
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User's email address

        Returns:
            User | None: User database object or None if not found
        """
        return self.session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by user_id (string identifier).

        Args:
            user_id: User's unique identifier

        Returns:
            User | None: User database object or None if not found
        """
        return self.session.query(User).filter(User.user_id == user_id).first()

    def get_user_by_id_numeric(self, id: int) -> User | None:
        """Get user by numeric database ID.

        Args:
            id: User's numeric database ID

        Returns:
            User | None: User database object or None if not found
        """
        return self.session.query(User).filter(User.id == id).first()

    def approve_user(self, user_id: int, approved_by_user_id: str) -> User | None:
        """Approve a user account.

        Args:
            user_id: Numeric user ID to approve
            approved_by_user_id: User ID of admin approving

        Returns:
            User | None: Updated User database object or None if not found
        """
        user = self.get_user_by_id_numeric(user_id)
        if user:
            user.approved = True
            user.approved_at = datetime.now(UTC)
            user.approved_by = approved_by_user_id
            self.session.commit()
            return user
        return None

    def reject_user(self, user_id: int) -> bool:
        """Reject a user account (delete it).

        Args:
            user_id: Numeric user ID to reject

        Returns:
            bool: True if user was deleted, False if user not found
        """
        user = self.get_user_by_id_numeric(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def get_pending_users(self) -> list[User]:
        """Get all users waiting for approval.

        Returns:
            list[User]: List of User database objects awaiting approval
        """
        return self.session.query(User).filter(~User.approved).all()

    def get_approved_users(self) -> list[User]:
        """Get all approved users.

        Returns:
            list[User]: List of approved User database objects
        """
        return self.session.query(User).filter(User.approved).all()

    def get_all_users(self) -> list[User]:
        """Get all users in the system.

        Returns:
            list[User]: List of all User database objects
        """
        return self.session.query(User).all()

    def activate_user(self, user_id: int) -> User | None:
        """Activate a user account.

        Args:
            user_id: Numeric user ID to activate

        Returns:
            User | None: Updated User database object or None if not found
        """
        user = self.get_user_by_id_numeric(user_id)
        if user:
            user.active = True
            self.session.commit()
            return user
        return None

    def deactivate_user(self, user_id: str) -> User | None:
        """Deactivate a user account.

        Args:
            user_id: User identifier to deactivate

        Returns:
            User | None: Updated User database object or None if not found
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.active = False
            self.session.commit()
            return user
        return None

    def authenticate_user(self, email: str, password: str) -> dict | None:
        """Authenticate a user and return user info if approved and active.

        Args:
            email: User's email address
            password: Plain text password to verify

        Returns:
            dict | None: Dictionary with user_id, email, is_admin or None if authentication failed
        """
        user = self.get_user_by_email(email)
        if user and user.approved and user.active:
            if check_password_hash(user.password_hash, password):
                return {
                    "user_id": user.user_id,
                    "email": user.email,
                    "is_admin": user.is_admin,
                }
        return None

    def update_user_profile(
        self, user_id: str, email: str | None = None
    ) -> User | None:
        """Update user profile information.

        Args:
            user_id: User identifier to update
            email: New email address (optional)

        Returns:
            User | None: Updated User database object or None if not found

        Raises:
            ValueError: If email is already in use
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Update email if provided and not already taken
        if email and email != user.email:
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise ValueError("Email already in use")
            user.email = email

        self.session.commit()
        return user

    def update_user_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> User | None:
        """Update user password after verifying current password.

        Args:
            user_id: User identifier to update
            current_password: Current password to verify
            new_password: New password to set

        Returns:
            User | None: Updated User database object or None if not found

        Raises:
            ValueError: If current password is incorrect
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            raise ValueError("Current password is incorrect")

        # Update password
        user.password_hash = generate_password_hash(new_password)
        self.session.commit()
        return user


user_service = UserService()
