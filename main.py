# main.py
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from agent.task_router import handle_task
import asyncio
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
        result = await asyncio.wait_for(handle_task(task_description), timeout=180)  # 3 minutes max
        return JSONResponse(content=result)
    except asyncio.TimeoutError:
        return JSONResponse(status_code=504, content={"error": "Processing exceeded 3-minute timeout."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
