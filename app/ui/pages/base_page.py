"""Base page class for UI components."""

from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session


class BasePage(ABC):
    """Base class for all UI pages."""
    
    def __init__(self):
        self.db_session: Optional[Session] = None
        self.company_id: Optional[int] = None
    
    @abstractmethod
    async def render(self, db_session: Session, company_id: Optional[int] = None) -> None:
        """Render the page content. Must be implemented by subclasses."""
        self.db_session = db_session
        self.company_id = company_id