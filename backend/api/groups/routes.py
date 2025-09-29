from backend.api.groups.sattlement import expense_settlement
from backend.api.groups.validations import CreateGroupValidation, AddGroupMemberValidation, CheckGroupMember,AddExpenseValidation,\
    LeaveGroupValidation
from backend.utils.table_query import CreateGroupQuery,AddUserQuery,CheckGroupUserQuery,AddExpenseQuery,\
    GetExpenseQuery,LeaveGroupQuery,DeleteGroupQuery
from backend.utils.db_conn import conn
import json
from fastapi import HTTPException,APIRouter
from backend.api.groups.schema.schemas import Group, UserAdd, GetGroupUsersResponse, GroupUser, AddExpenseRequest,GroupResponse


def get_db_conn():
    return conn
router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/CreateGroup", response_model=GroupResponse, status_code=201)
async def create_group(group: Group):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    cursor.execute(CreateGroupQuery.Create_Table_Query)
    CreateGroupValidation.validate_group_data(group)
    CreateGroupValidation.check_group_exist(cursor, group)
    cursor.execute(CreateGroupQuery.Insert_Query, (group.name, group.description))
    db_conn.commit()
    group_id = cursor.lastrowid
    new_group = CreateGroupValidation.fetch_group_by_id(cursor, group_id)
    cursor.close()
    return GroupResponse(
        success=True,
        message="Group created successfully",
        code=201,
        data=new_group
    )

@router.post("/add_user", status_code=201)
async def add_user_to_group(user: UserAdd):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    AddGroupMemberValidation.check_group_exist(cursor, user)
    AddGroupMemberValidation.check_user_exist(cursor, user)
    cursor.execute(AddUserQuery.AddUser_Table_Query)
    cursor.execute(AddUserQuery.Insert_User_Query,(user.group_id, user.user_id))
    db_conn.commit()
    cursor.close()
    return {"message": "User added successfully"}


@router.get("/check_group_users/{group_id}", response_model=GetGroupUsersResponse)
async def check_group_users(group_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    group_info = CheckGroupMember.check_group_exist(cursor, group_id)
    group_name, description = group_info
    cursor.execute(CheckGroupUserQuery.CheckGroup_User_Query, (group_id,))
    users = cursor.fetchall()
    cursor.close()
    user_list = [GroupUser(
        user_id=i[0],
        username=i[1],
        email=i[2])
        for i in users]
    return GetGroupUsersResponse(
        group_name=group_name,
        description=description,
        users=user_list
    )
@router.post("/add_expense", status_code=201)
async def add_expense(expense: AddExpenseRequest):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    cursor.execute(AddExpenseQuery.AddExpense_Table_Query)
    AddExpenseValidation.check_group_exist(cursor, expense)
    cursor.execute(AddExpenseQuery.Insert_Expense,
    (expense.group_id, expense.description, expense.amount, json.dumps(expense.paid_by), json.dumps(expense.split_on)))
    db_conn.commit()
    return {"message": "Expense added successfully"}

@router.get("/get_expenses/{group_id}/{user_id}", status_code=200)
async def get_expenses(group_id: int,user_id:int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute(GetExpenseQuery.GetExpense_Query, (group_id,))
    expenses = cursor.fetchall()
    user_settlement = expense_settlement(expenses,user_id)
    return user_settlement


@router.delete("/leave-group/{group_id}/{user_id}", status_code=200)
async def leave_group(group_id: int, user_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor(dictionary=True)
    LeaveGroupValidation.check_group_exist(cursor, group_id)
    LeaveGroupValidation.check_user_exist(cursor,group_id ,user_id)
    cursor.execute(LeaveGroupQuery.Check_Expense_Query, (group_id,))
    rows = cursor.fetchall()
    settlements = expense_settlement(rows,user_id)
    if settlements.get("You pay back") and settlements.get("You pay back")!=[]:
        response = []
        for item in settlements.get("You pay back"):
            response.append({"message": f"You dont leave group,You have to pay back amount {item.get('amount')} to {item.get('to_user')} "})
        return response
    cursor.execute(LeaveGroupQuery.Leave_Group_Query, (group_id, user_id))
    return {"message": f"User {user_id} has left the group {group_id} successfully."}


@router.delete("/group/{group_id}", status_code=200)
async def delete_group(group_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()

    cursor.execute(DeleteGroupQuery.Check_Group_Query, (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    cursor.execute(DeleteGroupQuery.Delete_Expense_Query, (group_id,))
    cursor.execute(DeleteGroupQuery.Delete_User_Query, (group_id,))
    cursor.execute(DeleteGroupQuery.Delete_Group_Query, (group_id,))
    db_conn.commit()
    cursor.close()
    return {"message": "Group deleted successfully done"}



