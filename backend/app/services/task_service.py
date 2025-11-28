"""Service for managing background search tasks with progress tracking"""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SQLALCHEMY_DATABASE_URI
from app.models import SearchTask

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing background search tasks"""

    def __init__(self):
        self.session = Session()

    def create_task(self, user_id: str, search_params: dict) -> SearchTask:
        """Create a new search task

        Args:
            user_id: The user who initiated the search
            search_params: Search parameters (date, times, locations, etc.)

        Returns:
            SearchTask: The created task
        """
        task_id = str(uuid.uuid4())
        location_ids = search_params.get("location_ids", [])

        task = SearchTask(
            task_id=task_id,
            user_id=user_id,
            status="pending",
            progress=0,
            current_step="Initializing search...",
            total_locations=len(location_ids),
            processed_locations=0,
            search_params=search_params,
        )

        self.session.add(task)
        self.session.commit()
        logger.info(f"[TASK] Created task {task_id} for user {user_id}")
        return task

    def get_task(self, task_id: str) -> SearchTask | None:
        """Get a task by ID

        Args:
            task_id: The task UUID

        Returns:
            SearchTask | None: The task or None if not found
        """
        return (
            self.session.query(SearchTask).filter(SearchTask.task_id == task_id).first()
        )

    def get_task_for_user(self, task_id: str, user_id: str) -> SearchTask | None:
        """Get a task by ID, ensuring it belongs to the user

        Args:
            task_id: The task UUID
            user_id: The user ID to verify ownership

        Returns:
            SearchTask | None: The task or None if not found/unauthorized
        """
        return (
            self.session.query(SearchTask)
            .filter(SearchTask.task_id == task_id, SearchTask.user_id == user_id)
            .first()
        )

    def update_task_progress(
        self,
        task_id: str,
        progress: int,
        current_step: str,
        processed_locations: int | None = None,
        total_locations: int | None = None,
    ) -> SearchTask | None:
        """Update task progress

        Args:
            task_id: The task UUID
            progress: Progress percentage (0-100)
            current_step: Description of current operation
            processed_locations: Number of locations processed so far
            total_locations: Total locations to process (optional, for correcting count)

        Returns:
            SearchTask | None: The updated task
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.progress = min(max(progress, 0), 100)  # Clamp between 0-100
        task.current_step = current_step
        if processed_locations is not None:
            task.processed_locations = processed_locations
        if total_locations is not None:
            task.total_locations = total_locations
        task.updated_at = datetime.now(UTC)

        self.session.commit()
        return task

    def start_task(self, task_id: str) -> SearchTask | None:
        """Mark task as running

        Args:
            task_id: The task UUID

        Returns:
            SearchTask | None: The updated task
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.status = "running"
        task.started_at = datetime.now(UTC)
        task.current_step = "Starting search..."
        task.updated_at = datetime.now(UTC)

        self.session.commit()
        logger.info(f"[TASK] Task {task_id} started")
        return task

    def complete_task(self, task_id: str, results: dict) -> SearchTask | None:
        """Mark task as completed with results

        Args:
            task_id: The task UUID
            results: The search results to store

        Returns:
            SearchTask | None: The updated task
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.status = "completed"
        task.progress = 100
        task.current_step = "Search completed"
        task.results = results
        task.completed_at = datetime.now(UTC)
        task.updated_at = datetime.now(UTC)

        self.session.commit()
        logger.info(f"[TASK] Task {task_id} completed")
        return task

    def fail_task(self, task_id: str, error_message: str) -> SearchTask | None:
        """Mark task as failed with error message

        Args:
            task_id: The task UUID
            error_message: Description of what went wrong

        Returns:
            SearchTask | None: The updated task
        """
        task = self.get_task(task_id)
        if not task:
            return None

        task.status = "failed"
        task.error_message = error_message
        task.completed_at = datetime.now(UTC)
        task.updated_at = datetime.now(UTC)

        self.session.commit()
        logger.error(f"[TASK] Task {task_id} failed: {error_message}")
        return task

    def cancel_task(self, task_id: str) -> SearchTask | None:
        """Cancel a pending or running task

        Args:
            task_id: The task UUID

        Returns:
            SearchTask | None: The updated task
        """
        task = self.get_task(task_id)
        if not task:
            return None

        if task.status in ("pending", "running"):
            task.status = "cancelled"
            task.current_step = "Search cancelled"
            task.completed_at = datetime.now(UTC)
            task.updated_at = datetime.now(UTC)
            self.session.commit()
            logger.info(f"[TASK] Task {task_id} cancelled")

        return task

    def cleanup_old_tasks(self, hours: int = 24) -> int:
        """Delete tasks older than specified hours

        Args:
            hours: Delete tasks older than this many hours

        Returns:
            int: Number of tasks deleted
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        deleted = (
            self.session.query(SearchTask)
            .filter(SearchTask.created_at < cutoff)
            .delete()
        )
        self.session.commit()
        logger.info(f"[TASK] Cleaned up {deleted} old tasks")
        return deleted

    def to_dict(self, task: SearchTask) -> dict:
        """Convert task to dictionary for API response

        Args:
            task: The SearchTask object

        Returns:
            dict: Task data as dictionary
        """
        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "current_step": task.current_step,
            "total_locations": task.total_locations,
            "processed_locations": task.processed_locations,
            "error_message": task.error_message,
            "results": task.results,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
        }


task_service = TaskService()
