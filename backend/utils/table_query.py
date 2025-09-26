class CreateGroupQuery:
    Create_Table_Query = f"""
    CREATE TABLE IF NOT EXISTS `Group` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description VARCHAR(255) NOT NULL ) """


class AddUserQuery:
    AddUser_Table_Query = f"""
    CREATE TABLE IF NOT EXISTS group_users (
        group_id INT,
        user_id INT,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES `Group`(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE)
        """


class CheckGroupUserQuery:
    CheckGroup_User_Query = f"""
    SELECT Users.id, Users.username, Users.email FROM Users 
    JOIN group_users  ON Users.id = group_users.user_id
    WHERE group_users.group_id = %s"""


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


class GetExpenseQuery:
    GetExpense_Query = f"""
    select id,group_id,description ,amount,paid_by,split_on from expense_detail 
    where group_id = %s
"""