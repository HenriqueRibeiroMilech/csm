from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import UserRole, table_registry

if TYPE_CHECKING:
    from .todo import Todo
    from .wedding import Rsvp, WeddingList


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.CASAL)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    todos: Mapped[list['Todo']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    wedding_lists: Mapped[list['WeddingList']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='owner',
    )

    rsvps: Mapped[list['Rsvp']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='guest',
    )
