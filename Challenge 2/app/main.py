from fastapi import FastAPI
from app.routes.hello import router as hello_router
from app.db.database import Base, engine

def create_app() -> FastAPI:
    app = FastAPI(
        title="FastAPI App with DB",
        version="1.0.0"
    )

    # Include the hello router
    app.include_router(hello_router)

    # Initialize database tables
    Base.metadata.create_all(bind=engine)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
