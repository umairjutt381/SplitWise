from pydantic import BaseModel
from typing import List, Optional


class Group(BaseModel):
    id: int = None
    name: Optional[str] = None
    description: Optional[str] = None

class UserAdd(BaseModel):
    group_id: int
    user_id: int

class GroupUser(BaseModel):
    user_id: int
    username: str
    email: str

class GetGroupUsersResponse(BaseModel):
    group_name: str
    description: str
    users: List[GroupUser]

class AddExpenseRequest(BaseModel):
    group_id: Optional[int] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    paid_by: Optional[List[str]] = None
    split_on: Optional[List[str]] = None

