from pydantic import BaseModel
from typing import List, Optional

from backend.utils.response_schema import APIResponseSchema


class Group(BaseModel):
    id: int = None
    name: str
    description: str

class GroupResponse(APIResponseSchema):
    data: Group

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
    group_id: int
    description: str
    amount: float
    paid_by: List[int]
    split_on: List[int]

