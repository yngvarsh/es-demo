import uvicorn

from auth.app import application

uvicorn.run(application, host="0.0.0.0", port=5001, log_level="info", access_log=True)
