
from backend.utils.db_conn import *
from fastapi import HTTPException,APIRouter
from backend.api.users.schema.schemas import CreateUser,Login


def get_db_conn():
    return conn
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create-group-user", status_code=201)
async def create_group_user(user: CreateUser):
    conn = get_db_conn()
    cursor = conn.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS Users (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )"""
    cursor.execute(create_table_query)
    cursor.execute("SELECT * FROM Users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        cursor.close()
        raise HTTPException(status_code=400, detail="Group user with this email already exists")
    hashed_pw = hash_password(user.password)
    cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)",
                   (user.username, user.email, hashed_pw))
    conn.commit()
    cursor.close()
    return {"message": "Group user created successfully"}

@router.post("/login", status_code=201)
async def login(users: Login):
    conn = get_db_conn()
    cursor = conn.cursor()
    if users.username:
        cursor.execute("SELECT id, username, password FROM Users WHERE username = %s", (users.username,))
        db_user = cursor.fetchone()
        if not db_user:
            cursor.close()
            raise HTTPException(status_code=400, detail="Invalid username or email")
        user_id, stored_username, stored_password = db_user
        identifier = stored_username
    elif users.email:
        cursor.execute("SELECT id, email, password FROM Users WHERE email = %s", (users.email,))
        db_user = cursor.fetchone()
        if not db_user:
            cursor.close()
            raise HTTPException(status_code=400, detail="Invalid username or email")
        user_id, stored_email, stored_password = db_user
        identifier = stored_email
    else:
        cursor.close()
        raise HTTPException(status_code=400, detail="Username or email required")

    if not verify_password(users.password, stored_password):
        cursor.close()
        raise HTTPException(status_code=400, detail="Invalid password")

    cursor.close()
    token = create_access_token(data={"sub": identifier, "user_id": user_id})
    refresh_token = create_refresh_token(data={"sub": identifier, "user_id": user_id})
    return {"access_token": token, "refresh_token": refresh_token}

