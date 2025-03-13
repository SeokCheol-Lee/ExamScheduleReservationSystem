from app.interface.api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.interface.api:app", host="0.0.0.0", port=8000, reload=True)
