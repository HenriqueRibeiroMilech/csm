from pydantic import BaseModel, ConfigDict

from backend.models import UserRole


class UserSchema(BaseModel):
    username: str
    email: str  # aceita e-mail ou CPF
    password: str
    role: UserRole = UserRole.CASAL


class UserPublic(BaseModel):
    id: int
    username: str
    email: str  # pode ser e-mail ou CPF
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]
