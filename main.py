from fastapi import FastAPI
from backend.api.users.routes import router as users_routes
from backend.api.groups.routes import router as groups_routes
app = FastAPI()

app.include_router(users_routes)

app.include_router(groups_routes)

