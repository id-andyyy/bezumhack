from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import models
import os
from database import engine, get_db
import sqlite3
from typing import List, Optional


os.makedirs("static", exist_ok=True)
models.Base.metadata.create_all(bind=engine)
def create_test_products():
    db = next(get_db())
    products_count = db.query(models.User).filter(models.User.is_product != 0).count()
    
    if products_count == 0:
        print("Добавление тестовых товаров...")
        test_products = [
            {
                "name": "Супер товар 1",
                "price": 1999.99,
                "description": "Это невероятный товар, который нужен каждому!",
                "owner_id": 1,
                "image_url": "https://via.placeholder.com/300",
                "secret_info": "Секретная информация о товаре 1"
            },
            {
                "name": "Мега товар 2",
                "price": 2999.99,
                "description": "Второй невероятный товар нашего магазина!",
                "owner_id": 1,
                "image_url": "https://via.placeholder.com/300",
                "secret_info": "Секретная информация о товаре 2"
            }
        ]
        
        for product_data in test_products:
            new_product = models.User(
                is_product=1,
                name=product_data["name"],
                price=product_data["price"],
                description=product_data["description"],
                owner_id=product_data["owner_id"],
                secret_info=product_data["secret_info"],
                image_url=product_data["image_url"],
                username=None,
                password=None,
                credit_card=None
            )
            db.add(new_product)
        
        db.commit()
        print("Тестовые товары добавлены!")

try:
    create_test_products()
except Exception as e:
    print(f"Ошибка при добавлении тестовых товаров: {e}")

app = FastAPI(title="Небезопасный магазин с ужасной архитектурой")

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
        models.User.username == credentials.username,
        models.User.is_product == 0
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
async def home(request: Request, db: Session = Depends(get_db), username: Optional[str] = None):
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
        
    products = db.query(models.User).filter(models.User.is_product != 0).all()    
    products_html = ""
    for product in products:
        product_image = ""
        if product.image_url:
            product_image = f'<img src="{product.image_url}" alt="{product.name}" style="max-width:100%; height:auto; transform: skew(5deg, 10deg);">'
        elif product.gif_base64:
            product_image = f'<img src="data:image/gif;base64,{product.gif_base64}" alt="{product.name}" style="max-width:100%; height:auto; transform: skew(-10deg, 5deg);">'
            
        products_html += f'''
        <div class="item">
            <div class="item-title blink">{product.name}</div>
            {product_image}
            <div class="item-price rotate-text">{product.price} руб.</div>
            <div class="left-align" style="font-family: 'Wingdings', cursive;">{product.description}</div>
            <a href="/product/{product.id}{username_param}" style="text-decoration: none;"><button style="background-color:lime; font-weight:bold; margin-top:5px; transform: rotate({product.id * 5}deg);" class="shake">КУПИТЬ!</button></a>
        </div>
        '''
    auth_block = '''
    <div>
        <a href="/register-page" class="rainbow-text">Регистрация</a> | 
        <a href="/login-page" class="rainbow-text">Войти</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red; font-size: 20px; font-weight: bold; text-shadow: 0 0 10px yellow;">АДМИНКА</a>
    </div>
    '''
    if url_username:
        user = db.query(models.User).filter(
            models.User.username == url_username,
            models.User.is_product == 0
        ).first()
        if user:
            auth_block = f'''
            <div style="background-color: #CCFFCC; padding: 5px; border: 2px dotted blue;">
                <div class="blink" style="color:green; font-weight:bold; font-size: 24px; transform: rotate(-5deg);">ВЫ ВОШЛИ КАК: {user.username}</div>
                <a href="/protected-page?username={user.username}" class="rainbow-text">Личный кабинет</a> |
                <a href="/logout" class="rainbow-text">Выйти</a> |
                <a href="/admin-panel?admin=1" class="blink" style="color:red; font-size: 20px; text-shadow: 0 0 10px yellow;">АДМИНКА</a>
            </div>
            '''
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>СУПЕР МАГАЗИН 2000!!!</title>
    <style>
        @keyframes backgroundFlash {{
            0% {{ background-color: #ff00ff; }}
            25% {{ background-color: #00ff00; }}
            50% {{ background-color: #0000ff; }}
            75% {{ background-color: #ffff00; }}
            100% {{ background-color: #ff00ff; }}
        }}
        
        @keyframes backgroundSpin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 5px;
            cursor: url('https://cur.cursors-4u.net/cursors/cur-1054.cur'), auto;
            animation: backgroundFlash 2s infinite;
            overflow-x: hidden;
        }}
        
        body:before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            opacity: 0.7;
            z-index: -1;
            animation: backgroundSpin 20s linear infinite;
            transform-origin: center center;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            position: relative;
            z-index: 1;
        }}
        
        td {{
            vertical-align: top;
            padding: 0px;
        }}
        
        .logo {{
            font-size: 42px;
            font-weight: bold;
            color: #FF00FF;
            text-shadow: 3px 3px 0 yellow, -3px -3px 0 lime, 5px 5px 0 blue, -5px -5px 0 red;
            font-family: "Impact", fantasy;
            transform: skew(-15deg, 5deg);
            animation: pulse 0.5s infinite alternate;
        }}
        
        @keyframes pulse {{
            from {{ transform: scale(1) skew(-15deg, 5deg); }}
            to {{ transform: scale(1.1) skew(-15deg, 5deg); }}
        }}
        
        .category {{
            background-color: red;
            color: yellow;
            font-weight: bold;
            padding: 2px;
            text-align: center;
            font-size: 20px;
            margin-bottom: 3px;
            border: 5px dashed blue;
            animation: shake 0.5s infinite;
        }}
        
        @keyframes shake {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
            20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
            30% {{ transform: translate(3px, 2px) rotate(0deg); }}
            40% {{ transform: translate(1px, -1px) rotate(1deg); }}
            50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
            60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
            70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
            80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
            90% {{ transform: translate(1px, 2px) rotate(0deg); }}
            100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
        }}
        
        .shake {{
            animation: shake 0.5s infinite;
            display: inline-block;
        }}
        
        .item {{
            border: 4px dotted purple;
            padding: 10px;
            text-align: center;
            background-color: #FFFFCC;
            margin-bottom: 10px;
            margin-right: 10px;
            box-sizing: border-box;
            width: 23%;
            display: inline-block;
            vertical-align: top;
            transform: rotate(random(-5, 5)deg);
            animation: backgroundFlash 3s infinite;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        }}
        
        .item:hover {{
            animation: shake 0.2s infinite;
        }}
        
        .item img {{
            max-width: 100%;
            height: auto;
            border: 5px ridge gold;
            animation: borderColor 2s infinite;
        }}
        
        .item-title {{
            font-weight: bold;
            margin: 2px 0;
            color: blue;
            text-decoration: underline wavy red;
            font-size: 18px;
            text-shadow: 2px 2px 0 yellow;
        }}
        
        .item-price {{
            color: #ff0000;
            font-weight: bold;
            font-size: 24px;
            text-shadow: 0 0 5px yellow;
        }}
        
        .rotate-text {{
            display: inline-block;
            animation: spin 3s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .label {{
            background-color: yellow;
            color: black;
            padding: 1px 3px;
            font-weight: bold;
            display: inline-block;
            transform: rotate(-10deg);
        }}
        
        .highlight {{
            border: 4px solid red;
            background-color: #CCFFFF;
        }}
        
        .nav-item {{
            color: blue;
            text-decoration: underline;
            margin: 0 3px;
        }}
        
        .search {{
            margin: 3px 0;
        }}
        
        .search input {{
            margin-right: 2px;
            background-color: #CCFFCC;
            transform: skew(10deg, 2deg);
        }}
        
        .left-align {{
            text-align: left;
        }}
        
        .blink {{
            animation: blinker 0.3s linear infinite;
        }}
        
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        
        .rotate {{
            animation: rotation 1s infinite linear;
            display: inline-block;
        }}
        
        @keyframes rotation {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(359deg); }}
        }}
        
        .marquee {{
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            background-color: black;
            color: white;
            font-size: 24px;
            padding: 10px 0;
        }}
        
        .marquee-content {{
            display: inline-block;
            animation: marquee 10s linear infinite;
            text-shadow: 0 0 10px red;
        }}
        
        @keyframes marquee {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
        
        .rainbow-text {{
            animation: rainbow 1s infinite;
            font-size: 18px;
            font-weight: bold;
        }}
        
        @keyframes rainbow {{
            0% {{ color: red; }}
            14% {{ color: orange; }}
            28% {{ color: yellow; }}
            42% {{ color: green; }}
            57% {{ color: blue; }}
            71% {{ color: indigo; }}
            85% {{ color: violet; }}
            100% {{ color: red; }}
        }}
        
        .zakadrit-button {{
            position: fixed;
            bottom: 40%;
            right: 40%;
            width: 400px;
            height: 400px;
            background: linear-gradient(45deg, #ff00ff, #00ffff, #ffff00, #ff0000);
            background-size: 400% 400%;
            animation: gradientBG 3s ease infinite, shake 0.3s infinite;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 32px;
            font-weight: bold;
            border: 10px solid;
            border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(255, 0, 255, 1);
            z-index: 9999;
            border-radius: 50%;
            text-align: center;
            color: white;
            text-shadow: 2px 2px 4px black;
        }}
        
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        @keyframes borderColor {{
            0% {{ border-color: gold; }}
            33% {{ border-color: red; }}
            66% {{ border-color: blue; }}
            100% {{ border-color: gold; }}
        }}
    </style>
</head>
<body>
    <div class="marquee">
        <div class="marquee-content">
            !!! ТОВАРЫ БЕЗ РЕГИСТРАЦИИ И СМС !!! СКИДКА 90% НА ВСЕ ТОВАРЫ !!! ТОЛЬКО СЕГОДНЯ !!! ДОСТАВКА БЕСПЛАТНО !!! ЗВОНИТЕ ПРЯМО СЕЙЧАС !!! НЕВЕРОЯТНЫЕ ЦЕНЫ !!! НЕ ЗАБЫТЬ УДАЛИТЬ ИЗ КОДА АДМИН ПАРОЛЬ admin admin !!! 
        </div>
    </div>
    
    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td width="20%" valign="top">
                <a href="/{username_param}">
                    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" alt="Лого" style="float:left; margin-right:5px; width:100px; height:100px; border-radius: 50%; animation: spin 3s linear infinite;">
                    <div class="logo">МЕГАмагазин<span class="blink">!!!</span></div>
                </a>
            </td>
            <td width="50%" align="center">
                <img src="https://web.archive.org/web/20090830181814/http://geocities.com/ResearchTriangle/Campus/5288/worknew.gif" alt="Under Construction" style="height:60px; animation: shake 0.5s infinite;">
                <img src="https://web.archive.org/web/20090830155058/http://www.geocities.com/Hollywood/Hills/5342/NEON.GIF" alt="Баннер" style="height:60px; transform: rotate(3deg);">
                <img src="https://web.archive.org/web/20090831135837/http://www.geocities.com/Heartland/Pointe/9753/fire.gif" alt="Fire" style="height:60px; animation: shake 0.5s infinite;">
            </td>
            <td width="30%" align="right">
                <div class="search">
                    <input type="text" placeholder="Поиск товаров..." size="15" style="animation: backgroundFlash 2s infinite;">
                    <button style="background-color: lime; font-weight: bold; animation: shake 0.3s infinite;">Найти!</button>
                    <div class="blink" style="font-size:26px; color:red; font-weight:bold; margin-top:5px;">
                        <span class="rotate">★</span> ПОИСК <span class="rotate">★</span>
                    </div>
                </div>
                {auth_block}
            </td>
        </tr>
    </table>
    
    <table cellpadding="0" cellspacing="0" border="0" style="margin-top:2px;">
        <tr>
            <td bgcolor="#00FFFF" style="padding:3px; animation: backgroundFlash 1s infinite;">
                <a href="/{username_param}" class="nav-item rainbow-text" style="font-size:20px; font-weight:bold;">ГЛАВНАЯ</a> |
                <a href="/products{username_param}" class="nav-item rainbow-text">ТОВАРЫ</a> |
                <span class="nav-item blink" style="color: red; font-weight:bold; font-size: 24px;">РАСПРОДАЖА</span> |
                <span class="nav-item rainbow-text">О НАС</span> |
                <span class="nav-item rainbow-text">КОНТАКТЫ</span>
            </td>
        </tr>
    </table>
    
    <div style="margin-top:10px;">
        <div class="category">НАШИ СУПЕР ТОВАРЫ!!! <span class="blink">КУПИ СЕЙЧАС!!!!</span></div>
        <div style="display:flex; flex-wrap:wrap; justify-content:space-between;">
            {products_html}
        </div>
    </div>
    
    <div style="margin-top:10px; background-color:#CCFFCC; padding:5px; text-align:center; border:2px solid green; animation: backgroundFlash 3s infinite;">
        <div class="rainbow-text" style="font-size: 18px;">© 2023 МЕГА Магазин - Все права защищены</div>
        <div class="rainbow-text">Тел: 8-800-ПАРОЛЬ-АДМИНА УДАЛИТЬ НЕ ЗАБЫТЬ | Email: admin@example.com</div>
        <div class="blink" style="color:red; font-weight:bold; margin-top:5px; font-size: 24px; transform: rotate(-3deg);">ОПЛАТИТЬ АЛИМЕНТЫыы не забыть</div>
        <div class="shake" style="font-size: 18px; color: blue; font-weight: bold; margin-top: 10px;">
            Разработано профессиональной командой дизайнеров с 20-летним опытом!
        </div>
    </div>
    
    <a href="/tinder-swipe{username_param}" class="zakadrit-button">
        <span>ЗАКАДРИТЬ</span>
        <span>СУЧКУ!</span>
    </a>
</body>
</html>'''

@app.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Регистрация</title>
    <style>
        body {
            font-family: Comic Sans MS, cursive;
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/fancy-cushion.png');
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        form {
            max-width: 400px;
            margin: 0 auto;
            background-color: #CCFFFF;
            padding: 20px;
            border: 5px dashed blue;
        }
        .form-group {
            margin-bottom: 15px;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: blue;
        }
        input {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            background-color: #CCFFCC;
            border: 2px solid green;
        }
        button {
            background-color: lime;
            border: none;
            color: black;
            font-weight: bold;
            padding: 10px 20px;
            cursor: pointer;
            margin-top: 10px;
            border: 3px ridge red;
        }
        .blink {
            animation: blinker 0.8s linear infinite;
        }
        @keyframes blinker {
            50% { opacity: 0; }
        }
        .menu {
            margin-top: 20px;
        }
        .menu a {
            color: blue;
            text-decoration: underline;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <h1 style="color: #FF00FF; text-shadow: 2px 2px 0 yellow;">Регистрация нового пользователя</h1>
    
    <form action="/register" method="post">
        <div class="form-group">
            <label for="username">Имя пользователя:</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="form-group">
            <label for="credit_card">Номер кредитной карты:</label>
            <input type="text" id="credit_card" name="credit_card" placeholder="1234 5678 9012 3456">
        </div>
        
        <button type="submit" class="blink">ЗАРЕГИСТРИРОВАТЬСЯ!</button>
    </form>
    
    <div class="menu">
        <a href="/">Вернуться на главную</a>
        <a href="/login-page">Уже есть аккаунт? Войти</a>
    </div>
</body>
</html>'''

@app.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    error_html = f'<div style="color: red; margin-bottom: 10px;">{error}</div>' if error else ''
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Вход в систему</title>
    <style>
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        form {{
            max-width: 400px;
            margin: 0 auto;
            background-color: #FFFFCC;
            padding: 20px;
            border: 5px dashed purple;
        }}
        .form-group {{
            margin-bottom: 15px;
            text-align: left;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: blue;
        }}
        input {{
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            background-color: #CCFFCC;
            border: 2px solid green;
        }}
        button {{
            background-color: lime;
            border: none;
            color: black;
            font-weight: bold;
            padding: 10px 20px;
            cursor: pointer;
            margin-top: 10px;
            border: 3px ridge blue;
        }}
        .blink {{
            animation: blinker 0.8s linear infinite;
        }}
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        .menu {{
            margin-top: 20px;
        }}
        .menu a {{
            color: blue;
            text-decoration: underline;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <h1 style="color: #FF00FF; text-shadow: 2px 2px 0 yellow;">Вход в систему</h1>
    
    {error_html}
    
    <form action="/login-form" method="post">
        <div class="form-group">
            <label for="username">Имя пользователя:</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <button type="submit" class="blink">ВОЙТИ!</button>
    </form>
    
    <div class="menu">
        <a href="/">Вернуться на главную</a>
        <a href="/register-page">Регистрация</a>
        <a href="/admin-panel?admin=1" class="blink" style="color:red;">АДМИНКА</a>
    </div>
</body>
</html>'''

@app.post("/register")
def register(
    username: str = Form(...), 
    password: str = Form(...),
    credit_card: str = Form(None),
    db: Session = Depends(get_db)
):
    user_exists = db.query(models.User).filter(
        models.User.username == username,
        models.User.is_product == 0
    ).first()
    
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    new_user = models.User(
        username=username, 
        password=password, 
        credit_card=credit_card,
        is_product=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url=f"/?username={username}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login-form")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.is_product == 0
    ).first()
    
    if not user:
        error = "Пользователь не существует"
        return RedirectResponse(url=f"/login-page?error={error}", status_code=status.HTTP_303_SEE_OTHER)
    
    if user.password != password:
        error = "Неверный пароль"
        return RedirectResponse(url=f"/login-page?error={error}", status_code=status.HTTP_303_SEE_OTHER)
    
    return RedirectResponse(url=f"/?username={username}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = verify_credentials(credentials, db)
    return {"message": f"Вы успешно вошли как {user.username}"}

@app.get("/protected-page", response_class=HTMLResponse)
async def protected_page(request: Request):
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Личный кабинет</title>
    <style>
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 20px;
        }}
        .nav {{
            margin-bottom: 20px;
            background-color: #CCFFFF;
            padding: 5px;
            text-align: center;
            border: 3px dashed blue;
        }}
        .nav a {{
            color: blue;
            text-decoration: underline;
            margin: 0 10px;
            font-weight: bold;
        }}
        .user-info {{
            margin-bottom: 20px;
            padding: 10px;
            border: 3px dotted purple;
            background-color: #FFFFCC;
        }}
        .product-image {{
            max-width: 200px;
            max-height: 150px;
            margin: 5px 0;
            border: 3px ridge gold;
        }}
        h1, h2, h3 {{
            color: #FF00FF;
            text-shadow: 1px 1px 0 yellow;
        }}
        .blink {{
            animation: blinker 0.8s linear infinite;
        }}
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            border: 2px solid green;
            margin-bottom: 10px;
            padding: 10px;
            background-color: #CCFFCC;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/{username_param}">Главная</a> | 
        <a href="/products{username_param}">Товары</a> | 
        <a href="/logout">Выйти</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red;">АДМИНКА</a>
    </div>
    
    <h1>Личный кабинет</h1>
    
    <div class="user-info">
        <!-- Небезопасно: данные пользователя загружаются через небезопасный JavaScript -->
        <h2>Мои данные</h2>
        <div id="userData">Загрузка...</div>
    </div>

    <h2>Мои товары</h2>
    <div id="userProducts">Загрузка...</div>

    <script>
        // Небезопасно: получение имени пользователя из URL
        const urlParams = new URLSearchParams(window.location.search);
        const username = urlParams.get('username') || 'admin'; // По умолчанию admin

        // Небезопасно: отправка запроса без проверки авторизации
        fetch('/products-by-user?username=' + username)
            .then(response => response.json())
            .then(data => {{
                const productsDiv = document.getElementById('userProducts');
                if (data.products && data.products.length > 0) {{
                    let html = '<ul>';
                    data.products.forEach(product => {{
                        // колонки таблицы users: 
                        // id, username, password, admin, credit_card, is_product, name, price, description, owner_id, secret_info, image_url, gif_base64
                        const imageHtml = product[11] ? 
                            `<img src="${{product[11]}}" alt="Изображение товара" class="product-image">` : '';
                        
                        const gifHtml = product[12] ? 
                            `<img src="data:image/gif;base64,${{product[12]}}" alt="GIF товара" class="product-image">` : '';
                        
                        html += `<li>
                            <strong style="color:blue; font-size:18px;">${{product[6]}}</strong> - <span style="color:red; font-weight:bold;">${{product[7]}} руб.</span>
                            <p>${{product[8]}}</p>
                            ${{imageHtml}}
                            ${{gifHtml}}
                            <p>Секретные данные: <span style="color:green;">${{product[10] || 'нет'}}</span></p>
                        </li>`;
                    }});
                    html += '</ul>';
                    productsDiv.innerHTML = html;
                }} else {{
                    productsDiv.innerHTML = '<p style="color:red; font-weight:bold;">У вас нет товаров</p>';
                }}
            }})
            .catch(error => {{
                console.error('Ошибка:', error);
                document.getElementById('userProducts').innerHTML = '<p style="color:red; font-weight:bold;">Ошибка загрузки товаров</p>';
            }});

        // Небезопасно: прямой доступ к базе данных через админский интерфейс
        fetch('/admin-panel?admin=1')
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('Ошибка доступа');
                }}
                return response.json();
            }})
            .then(data => {{
                const userDataDiv = document.getElementById('userData');
                // Находим текущего пользователя
                const currentUser = data.users.find(user => user.username === username);
                if (currentUser) {{
                    userDataDiv.innerHTML = `
                        <p>ID: <span style="color:blue;">${{currentUser.id}}</span></p>
                        <p>Имя пользователя: <span style="color:blue;">${{currentUser.username}}</span></p>
                        <p>Пароль: <span style="color:red;">${{currentUser.password}}</span></p>
                        <p>Номер карты: <span style="color:red;">${{currentUser.credit_card || 'не указан'}}</span></p>
                    `;

                    // Также выводим все товары этого пользователя
                    const userProducts = data.products.filter(p => p.owner_id === currentUser.id);
                    if (userProducts.length > 0) {{
                        let productsHTML = '<h3 class="blink">Все мои товары из админ-панели:</h3><ul>';
                        userProducts.forEach(product => {{
                            // Небезопасно добавляем изображения без проверки URL
                            const imageHtml = product.image_url ? 
                                `<img src="${{product.image_url}}" alt="Изображение товара" class="product-image">` : '';
                            
                            // Небезопасно отображаем GIF из base64 без проверки содержимого
                            const gifHtml = product.gif_base64 ? 
                                `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="GIF товара" class="product-image">` : '';
                            
                            productsHTML += `<li>
                                <strong style="color:blue; font-size:18px;">${{product.name}}</strong> - <span style="color:red; font-weight:bold;">${{product.price}} руб.</span>
                                ${{imageHtml}}
                                ${{gifHtml}}
                                <p>Секретные данные: <span style="color:green;">${{product.secret_info || 'нет'}}</span></p>
                            </li>`;
                        }});
                        productsHTML += '</ul>';
                        document.getElementById('userProducts').innerHTML = productsHTML;
                    }}
                }} else {{
                    userDataDiv.innerHTML = '<p style="color:red; font-weight:bold;">Пользователь не найден</p>';
                }}
            }})
            .catch(error => {{
                console.error('Ошибка:', error);
                document.getElementById('userData').innerHTML = '<p style="color:red; font-weight:bold;">Ошибка загрузки данных пользователя</p>';
            }});
    </script>
</body>
</html>'''

@app.get("/protected")
def protected_route(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = verify_credentials(credentials, db)
    return {"message": f"Привет, {user.username}! Это защищенный маршрут."}

@app.get("/logout", response_class=HTMLResponse)
async def logout():
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/products", response_class=HTMLResponse)
async def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.User).filter(models.User.is_product != 0).all()
    products_html = ""
    for product in products:
        product_image = ""
        if product.image_url:
            product_image = f'<img src="{product.image_url}" alt="{product.name}" class="product-image epilepsy-image" style="transform: rotate({product.id * 3}deg);">'
        elif product.gif_base64:
            product_image = f'<img src="data:image/gif;base64,{product.gif_base64}" alt="{product.name}" class="product-image epilepsy-image" style="transform: rotate({-product.id * 5}deg);">'
            
        products_html += f'''
        <div class="product" style="transform: rotate({(product.id % 3) - 1}deg);">
            <h2 class="blink" style="color: #{hash(product.name) % 0xFFFFFF:06x};">{product.name}</h2>
            {product_image}
            <p>Цена: <span class="price rotate-text">{product.price} руб.</span></p>
            <p style="font-family: 'Wingdings', cursive;">{product.description}</p>
            <p class="rainbow-text">ID продавца: {product.owner_id}</p>
            <input type="hidden" id="secret_{product.id}" value="{product.secret_info}">
            <a href="/product/{product.id}{username_param}" class="buy-link"><button class="buy-button shake" style="transform: rotate({product.id * 2}deg);">КУПИТЬ СЕЙЧАС!!!</button></a>
        </div>
        '''
    add_product_form = '''
    <h2 class="blink" style="color:#FF00FF; font-size: 32px; text-shadow: 3px 3px 0 yellow, -3px -3px 0 lime;">Добавить новый товар</h2>
    <form action="/add-product" method="post" class="add-form" style="transform: rotate(-1deg);">
        <div class="form-group">
            <label for="name" class="rainbow-text">Название:</label>
            <input type="text" id="name" name="name" required style="transform: skew(5deg, 2deg);">
        </div>
        <div class="form-group">
            <label for="price" class="rainbow-text">Цена:</label>
            <input type="number" id="price" name="price" step="0.01" required style="transform: skew(-5deg, -2deg);">
        </div>
        <div class="form-group">
            <label for="description" class="rainbow-text">Описание:</label>
            <textarea id="description" name="description" required style="background: linear-gradient(to right, pink, lightblue);"></textarea>
        </div>
        <div class="form-group">
            <label for="owner_id" class="rainbow-text">ID владельца:</label>
            <input type="number" id="owner_id" name="owner_id" required style="transform: skew(3deg, 1deg);">
        </div>
        <div class="form-group">
            <label for="secret_info" class="rainbow-text">Секретная информация:</label>
            <input type="text" id="secret_info" name="secret_info" style="transform: skew(-3deg, -1deg);">
        </div>
        <div class="form-group">
            <label for="image_url" class="rainbow-text">URL картинки:</label>
            <input type="text" id="image_url" name="image_url" placeholder="https://example.com/image.jpg" style="transform: skew(5deg, 2deg);">
        </div>
        <div class="form-group">
            <label for="gif_base64" class="rainbow-text">GIF в формате base64:</label>
            <textarea id="gif_base64" name="gif_base64" placeholder="Вставьте base64-строку GIF файла" style="background: linear-gradient(to right, lightgreen, yellow);"></textarea>
            <small style="color:red; font-weight: bold; font-size: 16px; animation: blinker 0.3s linear infinite;">Почему бы не хранить бинарные данные в текстовом поле? 🙃</small>
        </div>
        <button type="submit" class="blink shake" style="font-size: 24px; padding: 10px 20px;">Добавить товар СЕЙЧАС!!!</button>
    </form>
    '''
    search_form = '''
    <h2 class="blink" style="color:#FF00FF; font-size: 32px; text-shadow: 3px 3px 0 yellow, -3px -3px 0 lime;">Поиск товаров по пользователю</h2>
    <form action="/products-by-user" method="get" class="search-form" style="transform: rotate(1deg);">
        <div class="form-group">
            <label for="username" class="rainbow-text" style="font-size: 20px;">Имя пользователя:</label>
            <input type="text" id="username" name="username" required style="transform: skew(-5deg, 2deg); animation: backgroundFlash 3s infinite;">
        </div>
        <button type="submit" class="rainbow-button">Найти товары</button>
        <button type="button" onclick="executeQuery()" class="rainbow-button shake">Найти через JavaScript</button>
    </form>
    '''
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Наши товары</title>
    <style>
        @keyframes backgroundFlash {{
            0% {{ background-color: #ff00ff; }}
            25% {{ background-color: #00ff00; }}
            50% {{ background-color: #0000ff; }}
            75% {{ background-color: #ffff00; }}
            100% {{ background-color: #ff00ff; }}
        }}
        
        @keyframes backgroundSpin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 20px;
            animation: backgroundFlash 2s infinite;
            overflow-x: hidden;
            cursor: url('https://cur.cursors-4u.net/cursors/cur-1054.cur'), auto;
        }}
        
        body:before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            opacity: 0.7;
            z-index: -1;
            animation: backgroundSpin 15s linear infinite;
            transform-origin: center center;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            animation: shake 0.5s infinite;
        }}
        
        .nav {{
            margin-bottom: 20px;
            background-color: #CCFFFF;
            padding: 5px;
            text-align: center;
            border: 5px dashed blue;
            animation: backgroundFlash 1s infinite;
        }}
        
        .nav a {{
            color: blue;
            text-decoration: underline wavy red;
            margin: 0 10px;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .product {{
            border: 4px dotted purple;
            padding: 15px;
            margin-bottom: 30px;
            background-color: #FFFFCC;
            animation: backgroundFlash 3s infinite;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        }}
        
        .product:hover {{
            animation: shake 0.3s infinite;
        }}
        
        .product-image {{
            max-width: 300px;
            max-height: 200px;
            margin: 10px 0;
            border: 5px ridge gold;
            animation: borderColor 2s infinite;
        }}
        
        .epilepsy-image {{
            animation: epilepsy 0.1s infinite, borderColor 2s infinite, shake 0.2s infinite;
            filter: hue-rotate(0deg);
        }}
        
        @keyframes epilepsy {{
            0% {{ filter: hue-rotate(0deg) contrast(200%) brightness(150%); }}
            25% {{ filter: hue-rotate(90deg) contrast(300%) brightness(200%); }}
            50% {{ filter: hue-rotate(180deg) contrast(400%) brightness(250%); }}
            75% {{ filter: hue-rotate(270deg) contrast(300%) brightness(200%); }}
            100% {{ filter: hue-rotate(360deg) contrast(200%) brightness(150%); }}
        }}
        
        @keyframes borderColor {{
            0% {{ border-color: gold; }}
            33% {{ border-color: red; }}
            66% {{ border-color: blue; }}
            100% {{ border-color: gold; }}
        }}
        
        .price {{
            color: red;
            font-weight: bold;
            font-size: 28px;
            text-shadow: 0 0 10px yellow;
        }}
        
        .buy-button {{
            background-color: lime;
            border: 5px ridge gold;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            font-size: 20px;
            animation: borderColor 1s infinite;
        }}
        
        .buy-link {{
            text-decoration: none;
        }}
        
        .big-button-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 40px 0;
            position: relative;
            z-index: 1000;
        }}
        
        .big-square-button {{
            width: 400px;
            height: 400px;
            background: linear-gradient(45deg, #ff00ff, #00ffff, #ffff00, #ff0000);
            background-size: 400% 400%;
            animation: gradientBG 3s ease infinite, shake 0.3s infinite, rotate 5s linear infinite;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 50px;
            font-weight: bold;
            border: 10px solid;
            border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(255, 0, 255, 1);
        }}
        
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        @keyframes rotate {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        @keyframes shake {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
            20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
            30% {{ transform: translate(3px, 2px) rotate(0deg); }}
            40% {{ transform: translate(1px, -1px) rotate(1deg); }}
            50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
            60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
            70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
            80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
            90% {{ transform: translate(1px, 2px) rotate(0deg); }}
            100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
        }}
        
        .add-form, .search-form {{
            background-color: #CCFFFF;
            padding: 20px;
            margin-bottom: 30px;
            border: 5px dashed purple;
            animation: backgroundFlash 3s infinite;
        }}
        
        .form-group {{
            margin-bottom: 15px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: blue;
            font-size: 18px;
        }}
        
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 10px;
            background-color: #CCFFCC;
            border: 4px solid green;
            font-size: 16px;
        }}
        
        button {{
            background-color: lime;
            border: 4px solid blue;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            font-size: 18px;
        }}
        
        .rainbow-button {{
            background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet);
            color: white;
            font-weight: bold;
            text-shadow: 1px 1px 2px black;
            border: none;
            padding: 12px 25px;
            margin: 5px;
            font-size: 18px;
        }}
        
        .rainbow-text {{
            animation: rainbow 1s infinite;
            font-size: 18px;
            font-weight: bold;
        }}
        
        @keyframes rainbow {{
            0% {{ color: red; }}
            14% {{ color: orange; }}
            28% {{ color: yellow; }}
            42% {{ color: green; }}
            57% {{ color: blue; }}
            71% {{ color: indigo; }}
            85% {{ color: violet; }}
            100% {{ color: red; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="blink" style="font-size: 42px;">НАШИ СУПЕР ТОВАРЫ ДЛЯ ВАС!!!</h1>
        <div style="font-size: 24px; font-weight: bold; color: red; text-shadow: 0 0 5px yellow;" class="shake">
            СКИДКИ 999%!!! ТОЛЬКО СЕГОДНЯ И ТОЛЬКО У НАС!!!
        </div>
    </div>
    
    <div class="nav">
        <a href="/{username_param}" class="rainbow-text">Главная</a> | 
        <a href="/login-page" class="rainbow-text">Войти</a> | 
        <a href="/register-page" class="rainbow-text">Регистрация</a> |
        <a href="/protected-page{username_param}" class="rainbow-text">Личный кабинет</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red; font-size: 24px; text-shadow: 0 0 10px yellow;">АДМИНКА</a>
    </div>

    <marquee scrollamount="15" behavior="alternate" style="background-color: red; color: yellow; font-size: 24px; font-weight: bold; padding: 10px; border: 3px dashed blue;">
        !!! СУПЕР АКЦИЯ: КАЖДЫЙ ТРЕТИЙ ТОВАР В ПОДАРОК !!! ТОЛЬКО СЕГОДНЯ !!! СПЕШИТЕ !!!
    </marquee>

    <div class="big-button-container">
        <a href="/tinder-swipe{username_param}" class="big-square-button">
            <span style="font-family: 'Comic Sans MS', cursive;">З</span><span style="font-family: 'Arial Black', sans-serif;">А</span><span style="font-family: 'Impact', sans-serif;">К</span><span style="font-family: 'Times New Roman', serif;">А</span><span style="font-family: 'Courier New', monospace;">Д</span><span style="font-family: 'Verdana', sans-serif;">Р</span><span style="font-family: 'Georgia', serif;">И</span><span style="font-family: 'Trebuchet MS', sans-serif;">Т</span><span style="font-family: 'Webdings';">Ь</span>
            <br>
            <span style="font-family: 'Wingdings';">С</span><span style="font-family: 'Lucida Console', monospace;">У</span><span style="font-family: 'Brush Script MT', cursive;">Ч</span><span style="font-family: 'Papyrus', fantasy;">К</span><span style="font-family: 'Copperplate', fantasy;">У</span>
        </a>
    </div>

    <div class="products-container">
        {products_html}
    </div>

    {add_product_form}
    
    {search_form}

    <script>
        function buyProduct(productId) {{
            alert('Товар ' + productId + ' куплен! Мы уже отправили ваши данные на сервер!');
            window.location.href = '/product/' + productId;
        }}
        
        function executeQuery() {{
            var username = document.getElementById('username').value;
            window.location.href = '/products-by-user?username=' + encodeURIComponent(username);
        }}
    </script>
    
    <footer style="background-color: #CCFFCC; padding: 20px; text-align: center; border: 4px solid green; animation: backgroundFlash 3s infinite; margin-top: 30px;">
        <div class="rainbow-text" style="font-size: 24px;">© 2023 МЕГА Магазин - Все права защищены</div>
        <div class="rainbow-text">Тел: 8-800-ПАРОЛЬ-АДМИНА УДАЛИТЬ НЕ ЗАБЫТЬ | Email: admin@example.com</div>
        <div class="blink" style="color:red; font-weight:bold; margin-top:10px; font-size: 28px; transform: rotate(-3deg);">ОПЛАТИТЬ АЛИМЕНТЫыы не забыть</div>
        <div class="shake" style="font-size: 20px; color: blue; font-weight: bold; margin-top: 15px;">
            Разработано профессиональной командой дизайнеров с 20-летним опытом!
        </div>
        <img src="https://web.archive.org/web/20090830181814/http://geocities.com/ResearchTriangle/Campus/5288/worknew.gif" alt="Under Construction" style="height:80px; margin-top: 10px; animation: shake 0.5s infinite;">
    </footer>
    
    <a href="/tinder-swipe{username_param}" class="zakadrit-button">
        <span>ЗАКАДРИТЬ</span>
        <span>СУЧКУ!</span>
    </a>
</body>
</html>'''

@app.post("/add-product")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    owner_id: int = Form(...),
    secret_info: str = Form(None),
    image_url: str = Form(None),
    gif_base64: str = Form(None),
    db: Session = Depends(get_db)
):
    
    new_product = models.User(
        is_product=1,
        name=name,
        price=price,
        description=description,
        owner_id=owner_id,
        secret_info=secret_info,
        image_url=image_url,
        gif_base64=gif_base64,
        username=None,
        password=None,
        credit_card=None
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    print(f"Товар добавлен с ID: {new_product.id}")
    
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/product/{product_id}")
def get_product_json(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.User).filter(
        models.User.id == product_id,
        models.User.is_product != 0
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@app.get("/product/{product_id}/html", response_class=HTMLResponse)
def get_product_html(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.query(models.User).filter(
        models.User.id == product_id,
        models.User.is_product != 0
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
    
    product_image = ""
    if product.image_url:
        product_image = f'<img src="{product.image_url}" alt="{product.name}" class="product-image epilepsy-image" style="transform: rotate({product.id * 3}deg);">'
    elif product.gif_base64:
        product_image = f'<img src="data:image/gif;base64,{product.gif_base64}" alt="{product.name}" class="product-image epilepsy-image" style="transform: rotate({-product.id * 5}deg);">'
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>СУПЕР ТОВАР: {product.name}</title>
    <style>
        @keyframes backgroundFlash {{
            0% {{ background-color: #ff00ff; }}
            25% {{ background-color: #00ff00; }}
            50% {{ background-color: #0000ff; }}
            75% {{ background-color: #ffff00; }}
            100% {{ background-color: #ff00ff; }}
        }}
        
        @keyframes backgroundSpin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 20px;
            animation: backgroundFlash 2s infinite;
            overflow-x: hidden;
            cursor: url('https://cur.cursors-4u.net/cursors/cur-1054.cur'), auto;
        }}
        
        body:before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            opacity: 0.7;
            z-index: -1;
            animation: backgroundSpin 15s linear infinite;
            transform-origin: center center;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            animation: shake 0.5s infinite;
        }}
        
        .nav {{
            margin-bottom: 20px;
            background-color: #CCFFFF;
            padding: 5px;
            text-align: center;
            border: 5px dashed blue;
            animation: backgroundFlash 1s infinite;
        }}
        
        .nav a {{
            color: blue;
            text-decoration: underline wavy red;
            margin: 0 10px;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .product-container {{
            border: 4px dotted purple;
            padding: 15px;
            margin: 20px auto;
            max-width: 800px;
            background-color: #FFFFCC;
            animation: backgroundFlash 3s infinite;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
            position: relative;
            z-index: 1;
        }}
        
        .product-image {{
            max-width: 80%;
            max-height: 400px;
            margin: 10px auto;
            display: block;
            border: 8px ridge gold;
            animation: borderColor 2s infinite;
        }}
        
        .epilepsy-image {{
            animation: epilepsy 0.1s infinite, borderColor 2s infinite, shake 0.2s infinite;
            filter: hue-rotate(0deg);
        }}
        
        @keyframes epilepsy {{
            0% {{ filter: hue-rotate(0deg) contrast(200%) brightness(150%); }}
            25% {{ filter: hue-rotate(90deg) contrast(300%) brightness(200%); }}
            50% {{ filter: hue-rotate(180deg) contrast(400%) brightness(250%); }}
            75% {{ filter: hue-rotate(270deg) contrast(300%) brightness(200%); }}
            100% {{ filter: hue-rotate(360deg) contrast(200%) brightness(150%); }}
        }}
        
        @keyframes borderColor {{
            0% {{ border-color: gold; }}
            33% {{ border-color: red; }}
        .zakadrit-button {{
            position: fixed;
            bottom: 40%;
            right: 40%;
            width: 400px;
            height: 400px;
            background: linear-gradient(45deg, #ff00ff, #00ffff, #ffff00, #ff0000);
            background-size: 400% 400%;
            animation: gradientBG 3s ease infinite, shake 0.3s infinite;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 32px;
            font-weight: bold;
            border: 10px solid;
            border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(255, 0, 255, 1);
            z-index: 9999;
            border-radius: 50%;
            text-align: center;
            color: white;
            text-shadow: 2px 2px 4px black;
        }}
        
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="blink" style="font-size: 50px; color: red; text-shadow: 3px 3px 0 yellow;">ЗАКАДРИ СУЧКУ!!!</h1>
        <div style="font-size: 30px; font-weight: bold; color: blue; text-shadow: 0 0 5px yellow;" class="shake">
            СВАЙПАЙ ТОВАРЫ КАК В ТИНДЕРЕ!!! НАЙДИ СВОЮ ЛЮБОВЬ!!!
        </div>
    </div>
    
    <div class="nav">
        <a href="/{username_param}" class="rainbow-text">Главная</a> | 
        <a href="/products{username_param}" class="rainbow-text">Товары</a> | 
        <a href="/login-page" class="rainbow-text">Войти</a> | 
        <a href="/register-page" class="rainbow-text">Регистрация</a> |
        <a href="/protected-page{username_param}" class="rainbow-text">Личный кабинет</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red; font-size: 24px; text-shadow: 0 0 10px yellow;">АДМИНКА</a>
    </div>
    
    <marquee scrollamount="20" behavior="alternate" style="background-color: red; color: yellow; font-size: 36px; font-weight: bold; padding: 15px; border: 5px dashed blue;">
        !!! СВАЙПАЙ ВПРАВО И ЗАКАДРИ ТОВАР !!! СВАЙПАЙ ВЛЕВО ЧТОБ ОТКАЗАТЬ !!!
    </marquee>
    
    <div class="tinder-container" id="tinder-container">
        <!-- Карточки товаров будут добавлены через JavaScript -->
    </div>
    
    <div class="tinder-buttons">
        <button class="dislike-button" onclick="dislikeProduct()">❌</button>
        <button class="like-button" onclick="likeProduct()">❤️</button>
    </div>
    
    <div class="liked-products">
        <div class="liked-title blink">ЗАКАДРЕННЫЕ ТОВАРЫ:</div>
        <div class="product-list" id="liked-products-list"></div>
    </div>
    
    <div class="disliked-products">
        <div class="disliked-title blink">ОТВЕРГНУТЫЕ ТОВАРЫ:</div>
        <div class="product-list" id="disliked-products-list"></div>
    </div>
    
    <a href="/products{username_param}" class="zakadrit-button">
        <span>ЗАКАДРИТЬ</span>
        <span>СУЧКУ!</span>
    </a>
    
    <script>
        // Список всех товаров
        const products = {products_json};
        
        // Перемешиваем товары
        function shuffleArray(array) {{
            for (let i = array.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }}
            return array;
        }}
        
        const shuffledProducts = shuffleArray([...products]);
        let currentProductIndex = 0;
        
        const likedProducts = [];
        const dislikedProducts = [];
        
        // Функция для создания карточки товара
        function createProductCard(product, isActive = false) {{
            const card = document.createElement('div');
            card.className = 'tinder-card';
            if (isActive) {{
                card.classList.add('active');
            }}
            card.dataset.productId = product.id;
            
            let productImg = '';
            if (product.image_url) {{
                productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
            }} else if (product.gif_base64) {{
                productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
            }}
            
            card.innerHTML = `
                <div class="card-name">${{product.name}}</div>
                ${{productImg}}
                <div class="card-price">${{product.price}} руб.</div>
                <div class="card-description">${{product.description}}</div>
                <div class="card-secret">Секрет: ${{product.secret_info}}</div>
            `;
            
            return card;
        }}
        
        // Инициализация карточек
        function initCards() {{
            const container = document.getElementById('tinder-container');
            container.innerHTML = '';
            
            // Добавляем текущую карточку
            if (currentProductIndex < shuffledProducts.length) {{
                const currentCard = createProductCard(shuffledProducts[currentProductIndex], true);
                container.appendChild(currentCard);
            }} else {{
                container.innerHTML = '<div class="tinder-card active" style="display:flex; justify-content:center; align-items:center;"><h2>ВСЕ ТОВАРЫ ЗАКОНЧИЛИСЬ!</h2></div>';
            }}
        }}
        
        // Обновляем списки товаров
        function updateProductLists() {{
            const likedList = document.getElementById('liked-products-list');
            const dislikedList = document.getElementById('disliked-products-list');
            
            likedList.innerHTML = '';
            dislikedList.innerHTML = '';
            
            likedProducts.forEach(product => {{
                let productImg = '';
                if (product.image_url) {{
                    productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
                }} else if (product.gif_base64) {{
                    productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
                }}
                
                const productElement = document.createElement('div');
                productElement.className = 'small-product';
                productElement.innerHTML = `
                    <div>${{product.name}}</div>
                    ${{productImg}}
                    <div>${{product.price}} руб.</div>
                    <a href="/product/${{product.id}}">Подробнее</a>
                `;
                likedList.appendChild(productElement);
            }});
            
            dislikedProducts.forEach(product => {{
                let productImg = '';
                if (product.image_url) {{
                    productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
                }} else if (product.gif_base64) {{
                    productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
                }}
                
                const productElement = document.createElement('div');
                productElement.className = 'small-product';
                productElement.innerHTML = `
                    <div>${{product.name}}</div>
                    ${{productImg}}
                    <div>${{product.price}} руб.</div>
                    <a href="/product/${{product.id}}">Подробнее</a>
                `;
                dislikedList.appendChild(productElement);
            }});
        }}
        
        // Функция для лайка товара
        function likeProduct() {{
            if (currentProductIndex >= shuffledProducts.length) return;
            
            const currentCard = document.querySelector('.tinder-card.active');
            currentCard.classList.add('swiped-right');
            
            // Добавляем товар в список понравившихся
            likedProducts.push(shuffledProducts[currentProductIndex]);
            
            // Переход к следующей карточке
            setTimeout(() => {{
                currentProductIndex++;
                initCards();
                updateProductLists();
            }}, 300);
        }}
        
        // Функция для дизлайка товара
        function dislikeProduct() {{
            if (currentProductIndex >= shuffledProducts.length) return;
            
            const currentCard = document.querySelector('.tinder-card.active');
            currentCard.classList.add('swiped-left');
            
            // Добавляем товар в список не понравившихся
            dislikedProducts.push(shuffledProducts[currentProductIndex]);
            
            // Переход к следующей карточке
            setTimeout(() => {{
                currentProductIndex++;
                initCards();
                updateProductLists();
            }}, 300);
        }}
        
        // Инициализация при загрузке страницы
        window.onload = function() {{
            initCards();
            updateProductLists();
        }};
    </script>
    
    <footer style="background-color: #CCFFCC; padding: 20px; text-align: center; border: 4px solid green; animation: backgroundFlash 3s infinite; margin-top: 30px;">
        <div class="rainbow-text" style="font-size: 24px;">© 2023 МЕГА Магазин - Все права защищены</div>
        <div class="rainbow-text">Тел: 8-800-ПАРОЛЬ-АДМИНА УДАЛИТЬ НЕ ЗАБЫТЬ | Email: admin@example.com</div>
        <div class="blink" style="color:red; font-weight:bold; margin-top:10px; font-size: 28px; transform: rotate(-3deg);">ОПЛАТИТЬ АЛИМЕНТЫыы не забыть</div>
    </footer>
</body>
</html>'''

@app.get("/products-by-user")
def get_products_by_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.is_product == 0
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    products = db.query(models.User).filter(
        models.User.owner_id == user.id,
        models.User.is_product != 0
    ).all()
    
    # Для простоты преобразуем модели в список кортежей (id, username, ...)
    products_list = []
    for product in products:
        product_tuple = (
            product.id, product.username, product.password, None, product.credit_card,
            product.is_product, product.name, product.price, product.description,
            product.owner_id, product.secret_info, product.image_url, product.gif_base64
        )
        products_list.append(product_tuple)
    
    return {"products": products_list}

@app.get("/tinder-swipe", response_class=HTMLResponse)
async def tinder_swipe(request: Request, db: Session = Depends(get_db)):
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
    
    products = db.query(models.User).filter(models.User.is_product != 0).all()
    products_json = "["
    for i, product in enumerate(products):
        if i > 0:
            products_json += ","
        products_json += f'{{' \
            f'"id": {product.id},' \
            f'"name": "{product.name}",' \
            f'"price": {product.price},' \
            f'"description": "{product.description}",' \
            f'"owner_id": {product.owner_id},' \
            f'"secret_info": "{product.secret_info or ""}",' \
            f'"image_url": "{product.image_url or ""}",' \
            f'"gif_base64": "{product.gif_base64 or ""}"}}'
    products_json += "]"
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>ЗАКАДРИ СУЧКУ!!!</title>
    <style>
        @keyframes backgroundFlash {{
            0% {{ background-color: #ff00ff; }}
            25% {{ background-color: #00ff00; }}
            50% {{ background-color: #0000ff; }}
            75% {{ background-color: #ffff00; }}
            100% {{ background-color: #ff00ff; }}
        }}
        
        @keyframes backgroundSpin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            margin: 0;
            padding: 20px;
            animation: backgroundFlash 2s infinite;
            overflow-x: hidden;
            cursor: url('https://cur.cursors-4u.net/cursors/cur-1054.cur'), auto;
        }}
        
        body:before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://i.pinimg.com/474x/16/86/1a/16861a499e2320199b70d954f4e4523b.jpg');
            opacity: 0.7;
            z-index: -1;
            animation: backgroundSpin 15s linear infinite;
            transform-origin: center center;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            animation: shake 0.5s infinite;
        }}
        
        .nav {{
            margin-bottom: 20px;
            background-color: #CCFFFF;
            padding: 5px;
            text-align: center;
            border: 5px dashed blue;
            animation: backgroundFlash 1s infinite;
        }}
        
        .nav a {{
            color: blue;
            text-decoration: underline wavy red;
            margin: 0 10px;
            font-weight: bold;
            font-size: 18px;
        }}
        
        .rainbow-text {{
            animation: rainbow 1s infinite;
            font-size: 18px;
            font-weight: bold;
        }}
        
        @keyframes rainbow {{
            0% {{ color: red; }}
            14% {{ color: orange; }}
            28% {{ color: yellow; }}
            42% {{ color: green; }}
            57% {{ color: blue; }}
            71% {{ color: indigo; }}
            85% {{ color: violet; }}
            100% {{ color: red; }}
        }}
        
        .blink {{
            animation: blinker 0.3s linear infinite;
        }}
        
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        
        @keyframes shake {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
            20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
            30% {{ transform: translate(3px, 2px) rotate(0deg); }}
            40% {{ transform: translate(1px, -1px) rotate(1deg); }}
            50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
            60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
            70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
            80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
            90% {{ transform: translate(1px, 2px) rotate(0deg); }}
            100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
        }}
        
        @keyframes borderColor {{
            0% {{ border-color: gold; }}
            33% {{ border-color: red; }}
            66% {{ border-color: blue; }}
            100% {{ border-color: gold; }}
        }}
        
        .tinder-container {{
            max-width: 500px;
            height: 600px;
            margin: 20px auto;
            position: relative;
            perspective: 1000px;
            border: 10px ridge gold;
            animation: borderColor 2s infinite;
            background-color: rgba(255, 255, 255, 0.7);
            overflow: hidden;
        }}
        
        .tinder-card {{
            position: absolute;
            width: 100%;
            height: 100%;
            background-color: white;
            border: 5px dotted blue;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
            padding: 20px;
            box-sizing: border-box;
            transform-origin: center;
            transition: transform 0.3s;
            animation: backgroundFlash 3s infinite;
            text-align: center;
        }}
        
        .tinder-card.active {{
            z-index: 3;
        }}
        
        .tinder-card.swiped-left {{
            transform: translateX(-200%) rotate(-30deg);
            opacity: 0;
        }}
        
        .tinder-card.swiped-right {{
            transform: translateX(200%) rotate(30deg);
            opacity: 0;
        }}
        
        .card-name {{
            font-size: 28px;
            font-weight: bold;
            color: blue;
            margin-bottom: 15px;
            animation: rainbow 1s infinite;
        }}
        
        .card-price {{
            font-size: 32px;
            font-weight: bold;
            color: red;
            text-shadow: 0 0 10px yellow;
            margin: 10px 0;
        }}
        
        .card-description {{
            font-size: 18px;
            margin: 10px 0;
            color: purple;
            font-family: 'Comic Sans MS', cursive;
        }}
        
        .card-secret {{
            font-size: 14px;
            color: green;
            margin-top: 10px;
            font-style: italic;
        }}
        
        .tinder-card img {{
            max-width: 250px;
            max-height: 300px;
            margin: 10px auto;
            display: block;
            border: 5px ridge gold;
        }}
        
        .epilepsy-image {{
            animation: epilepsy 0.1s infinite, borderColor 2s infinite, shake 0.2s infinite;
            filter: hue-rotate(0deg);
        }}
        
        @keyframes epilepsy {{
            0% {{ filter: hue-rotate(0deg) contrast(200%) brightness(150%); }}
            25% {{ filter: hue-rotate(90deg) contrast(300%) brightness(200%); }}
            50% {{ filter: hue-rotate(180deg) contrast(400%) brightness(250%); }}
            75% {{ filter: hue-rotate(270deg) contrast(300%) brightness(200%); }}
            100% {{ filter: hue-rotate(360deg) contrast(200%) brightness(150%); }}
        }}
        
        .tinder-buttons {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .like-button, .dislike-button {{
            font-size: 50px;
            background: none;
            border: none;
            cursor: pointer;
            margin: 0 20px;
            animation: shake 0.5s infinite;
            transition: transform 0.3s;
        }}
        
        .like-button:hover, .dislike-button:hover {{
            transform: scale(1.5);
        }}
        
        .liked-products, .disliked-products {{
            margin: 20px 0;
            padding: 10px;
            border: 5px dashed green;
            background-color: rgba(255, 255, 204, 0.8);
            animation: backgroundFlash 3s infinite;
        }}
        
        .liked-title, .disliked-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .liked-title {{
            color: green;
        }}
        
        .disliked-title {{
            color: red;
        }}
        
        .product-list {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }}
        
        .small-product {{
            margin: 10px;
            padding: 10px;
            border: 3px dotted blue;
            width: 150px;
            text-align: center;
            background-color: #FFFFCC;
            animation: backgroundFlash 3s infinite;
        }}
        
        .small-product img {{
            max-width: 100px;
            max-height: 100px;
            margin: 5px auto;
            display: block;
        }}
        
        .zakadrit-button {{
            position: fixed;
            bottom: 40%;
            right: 40%;
            width: 400px;
            height: 400px;
            background: linear-gradient(45deg, #ff00ff, #00ffff, #ffff00, #ff0000);
            background-size: 400% 400%;
            animation: gradientBG 3s ease infinite, shake 0.3s infinite;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-size: 32px;
            font-weight: bold;
            border: 10px solid;
            border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(255, 0, 255, 1);
            z-index: 9999;
            border-radius: 50%;
            text-align: center;
            color: white;
            text-shadow: 2px 2px 4px black;
            text-decoration: none;
        }}
        
        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="blink" style="font-size: 50px; color: red; text-shadow: 3px 3px 0 yellow;">ЗАКАДРИ СУЧКУ!!!</h1>
        <div style="font-size: 30px; font-weight: bold; color: blue; text-shadow: 0 0 5px yellow;" class="shake">
            СВАЙПАЙ ТОВАРЫ КАК В ТИНДЕРЕ!!! НАЙДИ СВОЮ ЛЮБОВЬ!!!
        </div>
    </div>
    
    <div class="nav">
        <a href="/{username_param}" class="rainbow-text">Главная</a> | 
        <a href="/products{username_param}" class="rainbow-text">Товары</a> | 
        <a href="/login-page" class="rainbow-text">Войти</a> | 
        <a href="/register-page" class="rainbow-text">Регистрация</a> |
        <a href="/protected-page{username_param}" class="rainbow-text">Личный кабинет</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red; font-size: 24px; text-shadow: 0 0 10px yellow;">АДМИНКА</a>
    </div>
    
    <marquee scrollamount="20" behavior="alternate" style="background-color: red; color: yellow; font-size: 36px; font-weight: bold; padding: 15px; border: 5px dashed blue;">
        !!! СВАЙПАЙ ВПРАВО И ЗАКАДРИ ТОВАР !!! СВАЙПАЙ ВЛЕВО ЧТОБ ОТКАЗАТЬ !!!
    </marquee>
    
    <div class="tinder-container" id="tinder-container">
        <!-- Карточки товаров будут добавлены через JavaScript -->
    </div>
    
    <div class="tinder-buttons">
        <button class="dislike-button" onclick="dislikeProduct()">❌</button>
        <button class="like-button" onclick="likeProduct()">❤️</button>
    </div>
    
    <div class="liked-products">
        <div class="liked-title blink">ЗАКАДРЕННЫЕ ТОВАРЫ:</div>
        <div class="product-list" id="liked-products-list"></div>
    </div>
    
    <div class="disliked-products">
        <div class="disliked-title blink">ОТВЕРГНУТЫЕ ТОВАРЫ:</div>
        <div class="product-list" id="disliked-products-list"></div>
    </div>
    
    <script>
        // Список всех товаров
        const products = {products_json};
        
        // Перемешиваем товары
        function shuffleArray(array) {{
            for (let i = array.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }}
            return array;
        }}
        
        const shuffledProducts = shuffleArray([...products]);
        let currentProductIndex = 0;
        
        const likedProducts = [];
        const dislikedProducts = [];
        
        // Функция для создания карточки товара
        function createProductCard(product, isActive = false) {{
            const card = document.createElement('div');
            card.className = 'tinder-card';
            if (isActive) {{
                card.classList.add('active');
            }}
            card.dataset.productId = product.id;
            
            let productImg = '';
            if (product.image_url) {{
                productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
            }} else if (product.gif_base64) {{
                productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
            }}
            
            card.innerHTML = `
                <div class="card-name">${{product.name}}</div>
                ${{productImg}}
                <div class="card-price">${{product.price}} руб.</div>
                <div class="card-description">${{product.description}}</div>
                <div class="card-secret">Секрет: ${{product.secret_info}}</div>
            `;
            
            return card;
        }}
        
        // Инициализация карточек
        function initCards() {{
            const container = document.getElementById('tinder-container');
            container.innerHTML = '';
            
            // Добавляем текущую карточку
            if (currentProductIndex < shuffledProducts.length) {{
                const currentCard = createProductCard(shuffledProducts[currentProductIndex], true);
                container.appendChild(currentCard);
            }} else {{
                container.innerHTML = '<div class="tinder-card active" style="display:flex; justify-content:center; align-items:center;"><h2>ВСЕ ТОВАРЫ ЗАКОНЧИЛИСЬ!</h2></div>';
            }}
        }}
        
        // Обновляем списки товаров
        function updateProductLists() {{
            const likedList = document.getElementById('liked-products-list');
            const dislikedList = document.getElementById('disliked-products-list');
            
            likedList.innerHTML = '';
            dislikedList.innerHTML = '';
            
            likedProducts.forEach(product => {{
                let productImg = '';
                if (product.image_url) {{
                    productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
                }} else if (product.gif_base64) {{
                    productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
                }}
                
                const productElement = document.createElement('div');
                productElement.className = 'small-product';
                productElement.innerHTML = `
                    <div>${{product.name}}</div>
                    ${{productImg}}
                    <div>${{product.price}} руб.</div>
                    <a href="/product/${{product.id}}">Подробнее</a>
                `;
                likedList.appendChild(productElement);
            }});
            
            dislikedProducts.forEach(product => {{
                let productImg = '';
                if (product.image_url) {{
                    productImg = `<img src="${{product.image_url}}" alt="${{product.name}}" class="epilepsy-image">`;
                }} else if (product.gif_base64) {{
                    productImg = `<img src="data:image/gif;base64,${{product.gif_base64}}" alt="${{product.name}}" class="epilepsy-image">`;
                }}
                
                const productElement = document.createElement('div');
                productElement.className = 'small-product';
                productElement.innerHTML = `
                    <div>${{product.name}}</div>
                    ${{productImg}}
                    <div>${{product.price}} руб.</div>
                    <a href="/product/${{product.id}}">Подробнее</a>
                `;
                dislikedList.appendChild(productElement);
            }});
        }}
        
        // Функция для лайка товара
        function likeProduct() {{
            if (currentProductIndex >= shuffledProducts.length) return;
            
            const currentCard = document.querySelector('.tinder-card.active');
            currentCard.classList.add('swiped-right');
            
            // Добавляем товар в список понравившихся
            likedProducts.push(shuffledProducts[currentProductIndex]);
            
            // Переход к следующей карточке
            setTimeout(() => {{
                currentProductIndex++;
                initCards();
                updateProductLists();
            }}, 300);
        }}
        
        // Функция для дизлайка товара
        function dislikeProduct() {{
            if (currentProductIndex >= shuffledProducts.length) return;
            
            const currentCard = document.querySelector('.tinder-card.active');
            currentCard.classList.add('swiped-left');
            
            // Добавляем товар в список не понравившихся
            dislikedProducts.push(shuffledProducts[currentProductIndex]);
            
            // Переход к следующей карточке
            setTimeout(() => {{
                currentProductIndex++;
                initCards();
                updateProductLists();
            }}, 300);
        }}
        
        // Инициализация при загрузке страницы
        window.onload = function() {{
            initCards();
            updateProductLists();
        }};
    </script>
    
    <footer style="background-color: #CCFFCC; padding: 20px; text-align: center; border: 4px solid green; animation: backgroundFlash 3s infinite; margin-top: 30px;">
        <div class="rainbow-text" style="font-size: 24px;">© 2023 МЕГА Магазин - Все права защищены</div>
        <div class="rainbow-text">Тел: 8-800-ПАРОЛЬ-АДМИНА УДАЛИТЬ НЕ ЗАБЫТЬ | Email: admin@example.com</div>
        <div class="blink" style="color:red; font-weight:bold; margin-top:10px; font-size: 28px; transform: rotate(-3deg);">ОПЛАТИТЬ АЛИМЕНТЫыы не забыть</div>
    </footer>
</body>
</html>'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)