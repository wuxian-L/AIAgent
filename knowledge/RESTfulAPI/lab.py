from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}

@app.post("/echo")
async def echo(data: dict):
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("knowledge.RESTfulAPI.lab:app", host="127.0.0.1", port=8000, reload=True)
    