from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Простая регистрация и авторизация")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/register")
def register(
    username: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_exists = db.query(models.User).filter(models.User.username == username).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    new_user = models.User(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован"}



@app.post("/login")
def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = verify_credentials(credentials, db)
    return {"message": f"Вы успешно вошли как {user.username}"}

@app.get("/protected")
def protected_route(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = verify_credentials(credentials, db)
    return {"message": f"Привет, {user.username}! Это защищенный маршрут."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 