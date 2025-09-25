from backend.api.groups.sattlement import expense_settlement
from backend.utils.db_conn import *
import json
from fastapi import HTTPException,APIRouter
from backend.api.groups.schema.schemas import Group,UserAdd,GetGroupUsersResponse,GroupUser,AddExpenseRequest

def get_db_conn():
    return conn
router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/CreateGroup", response_model=Group, status_code=201)
async def create_group(group: Group):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    table_name = "`Group`"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description VARCHAR(255) NOT NULL ) """
    cursor.execute(create_table_query)
    if not group.name.strip() or not group.description.strip():
        raise HTTPException(status_code=400, detail="Name and description are required")
    check_query = f"SELECT id FROM {table_name} WHERE name = %s"
    cursor.execute(check_query, (group.name,))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="Group with this name already exists")
    insert_query = f"INSERT INTO {table_name} (name, description) VALUES (%s, %s)"
    cursor.execute(insert_query, (group.name, group.description))
    db_conn.commit()
    group_id = cursor.lastrowid
    select_query = f"SELECT id, name, description FROM {table_name} WHERE id = %s"
    cursor.execute(select_query, (group_id,))
    row = cursor.fetchone()
    cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Group not found after creation")
    return Group(id=row[0], name=row[1], description=row[2])

@router.post("/add_user", status_code=201)
async def add_user_to_group(user: UserAdd):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM `Group` WHERE id = %s", (user.group_id,))
    if cursor.fetchone() is None:
        cursor.close()
        raise HTTPException(status_code=404, detail="Group not found")
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user.user_id,))
    user_detail = cursor.fetchone()
    if user_detail is None:
        cursor.close()
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_users (
        group_id INT,
        user_id INT,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES `Group`(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE)
        """)
    cursor.execute("INSERT IGNORE INTO group_users (group_id, user_id) VALUES (%s, %s)",
        (user.group_id, user.user_id)
    )
    db_conn.commit()
    cursor.close()
    return {"message": "User added successfully"}


@router.get("/check_group_users/{group_id}", response_model=GetGroupUsersResponse)
async def check_group_users(group_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()
    cursor.execute("SELECT name, description FROM `Group` WHERE id = %s", (group_id,))
    group_info = cursor.fetchone()
    if not group_info:
        cursor.close()
        raise HTTPException(status_code=404, detail="Group not found")
    group_name, description = group_info
    cursor.execute("""
    SELECT Users.id, Users.username, Users.email FROM Users 
    JOIN group_users  ON Users.id = group_users.user_id
    WHERE group_users.group_id = %s""", (group_id,))
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_detail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_id INT NOT NULL,
            description VARCHAR(255) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            paid_by JSON NOT NULL,
            split_on JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES `Group`(id) ON DELETE CASCADE
        ) """)
    cursor.execute("SELECT id FROM `Group` WHERE id = %s", (expense.group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    cursor.execute("""INSERT INTO expense_detail (group_id, description, amount, paid_by,split_on) VALUES (%s,%s, %s, %s, %s)""",
       (expense.group_id, expense.description, expense.amount, json.dumps(expense.paid_by), json.dumps(expense.split_on)))
    db_conn.commit()
    return {"message": "Expense added successfully"}

@router.get("/get_expenses/{group_id}/{user_id}", status_code=200)
async def get_expenses(group_id: int,user_id:int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("select id,group_id,description ,amount,paid_by,split_on from expense_detail where group_id = %s", (group_id,))
    expenses = cursor.fetchall()
    user_settlement = expense_settlement(expenses,user_id)
    return user_settlement


@router.delete("/leave-group/{group_id}/{user_id}", status_code=200)
async def leave_group(group_id: int, user_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM `Group` WHERE id = %s", (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")
    cursor.execute("SELECT user_id FROM group_users WHERE group_id = %s AND user_id = %s", (group_id, user_id))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found in group")
    cursor.execute("SELECT * FROM expense_detail WHERE group_id = %s", (group_id,))
    rows = cursor.fetchall()
    settlements = expense_settlement(rows,user_id)
    if settlements.get("You pay back") and settlements.get("You pay back")!=[]:
        response = []
        for item in settlements.get("You pay back"):
            response.append({"message": f"You dont leave group,You have to pay back amount {item.get('amount')} to {item.get('to_user')} "})
        return response
    cursor.execute("DELETE FROM group_users WHERE group_id = %s AND user_id = %s", (group_id, user_id))
    return {"message": f"User {user_id} has left the group {group_id} successfully."}


@router.delete("/group/{group_id}", status_code=200)
async def delete_group(group_id: int):
    db_conn = get_db_conn()
    cursor = db_conn.cursor()

    cursor.execute("SELECT id FROM `Group` WHERE id = %s", (group_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    cursor.execute("DELETE FROM expense_detail WHERE group_id = %s", (group_id,))
    cursor.execute("DELETE FROM group_users WHERE group_id = %s", (group_id,))
    cursor.execute("DELETE FROM `Group` WHERE id = %s", (group_id,))
    db_conn.commit()
    cursor.close()
    return {"message": "Group deleted successfully"}



