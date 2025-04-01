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
async def home(request: Request, db: Session = Depends(get_db), username: Optional[str] = None):
    # Получаем все товары
    products = db.query(models.User).filter(models.User.is_product == 1).all()
    
    # Генерируем HTML для товаров
    products_html = ""
    for product in products:
        product_image = ""
        if product.image_url:
            product_image = f'<img src="{product.image_url}" alt="{product.name}" style="max-width:100%; height:auto;">'
        elif product.gif_base64:
            product_image = f'<img src="data:image/gif;base64,{product.gif_base64}" alt="{product.name}" style="max-width:100%; height:auto;">'
            
        products_html += f'''
        <div class="item">
            <div class="item-title">{product.name}</div>
            {product_image}
            <div class="item-price">{product.price} руб.</div>
            <div class="left-align">{product.description}</div>
            <button style="background-color:lime; font-weight:bold; margin-top:5px;">КУПИТЬ!</button>
        </div>
        '''
    
    # Блок авторизации в зависимости от наличия пользователя
    auth_block = '''
    <div>
        <a href="/register-page">Регистрация</a> | 
        <a href="/login-page">Войти</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red;">АДМИНКА</a>
    </div>
    '''
    
    # Получаем параметр username из URL (плохая практика - не проверяем авторизацию)
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
        user = db.query(models.User).filter(
            models.User.username == url_username,
            models.User.is_product == 0
        ).first()
        if user:
            # Если пользователь найден, меняем блок авторизации
            auth_block = f'''
            <div style="background-color: #CCFFCC; padding: 5px; border: 2px dotted blue;">
                <div class="blink" style="color:green; font-weight:bold;">ВЫ ВОШЛИ КАК: {user.username}</div>
                <a href="/protected-page?username={user.username}">Личный кабинет</a> |
                <a href="/logout">Выйти</a> |
                <a href="/admin-panel?admin=1" class="blink" style="color:red;">АДМИНКА</a>
            </div>
            '''
    
    # Возвращаем весь HTML-код напрямую из Python
    return f'''<!DOCTYPE html>
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
            padding: 2px;
            text-align: center;
            background-color: #FFFFCC;
            margin-bottom: 3px;
            margin-right: 3px;
            box-sizing: border-box;
            width: 23%;
            display: inline-block;
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
        
        .left-align {{
            text-align: left;
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
                    <img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" alt="Лого" style="float:left; margin-right:5px; width:80px; height:80px;">
                    <div class="logo">МЕГАмагазин<span class="blink">!!!</span></div>
                </a>
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
                {auth_block}
            </td>
        </tr>
    </table>
    
    <table cellpadding="0" cellspacing="0" border="0" style="margin-top:2px;">
        <tr>
            <td bgcolor="#00FFFF" style="padding:3px;">
                <a href="/{username_param}" class="nav-item" style="font-size:16px; font-weight:bold;">ГЛАВНАЯ</a> |
                <a href="/products{username_param}" class="nav-item">ТОВАРЫ</a> |
                <span class="nav-item blink" style="color: red; font-weight:bold;">РАСПРОДАЖА</span> |
                <span class="nav-item">О НАС</span> |
                <span class="nav-item">КОНТАКТЫ</span>
            </td>
        </tr>
    </table>
    
    <div style="margin-top:10px;">
        <div class="category">НАШИ СУПЕР ТОВАРЫ!!!</div>
        <div style="display:flex; flex-wrap:wrap; justify-content:space-between;">
            {products_html}
        </div>
    </div>
    
    <div style="margin-top:10px; background-color:#CCFFCC; padding:5px; text-align:center; border:2px solid green;">
        <div>© 2023 МЕГА Магазин - Все права защищены</div>
        <div>Тел: 8-800-ПАРОЛЬ-АДМИНА | Email: admin@example.com</div>
        <div class="blink" style="color:red; font-weight:bold; margin-top:5px;">САЙТ СОЗДАН ЛУЧШИМИ ПРОГРАММИСТАМИ!</div>
    </div>
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
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/fancy-cushion.png');
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
    
    # После регистрации сразу перенаправляем на главную с именем пользователя
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
        models.User.is_product == 0  # Это пользователь, а не товар
    ).first()
    
    if not user:
        # Возвращаем страницу логина с ошибкой
        error = "Пользователь не существует"
        return RedirectResponse(url=f"/login-page?error={error}", status_code=status.HTTP_303_SEE_OTHER)
    
    if user.password != password:
        # Возвращаем страницу логина с ошибкой
        error = "Неверный пароль"
        return RedirectResponse(url=f"/login-page?error={error}", status_code=status.HTTP_303_SEE_OTHER)
    
    # Перенаправляем на главную страницу с указанием имени пользователя в URL
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
    # Получаем параметр username из URL
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
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/fancy-cushion.png');
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
    # Просто перенаправляем на главную без параметров, чтобы "выйти"
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/products", response_class=HTMLResponse)
async def list_products(request: Request, db: Session = Depends(get_db)):
    # Получаем все товары
    products = db.query(models.User).filter(models.User.is_product == 1).all()
    
    # Генерируем HTML для товаров
    products_html = ""
    for product in products:
        product_image = ""
        if product.image_url:
            product_image = f'<img src="{product.image_url}" alt="{product.name}" class="product-image">'
        elif product.gif_base64:
            product_image = f'<img src="data:image/gif;base64,{product.gif_base64}" alt="{product.name}" class="product-image">'
            
        products_html += f'''
        <div class="product">
            <h2>{product.name}</h2>
            {product_image}
            <p>Цена: <span class="price">{product.price} руб.</span></p>
            <p>{product.description}</p>
            <p>ID продавца: {product.owner_id}</p>
            <input type="hidden" id="secret_{product.id}" value="{product.secret_info}">
            <button onclick="buyProduct({product.id})" class="buy-button">КУПИТЬ!</button>
        </div>
        '''
    
    # Форма добавления товара
    add_product_form = '''
    <h2 class="blink" style="color:#FF00FF;">Добавить новый товар</h2>
    <form action="/add-product" method="post" class="add-form">
        <div class="form-group">
            <label for="name">Название:</label>
            <input type="text" id="name" name="name" required>
        </div>
        <div class="form-group">
            <label for="price">Цена:</label>
            <input type="number" id="price" name="price" step="0.01" required>
        </div>
        <div class="form-group">
            <label for="description">Описание:</label>
            <textarea id="description" name="description" required></textarea>
        </div>
        <div class="form-group">
            <label for="owner_id">ID владельца:</label>
            <input type="number" id="owner_id" name="owner_id" required>
        </div>
        <div class="form-group">
            <label for="secret_info">Секретная информация:</label>
            <input type="text" id="secret_info" name="secret_info">
        </div>
        <div class="form-group">
            <label for="image_url">URL картинки:</label>
            <input type="text" id="image_url" name="image_url" placeholder="https://example.com/image.jpg">
        </div>
        <div class="form-group">
            <label for="gif_base64">GIF в формате base64:</label>
            <textarea id="gif_base64" name="gif_base64" placeholder="Вставьте base64-строку GIF файла"></textarea>
            <small style="color:red;">Почему бы не хранить бинарные данные в текстовом поле? 🙃</small>
        </div>
        <button type="submit" class="blink">Добавить товар</button>
    </form>
    '''
    
    # Форма поиска товаров
    search_form = '''
    <h2 class="blink" style="color:#FF00FF;">Поиск товаров по пользователю</h2>
    <form action="/products-by-user" method="get" class="search-form">
        <div class="form-group">
            <label for="username">Имя пользователя:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <button type="submit">Найти товары</button>
        <button type="button" onclick="executeQuery()">Найти через JavaScript</button>
    </form>
    '''
    
    # Получаем параметр username из URL (для сохранения авторизации)
    url_username = request.query_params.get('username')
    username_param = ""
    if url_username:
        username_param = f"?username={url_username}"
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Наши товары</title>
    <style>
        body {{
            font-family: Comic Sans MS, cursive;
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/fancy-cushion.png');
            margin: 0;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
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
        .product {{
            border: 2px dotted purple;
            padding: 10px;
            margin-bottom: 20px;
            background-color: #FFFFCC;
        }}
        .product-image {{
            max-width: 300px;
            max-height: 200px;
            margin: 10px 0;
            border: 3px ridge gold;
        }}
        .price {{
            color: red;
            font-weight: bold;
            font-size: 18px;
        }}
        .buy-button {{
            background-color: lime;
            border: 3px ridge gold;
            padding: 5px 10px;
            font-weight: bold;
            cursor: pointer;
        }}
        .add-form, .search-form {{
            background-color: #CCFFFF;
            padding: 15px;
            margin-bottom: 20px;
            border: 3px dashed purple;
        }}
        .form-group {{
            margin-bottom: 10px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: blue;
        }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 5px;
            background-color: #CCFFCC;
            border: 2px solid green;
        }}
        button {{
            background-color: lime;
            border: 2px solid blue;
            padding: 5px 10px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 5px;
        }}
        .blink {{
            animation: blinker 0.8s linear infinite;
        }}
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        h1, h2 {{
            color: #FF00FF;
            text-shadow: 1px 1px 0 yellow;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="blink">НАШИ СУПЕР ТОВАРЫ!!!</h1>
    </div>
    
    <div class="nav">
        <a href="/{username_param}">Главная</a> | 
        <a href="/login-page">Войти</a> | 
        <a href="/register-page">Регистрация</a> |
        <a href="/protected-page{username_param}">Личный кабинет</a> |
        <a href="/admin-panel?admin=1" class="blink" style="color:red;">АДМИНКА</a>
    </div>

    <div class="products-container">
        {products_html}
    </div>

    {add_product_form}
    
    {search_form}

    <script>
        function buyProduct(id) {{
            alert('Товар куплен! Но на самом деле нет. ID: ' + id);
            // Небезопасно - показываем секретные данные
            const secretData = document.getElementById('secret_' + id).value;
            if (secretData) {{
                alert('Секретные данные товара: ' + secretData);
            }}
        }}
        
        function executeQuery() {{
            let username = document.getElementById('username').value;
            // Потенциально опасное построение SQL-запроса в коде
            let query = `
            SELECT * FROM users 
            WHERE is_product = 1 
            AND owner_id IN (
                SELECT id FROM users 
                WHERE username = '${{username}}' AND is_product = 0
            )`;
            console.log("Выполняем запрос: " + query);
            // Отправляем запрос на сервер
            fetch('/products-by-user?username=' + username)
                .then(response => response.json())
                .then(data => {{
                    console.log(data);
                    alert('Найдено товаров: ' + (data.products ? data.products.length : 0));
                }});
        }}
    </script>
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