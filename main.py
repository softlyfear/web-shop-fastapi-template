




from fastapi import FastAPI

from app.web.router import router as web_router
app = FastAPI()


from fastapi.staticfiles import StaticFiles

from app.web.router import router as web_router

app = FastAPI()



app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router)
