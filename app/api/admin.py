from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from core.config import settings

# Инициализация Jinja2Templates с указанием директории шаблонов
admin = Jinja2Templates(directory=settings.files.admin_templates)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/", response_class=HTMLResponse)
async def render_admin(request: Request):
    return admin.TemplateResponse(
        "index.html",  # Имя шаблона
        {"request": request}  # Контекст с передачей request
    )