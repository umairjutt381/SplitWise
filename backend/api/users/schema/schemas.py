from pydantic import BaseModel

class Login(BaseModel):
    username: str =None
    email: str =None
    password: str

class CreateUser(BaseModel):
    username: str
    email: str
    password: str
