"""
Simple FastAPI test application
"""
from fastapi import FastAPI

app = FastAPI(
    title="Kade Connect API - Test",
    description="Simple test version",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Kade Connect API is running!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "kade-connect-test"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Kade Connect API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
