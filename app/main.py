from fastapi import FastAPI
from .routers import auth_router, post_router, user_router, comment_router
from .database import Base, engine

# Init main FastAPI app object
app = FastAPI()

# Initiate database tables
Base.metadata.create_all(engine)


# Include routers
app.include_router(auth_router, prefix='/api', tags=['authentication'])
app.include_router(post_router, prefix='/api', tags=['posts'])
app.include_router(user_router, prefix='/api', tags=['users'])
app.include_router(comment_router, prefix='/api', tags=['comments'])
