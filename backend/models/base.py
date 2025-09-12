from enum import Enum

from sqlalchemy.orm import registry

table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


class UserRole(str, Enum):
    CASAL = 'CASAL'
    CONVIDADO = 'CONVIDADO'


class GiftStatus(str, Enum):
    available = 'available'
    reserved = 'reserved'
    purchased = 'purchased'


class RsvpStatus(str, Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    declined = 'declined'
