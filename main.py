from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import models
import os
from database import engine, get_db

# Создаем директории для статических файлов и шаблонов, если их нет
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Простая регистрация и авторизация")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials, db: Session):
    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не существует",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/register")
def register(
    username: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_exists = db.query(models.Megabait).filter(models.User.username == username).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    new_user = models.Megabait(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/login-page", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login-form")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Пользователь не существует"}
        )
    
    if user.password != password:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Неверный пароль"}
        )
    
    return RedirectResponse(url="/protected-page", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = verify_credentials(credentials, db)
    return {"message": f"Вы успешно вошли как {user.username}"}

@app.get("/protected-page", response_class=HTMLResponse)
async def protected_page(request: Request):
    return templates.TemplateResponse("protected.html", {"request": request})

@app.get("/protected")
def protected_route(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = verify_credentials(credentials, db)
    return {"message": f"Привет, {user.username}! Это защищенный маршрут."}

@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 