from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from scraper import scrape_url

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Req(BaseModel):
    url: str

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape")
async def scrape(req: Req):
    return {"result": await scrape_url(req.url)}
