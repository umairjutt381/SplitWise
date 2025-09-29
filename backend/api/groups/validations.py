from fastapi import HTTPException
from backend.api.groups.schema.schemas import Group,UserAdd,AddExpenseRequest
from backend.utils.response_schema import APIResponseSchema
from backend.utils.table_query import (CreateGroupQuery,AddUserQuery,CheckGroupUserQuery,AddExpenseQuery,
                                       LeaveGroupQuery)


class CreateGroupValidation(APIResponseSchema):

    def validate_group_data(group):
        if not group.name.strip() or not group.description.strip():
            raise HTTPException(status_code=400, detail="Name and description are required")


    def check_group_exist(cursor,group):
        cursor.execute(CreateGroupQuery.Check_Query, (group.name,))
        existing = cursor.fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Group with this name already exists")

    def fetch_group_by_id(cursor, group_id: int):
        cursor.execute(CreateGroupQuery.Select_Query, (group_id,))
        row = cursor.fetchone()
        cursor.close()
        if not row:
            raise HTTPException(status_code=404, detail="Group not found after creation")
        return Group(id=row[0], name=row[1], description=row[2])

class AddGroupMemberValidation:

    def check_group_exist(cursor, user):
        cursor.execute(AddUserQuery.Check_Group_Query, (user.group_id,))
        if cursor.fetchone() is None:
            cursor.close()
            raise HTTPException(status_code=404, detail="Group not found")

    def check_user_exist(cursor, user):
        cursor.execute(AddUserQuery.Check_User_Query, (user.user_id,))
        user_detail = cursor.fetchone()
        if user_detail is None:
            cursor.close()
            raise HTTPException(status_code=404, detail="User not found")


class CheckGroupMember:

    def check_group_exist(cursor,group_id: int):
        cursor.execute(CheckGroupUserQuery.Check_Group_Query, (group_id,))
        group_info = cursor.fetchone()
        if not group_info:
            cursor.close()
            raise HTTPException(status_code=404, detail="Group not found")
        return group_info

class AddExpenseValidation:
    def check_group_exist(cursor, expense):
        cursor.execute(AddExpenseQuery.Check_Group_Query, (expense.group_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Group not found")

class LeaveGroupValidation:
    def check_group_exist(cursor, group_id:int):
        cursor.execute(LeaveGroupQuery.Check_Group_Query, (group_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Group not found")

    def check_user_exist(cursor, group_id:int,user_id:int):
        cursor.execute(LeaveGroupQuery.Check_User_Query, (group_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found in group")
