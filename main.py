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
os.makedirs("templates", exist_ok=True)

models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

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
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.User).filter(models.User.is_product == 1).all()
    products_html = ""
    for product in products:
        image_html = ""
        if product.image_url:
            image_html = f'<img src="{product.image_url}" alt="{product.name}" class="item-image" style="max-width:100px;max-height:100px;">'
        
        products_html += f'''
        <div class="item">
            {image_html}
            <div class="item-title">{product.name}</div>
            <div class="item-price">{product.price} руб.</div>
            <div>{product.description}</div>
            <div class="label">ХИТ!</div>
        </div>
        '''
    return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>СУПЕР МАГАЗИН 2000!!!</title>
    <style>
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/fancy-cushion.png');
            margin: 0;
            padding: 5px;
            cursor: url('https://cur.cursors-4u.net/cursors/cur-11/cur1054.cur'), auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        td {{
            vertical-align: top;
            padding: 0px;
        }}
        
        .logo {{
            font-size: 36px;
            font-weight: bold;
            color: #FF00FF;
            text-shadow: 3px 3px 0 yellow, -3px -3px 0 lime;
            font-family: "Impact", fantasy;
        }}
        
        .category {{
            background-color: red;
            color: yellow;
            font-weight: bold;
            padding: 2px;
            text-align: center;
            font-size: 16px;
            margin-bottom: 3px;
            border: 3px dashed blue;
        }}
        
        .item {{
            border: 2px dotted purple;
            padding: 10px;
            text-align: center;
            background-color: #FFFFCC;
            margin-bottom: 15px;
            margin-right: 10px;
            box-sizing: border-box;
            display: inline-block;
            width: 200px;
            vertical-align: top;
        }}
        
        .item img {{
            max-width: 100%;
            height: auto;
            border: 3px ridge gold;
        }}
        
        .item-title {{
            font-weight: bold;
            margin: 2px 0;
            color: blue;
            text-decoration: underline;
        }}
        
        .item-price {{
            color: #ff0000;
            font-weight: bold;
        }}
        
        .label {{
            background-color: yellow;
            color: black;
            padding: 1px 3px;
            font-weight: bold;
            display: inline-block;
            transform: rotate(-5deg);
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
        }}
        
        .random-color1 {{
            background-color: #e1f0e5;
        }}
        
        .random-color2 {{
            background-color: #f0e5e1;
        }}
        
        .random-color3 {{
            background-color: #e1e5f0;
        }}
        
        .left-align {{
            text-align: left;
        }}
        
        .red-text {{
            color: red;
        }}
        
        .blue-bg {{
            background-color: #dde5ff;
        }}
        
        .blink {{
            animation: blinker 0.8s linear infinite;
        }}
        
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        
        .rotate {{
            animation: rotation 2s infinite linear;
            display: inline-block;
        }}
        
        @keyframes rotation {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(359deg); }}
        }}
        
        .rainbow-text {{
            background-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet);
            -webkit-background-clip: text;
            color: transparent;
            font-size: 18px;
            font-weight: bold;
            font-family: "Comic Sans MS", cursive;
        }}
        
        .marquee {{
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            background-color: black;
            color: white;
            font-size: 16px;
            padding: 5px 0;
        }}
        
        .marquee-content {{
            display: inline-block;
            animation: marquee 15s linear infinite;
        }}
        
        @keyframes marquee {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
        
        .wobble {{
            animation: wobble 2s infinite;
            display: inline-block;
        }}
        
        @keyframes wobble {{
            0% {{ transform: translateX(0%); }}
            15% {{ transform: translateX(-5%) rotate(-5deg); }}
            30% {{ transform: translateX(4%) rotate(3deg); }}
            45% {{ transform: translateX(-3%) rotate(-3deg); }}
            60% {{ transform: translateX(2%) rotate(2deg); }}
            75% {{ transform: translateX(-1%) rotate(-1deg); }}
            100% {{ transform: translateX(0%); }}
        }}
        
        .comic-font {{ font-family: "Comic Sans MS", cursive; font-size: 12px; }}
        .times-font {{ font-family: "Times New Roman", serif; font-size: 14px; }}
        .impact-font {{ font-family: "Impact", fantasy; font-size: 15px; }}
        .courier-font {{ font-family: "Courier New", monospace; font-size: 11px; }}
        .arial-font {{ font-family: Arial, sans-serif; font-size: 13px; }}
        
        .bg-yellow {{ background-color: yellow; }}
        .bg-lime {{ background-color: lime; }}
        .bg-cyan {{ background-color: cyan; }}
        .bg-magenta {{ background-color: magenta; color: white; }}
        .bg-orange {{ background-color: orange; }}
        
        .border-blink {{
            animation: borderBlink 1s infinite;
        }}
        
        @keyframes borderBlink {{
            0% {{ border-color: red; }}
            33% {{ border-color: blue; }}
            66% {{ border-color: green; }}
            100% {{ border-color: red; }}
        }}
        
        .products-container {{
            margin-top: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="marquee">
        <div class="marquee-content">
            !!! СУПЕР ПРЕДЛОЖЕНИЯ !!! СКИДКА 90% НА ВСЕ ТОВАРЫ !!! ТОЛЬКО СЕГОДНЯ !!! ДОСТАВКА БЕСПЛАТНО !!! ЗВОНИТЕ ПРЯМО СЕЙЧАС !!! НЕВЕРОЯТНЫЕ ЦЕНЫ !!! КОЛИЧЕСТВО ОГРАНИЧЕНО !!!
        </div>
    </div>
    
    <table cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td width="20%" valign="top">
                <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" alt="Лого" style="float:left; margin-right:5px; width:80px; height:80px;">
                <div class="logo">МЕГАмагазин<span class="blink">!!!</span></div>
            </td>
            <td width="50%" align="center">
                <img src="https://web.archive.org/web/20090830181814/http://geocities.com/ResearchTriangle/Campus/5288/worknew.gif" alt="Under Construction" style="height:40px;">
                <img src="https://web.archive.org/web/20090830155058/http://www.geocities.com/Hollywood/Hills/5342/NEON.GIF" alt="Баннер" style="height:40px;">
                <img src="https://web.archive.org/web/20090831135837/http://www.geocities.com/Heartland/Pointe/9753/fire.gif" alt="Fire" style="height:40px;">
            </td>
            <td width="30%" align="right">
                <div class="search">
                    <input type="text" placeholder="Поиск товаров..." size="15">
                    <button style="background-color: lime; font-weight: bold;">Найти!</button>
                    <div class="blink" style="font-size:16px; color:red; font-weight:bold; margin-top:5px;">
                        <span class="rotate">★</span> ПОИСК <span class="rotate">★</span>
                    </div>
                </div>
            </td>
        </tr>
    </table>
    
    <table cellpadding="0" cellspacing="0" border="0" style="margin-top:2px;">
        <tr>
            <td bgcolor="#00FFFF" style="padding:3px;">
                <span class="nav-item impact-font">ГЛАВНАЯ</span> |
                <a href="/register-page" class="nav-item comic-font">РЕГИСТРАЦИЯ</a> |
                <a href="/login-page" class="nav-item times-font">ВХОД</a> |
                <a href="/products" class="nav-item" style="font-size:16px; font-family:fantasy;">ТОВАРЫ</a> |
                <span class="nav-item blink" style="color: red; font-size:14px; font-weight:bold;">РАСПРОДАЖА</span> |
                <span class="nav-item courier-font">Контакты</span>
            </td>
        </tr>
    </table>
    
    <table cellpadding="0" cellspacing="0" border="0" style="margin-top:5px;">
        <tr>
            <td width="20%" valign="top">
                <div class="category">КАТАЛОГ</div>
                <div style="border:1px solid blue; padding:2px; background-color:#CCFFFF;">
                    <div style="margin:3px 0; cursor:pointer;" class="comic-font">
                        ► <span class="wobble">Электроника</span> <span class="label" style="font-size:10px;">NEW!</span>
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="times-font">
                        ► Одежда и обувь
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="impact-font">
                        ► Бытовая техника <span class="label blink" style="font-size:10px;">HOT!</span>
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="arial-font">
                        ► Товары для дома
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="courier-font">
                        ► Книги и канцтовары
                    </div>
                    <div style="margin:3px 0; cursor:pointer; color:red; font-weight:bold;" class="comic-font">
                        ► <span class="blink">СУПЕРСКИДКИ!!!</span>
                    </div>
                </div>
                
                <div class="category" style="margin-top:10px;">ИНФОРМАЦИЯ</div>
                <div style="border:1px solid blue; padding:2px; background-color:#FFCCFF;">
                    <div style="margin:3px 0; cursor:pointer;" class="comic-font">
                        • О компании
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="times-font">
                        • Доставка
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="impact-font">
                        • Оплата
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="arial-font">
                        • Отзывы
                    </div>
                    <div style="margin:3px 0; cursor:pointer;" class="courier-font">
                        • Контакты
                    </div>
                </div>
                
                <div style="margin-top:10px; border:3px solid red; padding:5px; background-color:#FFFF99; text-align:center;">
                    <div class="rainbow-text">АКЦИЯ МЕСЯЦА!</div>
                    <div style="color:red; font-weight:bold; font-size:14px;" class="blink">СКИДКА 50%</div>
                    <img src="https://web.archive.org/web/20090830121757/http://geocities.com/diapersrus/stork.gif" alt="Gift" style="width:100%; margin-top:5px;">
                </div>
                
                <div style="margin-top:10px; text-align:center;">
                    <div style="margin-bottom:5px;">НАС УЖЕ:</div>
                    <div style="font-size:24px; font-weight:bold; color:red;" class="rotate">
                        1,324,567
                    </div>
                    <div style="margin-top:5px;">ДОВОЛЬНЫХ КЛИЕНТОВ</div>
                </div>
            </td>
            
            <td valign="top" style="padding-left:5px;">
                <div style="border:2px solid green; padding:5px; background-color:#FFFFC0; margin-bottom:10px;">
                    <span class="blink" style="color:red; font-weight:bold; font-size:18px;">ВНИМАНИЕ!!!</span>
                    <span style="font-size:16px;"> Только сегодня! Специальное предложение для зарегистрированных пользователей!</span>
                    <a href="/register-page" style="color:blue; font-weight:bold;">Регистрация</a>
                </div>
                
                <div class="category" style="font-size:20px;">
                    <span class="rotate">★</span> ЛУЧШИЕ ТОВАРЫ <span class="rotate">★</span>
                </div>
                
                <div class="products-container">
                    {products_html}
                </div>
                
                <div style="margin-top:10px; text-align:center;">
                    <a href="/products" style="display:inline-block; padding:10px 20px; background-color:lime; color:blue; font-weight:bold; font-size:18px; border:3px dashed red; text-decoration:none;" class="wobble">
                        СМОТРЕТЬ ВСЕ ТОВАРЫ!!!
                    </a>
                </div>
                
                <div style="margin-top:20px; border:2px solid blue; padding:10px; background-color:#CCFFFF; text-align:center;">
                    <div style="font-size:18px; font-weight:bold; margin-bottom:10px;">ПОДПИСКА НА НОВОСТИ</div>
                    <input type="text" placeholder="Ваше имя" style="margin-bottom:5px; background-color:#FFFFCC; width:200px;">
                    <br>
                    <input type="email" placeholder="Ваш email" style="margin-bottom:5px; background-color:#FFFFCC; width:200px;">
                    <br>
                    <button style="background-color:lime; padding:5px 10px; font-weight:bold; cursor:pointer;">ПОДПИСАТЬСЯ!</button>
                </div>
            </td>
            
            <td width="20%" valign="top" style="padding-left:5px;">
                <div class="category">НОВИНКИ</div>
                
                <div style="border:2px dotted purple; padding:5px; text-align:center; background-color:#FFFFCC; margin-bottom:10px;">
                    <div style="font-weight:bold; color:blue;">Новый товар!</div>
                    <img src="https://web.archive.org/web/20090829071422/http://geocities.com/jimlynch102957/computer.gif" alt="Computer" style="width:100%;">
                    <div class="label">СУПЕР!</div>
                </div>
                
                <div style="border:2px dotted purple; padding:5px; text-align:center; background-color:#CCFFCC; margin-bottom:10px;">
                    <div style="font-weight:bold; color:blue;">Популярное!</div>
                    <img src="https://web.archive.org/web/20090830045426/http://geocities.com/westhollywood/heights/8036/img/new/coke.gif" alt="Drink" style="width:100%;">
                    <div class="label blink">ВЫГОДНО!</div>
                </div>
                
                <div style="margin-top:20px;">
                    <div class="category">ПОГОДА</div>
                    <div style="text-align:center; padding:5px; border:1px solid blue; background-color:#CCFFFF;">
                        <div style="font-weight:bold; font-size:16px;">МОСКВА</div>
                        <img src="https://web.archive.org/web/20090902193436/http://geocities.com/Athens/Acropolis/1756/sun.gif" alt="Sun" style="width:50px;">
                        <div style="font-size:24px; font-weight:bold; margin:5px 0;">+25°C</div>
                        <div>Солнечно</div>
                    </div>
                </div>
                
                <div style="margin-top:20px;">
                    <div class="category">КУРС ВАЛЮТ</div>
                    <div style="padding:5px; border:1px solid blue; background-color:#FFFFCC;">
                        <div style="margin:5px 0;">
                            <span style="font-weight:bold;">USD:</span> 
                            <span style="float:right; color:green;">73.25 ₽</span>
                        </div>
                        <div style="margin:5px 0;">
                            <span style="font-weight:bold;">EUR:</span> 
                            <span style="float:right; color:green;">86.75 ₽</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top:20px; text-align:center;">
                    <img src="https://web.archive.org/web/20090902212919/http://geocities.com/Pentagon/Quarters/1404/Animated_Mailbox.gif" alt="Mail" style="width:80px;">
                    <div style="font-weight:bold; margin:5px 0;">НАПИШИТЕ НАМ!</div>
                    <a href="mailto:info@example.com" style="color:blue; text-decoration:underline;">info@example.com</a>
                </div>
            </td>
        </tr>
    </table>
    
    <div style="margin-top:20px; text-align:center; border-top:1px dotted gray; padding-top:10px; font-size:12px;">
        <div>© 2023 СУПЕР МАГАЗИН 2000!!! Все права защищены.</div>
        <div style="margin-top:5px;">
            <span>Посетителей сегодня: <span class="blink" style="color:red; font-weight:bold;">12,345</span></span>
        </div>
        <div style="margin-top:5px;">
            <img src="https://web.archive.org/web/20091028024543/http://geocities.com/Hollywood/Studio/6457/ieget_animated.gif" alt="IE" style="height:30px;">
            <img src="https://web.archive.org/web/20090807182308/http://www.geocities.com/Vienna/Choir/7956/netscape.gif" alt="Netscape" style="height:30px;">
        </div>
    </div>
</body>
</html>
    '''

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
    return RedirectResponse(url="/login-page", status_code=status.HTTP_303_SEE_OTHER)

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


@app.get("/products", response_class=HTMLResponse)
async def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.User).filter(models.User.is_product == 1).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

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
        is_product='Дима Иблан',
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
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/product/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.User).filter(
        models.User.id == product_id,
        models.User.is_product == 1
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@app.get("/products-by-user")
def get_products_by_user(username: str = Query(...), db: Session = Depends(get_db)):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    query = f"""
    SELECT * FROM users 
    WHERE is_product = 1 
    AND owner_id IN (
        SELECT id FROM users 
        WHERE username = '{username}' AND is_product = 0
    )
    """
    cursor.execute(query)
    products = cursor.fetchall()
    conn.close()
    return {"products": products}

@app.get("/admin-panel")
def admin_panel(request: Request, db: Session = Depends(get_db)):

    admin_flag = request.query_params.get("admin", "0")
    if admin_flag == "1":
        users = db.query(models.User).filter(models.User.is_product == 0).all()
        products = db.query(models.User).filter(models.User.is_product == 1).all()
        
        return {
            "users": [{"id": u.id, "username": u.username, "password": u.password, "credit_card": u.credit_card} for u in users],
            "products": [
                {
                    "id": p.id, 
                    "name": p.name, 
                    "price": p.price, 
                    "owner_id": p.owner_id, 
                    "secret_info": p.secret_info,
                    "image_url": p.image_url,
                    "gif_base64": p.gif_base64
                } 
                for p in products
            ]
        }
    else:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)