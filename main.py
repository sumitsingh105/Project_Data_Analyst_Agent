from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from agent.task_router import handle_task
import uvicorn

app = FastAPI()

@app.post("/api/")
async def analyze(request: Request):
    form = await request.form()
    task_file = form.get("file")
    if task_file is None:
        return JSONResponse(status_code=400, content={"error": "Missing 'file'"})
    
    task_text = await task_file.read()
    task_description = task_text.decode("utf-8")

    try:
        result = await handle_task(task_description)  # <-- add await here
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
