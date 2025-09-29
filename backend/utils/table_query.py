class CreateGroupQuery:
    Create_Table_Query = f"""
    CREATE TABLE IF NOT EXISTS `Group` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description VARCHAR(255) NOT NULL ) """

    Check_Query = f"SELECT id FROM `Group` WHERE name = %s"

    Insert_Query = f"INSERT INTO `Group` (name, description) VALUES (%s, %s)"

    Select_Query = f"SELECT id, name, description FROM `Group` WHERE id = %s"

class AddUserQuery:
    AddUser_Table_Query = f"""
    CREATE TABLE IF NOT EXISTS group_users (
        group_id INT,
        user_id INT,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES `Group`(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE)
        """

    Check_Group_Query = f"SELECT id FROM `Group` WHERE id = %s"

    Check_User_Query = f"SELECT * FROM Users WHERE id = %s"

    Insert_User_Query = f"INSERT IGNORE INTO group_users (group_id, user_id) VALUES (%s, %s)"


class CheckGroupUserQuery:
    CheckGroup_User_Query = f"""
    SELECT Users.id, Users.username, Users.email FROM Users 
    JOIN group_users  ON Users.id = group_users.user_id
    WHERE group_users.group_id = %s"""

    Check_Group_Query = f"SELECT name, description FROM `Group` WHERE id = %s"

class AddExpenseQuery:
    AddExpense_Table_Query = f"""
        CREATE TABLE IF NOT EXISTS expense_detail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            group_id INT NOT NULL,
            description VARCHAR(255) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            paid_by JSON NOT NULL,
            split_on JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES `Group`(id) ON DELETE CASCADE
        ) """

    Check_Group_Query = f"SELECT id FROM `Group` WHERE id = %s"

    Insert_Expense = f"INSERT INTO expense_detail (group_id, description, amount, paid_by,split_on) VALUES (%s,%s, %s, %s, %s)"


class GetExpenseQuery:
    GetExpense_Query = f"""
    select id,group_id,description ,amount,paid_by,split_on from expense_detail 
    where group_id = %s
"""


class LeaveGroupQuery:
   Check_Group_Query = f"SELECT id FROM `Group` WHERE id = %s"

   Check_User_Query = f"SELECT user_id FROM group_users WHERE group_id = %s AND user_id = %s"

   Check_Expense_Query = f"SELECT * FROM expense_detail WHERE group_id = %s"

   Leave_Group_Query = f"DELETE FROM group_users WHERE group_id = %s AND user_id = %s"


class DeleteGroupQuery:
    Check_Group_Query = f"SELECT id FROM `Group` WHERE id = %s"

    Delete_Expense_Query = f"DELETE FROM expense_detail WHERE group_id = %s"

    Delete_User_Query = f"DELETE FROM group_users WHERE group_id = %s"

    Delete_Group_Query = f"DELETE FROM `Group` WHERE id = %s"
