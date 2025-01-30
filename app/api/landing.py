from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from core.config import settings

# Инициализация Jinja2Templates с указанием директории шаблонов
landing = Jinja2Templates(directory=settings.files.landing_templates)

router = APIRouter(tags=["landing"])

@router.get("/", response_class=HTMLResponse)
async def render_landing(request: Request):
    return landing.TemplateResponse(
        "index.html",  # Имя шаблона
        {"request": request}  # Контекст с передачей request
    )