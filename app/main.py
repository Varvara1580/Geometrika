# Импортируем FastAPI — главный класс, который создаёт веб-приложение (сайт/API)
from fastapi import FastAPI, Request, Form, Depends, File, UploadFile

# HTMLResponse — говорим FastAPI, что ответ будет HTML (страница)
# RedirectResponse — ответ-перенаправление (после POST обычно редиректят на GET)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

# Jinja2Templates — подключаем шаблоны (HTML-файлы с подстановками {{ ... }})
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, mapped_column
from app.Models import User, User_progress, Refresh_token, Geometry_class, Own_topic, Own_task, User_progress_own
from app.database import engine, Base, get_db

import os #для сохранения своих картинок, создает path
import shutil #для сохранения своих картинок
import uuid #для генерации уникальных id в сохранении своих картинок
from fastapi.staticfiles import StaticFiles
from app.fill import *

import matplotlib
matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import io
from matplotlib.figure import Figure



from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# Указываем папку, где лежат HTML-шаблоны
templates = Jinja2Templates(directory= BASE_DIR / "templates")
app = FastAPI()



Base.metadata.create_all(bind = engine)

SECRET_KEY = '12345'

ALGORITHM = 'HS256'

ACCESS_TOKEN = 60

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')

UPLOAD_DIR = BASE_DIR / 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok = True)


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hash_password: str):
    return pwd_context.verify(password, hash_password)


def create_access_token(user: User):
    global ALGORITHM
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN)
    data = {'sub': user.username, 'user_id': user.id, 'role': user.role, 'type': 'access', 'exp': expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user: User):
    global ALGORITHM
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN)
    data = {'sub': user.username, 'user_id': user.id, 'role': user.role, 'type': 'refresh', 'exp': expire}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def decode_token(token: str) -> dict:
    global ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
        '''
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
        '''


def create_user(name: str, surname: str, username: str, password: str, role: str, db: Session):
    new_user = db.scalars(select(User).where((User.name == name) | (User.surname == surname) |(User.username == username) | (User.password == password))).first()
    if new_user is not None:
        return None
    user = User(name = name, surname = surname, username = username, password = hash_password(password), role = role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(username: str, password: str, db: Session):
    user = db.scalars(select(User).where(User.username == username)).first()
    if user is None:
        return None
    if not verify_password(password, user.password):
        return 'Неверный пароль'
    return user



def get_user(request: Request, db: Session):
    token = request.cookies.get('access_token')
    #print(token)
    if not token:
        return None
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != 'access':
        return None
    user_id = payload.get('user_id')
    if user_id is None:
        return None
    user = db.get(User, user_id)
    return user
@app.get('/')
def index(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    print(user)
    if user is None:
        return templates.TemplateResponse(request = request, name = 'login.html')
    init_db(db)
    topics = db.scalars(select(Topic)).all()
    tasks = db.scalars(select(Task)).all()
    kolvo = [12, 24, 18, 9, 12, 18, 10, 15, 24, 21, 27, 54, 36, 28, 26, 17, 15, 16, 22, 23, 54, 17, 86, 37, 26]
    difficulty = ['*', '*', '*', '*', '*', '**', '**', '**', '**', '**', '***', '***', '***', '***', '***', '****',
                  '****', '****', '****', '*****', '*****', '*****', '*****', '*****', '*****']
    sch_topic = 0
    user_result = 0
    class_names = ''
    if user.role == 'user':
        for i in user.classes:
            class_names += i.name + ', '
    else:
        for i in user.created:
            class_names += i.name + ', '
    print(class_names)
    class_names = class_names[:-2]
    if user.role == 'user':
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
    else:
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
    return templates.TemplateResponse(request = request, name = 'index.html',
                                      context = {'user': user, 'topics': topics, 'tasks': tasks,
                                                 'kolvo': kolvo, 'difficulty': difficulty, 'class_names': class_names,
                                                 'all_classes': all_classes})

@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse(request = request, name = 'login.html')
@app.post('/login')
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = login_user(username, password, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Пользователя с таким username не существует'})
    if user == 'Неверный пароль':
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': user})
    access_token = create_access_token(user)
    refresh_token, date = create_refresh_token(user)
    token_db = Refresh_token(token=refresh_token, updated_at=date, user_id=user.id)
    db.add(token_db)
    db.commit()
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
    return response


@app.get('/register')
def register(request: Request):
    return templates.TemplateResponse(request = request, name = 'register.html')
@app.post('/register')
def register_post(request: Request, name: str = Form(...), surname: str = Form(...),
                  username: str = Form(...), password: str = Form(...), role: str = Form(...),
                  admin_password: str = Form(...), db: Session = Depends(get_db)):
    user = create_user(name = name, surname = surname, username = username, password = password, role = role, db = db)
    if admin_password != 'admin_password' and role == 'admin':
        return templates.TemplateResponse(request=request, name='register.html',
                                          context={'message': 'Неверный код доступа для администратора'})
    if user is None:
        return templates.TemplateResponse(request=request, name='register.html',
                                          context={'message': 'Пользователь с таким username или email уже существует'})
    return RedirectResponse('/login', status_code = 303)


@app.get('/logout')
def logout():
    response = RedirectResponse(url = '/login', status_code = 303)
    response.delete_cookie('access_token')
    return response


@app.get('/task/{topic_id}/{task_id}')
def task(request: Request, topic_id: int, task_id: int, db: Session = Depends(get_db), ):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request = request, name = 'login.html',
                                          context = {'message': 'Вы не вошли в систему'})
    task = db.scalars(select(Task).where((Task.number == task_id) & (Task.topic_id == topic_id))).first()
    kolvo = len(db.scalars(select(Task).where(Task.topic_id == topic_id)).all())
    #tasks = db.scalars(select(Task).where(Task.topic_id == topic_id))
    #all_tasks = [task.id for task in tasks]
    #progresses = db.scalars(select(User_progress).where((User_progress.user_id == user.id) &
    #                                                    (User_progress.task_id.in_(all_tasks)))).all()
    progress = db.scalars(select(User_progress).where((User_progress.user_id == user.id)
                                                      & (User_progress.task_id == task.id))).first()
    message = None
    if progress is not None and progress.saved == True:
        message = 'Ответ сохранен'
    return templates.TemplateResponse(request = request, name = 'task.html',
                                      context = {'task': task, 'kolvo': kolvo, 'task_id': task_id,
                                                 'username': user.username, 'schedule': user.schedule,
                                                 'message': message})
                                                 #'progresses': progresses})

@app.post('/task/{topic_id}/{task_id}')
def task_post(request: Request, topic_id: int, task_id: int, db: Session = Depends(get_db),
              user_answer: str = Form(None), button: str = Form(None)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    task = db.scalars(select(Task).where((Task.number == task_id) & (Task.topic_id == topic_id))).first()
    kolvo = len(db.scalars(select(Task).where(Task.topic_id == topic_id)).all())
    if button == 'next':
        if task_id == kolvo:
            tasks = db.scalars(select(Task).where(Task.topic_id == topic_id))
            all_tasks = [task.id for task in tasks]
            print(all_tasks)
            progress = len(db.scalars(select(User_progress).
                                  where((User_progress.user_id == user.id) &
                                        (User_progress.is_correct == True) &
                                        (User_progress.task_id.in_(all_tasks)))).all())
            progresses = db.scalars(select(User_progress).
                                      where((User_progress.user_id == user.id) &
                                            (User_progress.task_id.in_(all_tasks)))).all()
            print(len(progresses), progress)
            for i in progresses:
                print(i.is_correct, i.user_result)
                print()
                i.saved = False
                i.is_correct_1 = i.is_correct
                i.is_correct = False
            db.commit()
            return templates.TemplateResponse(request = request, name = 'result.html',
                                              context = {'kolvo': kolvo, 'username': user.username,
                                                         'progress': int(progress), 'schedule': user.schedule})
        return RedirectResponse(f'/task/{topic_id}/{task_id + 1}', status_code = 303)
    elif button == 'save':
        progress = db.scalars(select(User_progress).where((User_progress.user_id == user.id) &
                                                          (User_progress.task_id == task.id))).first()
        if progress is None:
            progress = User_progress(user_id=user.id, task_id=task.id,
                                     is_correct=(user_answer == task.otv),
                                     is_correct_1 = (user_answer == task.otv),
                                     user_result=int(user_answer == task.otv))
            db.add(progress)
            db.commit()
            db.refresh(progress)
        else:
            if not progress.is_correct and user_answer == task.otv:
                progress.is_correct = True
                progress.is_correct_1 = True
                progress.user_result = 1
            elif progress.is_correct and user_answer != task.otv:
                progress.is_correct = False
                progress.is_correct_1 = False
                progress.user_result = 0
            db.commit()
            db.refresh(progress)
        print(123)
        print(progress.is_correct, progress.user_result)
        progress.saved = True
        db.commit()
        db.refresh(progress)
        tasks = db.scalars(select(Task).where(Task.topic_id == topic_id))
        all_tasks = [task.id for task in tasks]
        progresses = db.scalars(select(User_progress).where((User_progress.user_id == user.id) &
                                                          (User_progress.task_id.in_(all_tasks)))).all()
        return templates.TemplateResponse(request=request, name='task.html',
                                          context={'task': task, 'kolvo': kolvo, 'task_id': task_id,
                                                   'username': user.username, 'user_answer': user_answer,
                                                   'button': button, 'schedule': user.schedule,
                                                   'message': 'Ответ сохранен'})#'progresses': progresses})
    elif button == 'pred':
        return RedirectResponse(f'/task/{topic_id}/{task_id - 1}', status_code=303)
    elif button == 'check':
        result = ''
        color = ''
        if not user_answer:
            result = 'Выберите ответ'
            color = '#ff7803'
        elif user_answer == task.otv:
            result = 'Верно'
            color = '#02fa30'
        else:
            result = 'Неверно'
            color = '#ff0703'
        progress = db.scalars(select(User_progress).where((User_progress.user_id == user.id) &
                                                          (User_progress.task_id == task.id))).first()
        if progress is None:
            progress = User_progress(user_id=user.id, task_id=task.id,
                                     is_correct=(user_answer == task.otv),
                                     is_correct_1=(user_answer == task.otv),
                                     user_result=int(user_answer == task.otv))
            db.add(progress)
            db.commit()
            db.refresh(progress)
        else:
            if not progress.is_correct and user_answer == task.otv:
                progress.is_correct = True
                progress.is_correct_1 = True
                progress.user_result = 1
            elif progress.is_correct and user_answer != task.otv:
                progress.is_correct = False
                progress.is_correct_1 = False
                progress.user_result = 0
            db.commit()
            db.refresh(progress)
        #tasks = db.scalars(select(Task).where(Task.topic_id == topic_id))
        #all_tasks = [task.id for task in tasks]
        #progresses = db.scalars(select(User_progress).where((User_progress.user_id == user.id) &
        #                                                    (User_progress.task_id.in_(all_tasks)))).all()
        print(progress)
        return templates.TemplateResponse(request=request, name='task.html',
            context={'result': result, 'task': task, 'color': color, 'kolvo': kolvo, 'task_id': task_id,
            'username': user.username, 'user_answer': user_answer, 'button': button,
                     'schedule': user.schedule})#'progresses': progresses})






def figure_to_response(figure):
    buffer = io.BytesIO()
    figure.savefig(buffer, format = 'png')
    buffer.seek(0)
    return StreamingResponse(buffer, media_type = 'image/png')

@app.get('/bar.png')
def bar(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    figure1 = Figure(figsize=(11.5, 2.5), dpi=100)
    plt1 = figure1.subplots()
    topics = db.scalars(select(Topic)).all()
    total = []
    correct = []
    for topic in topics:
        tasks = db.scalars(select(Task).where(Task.topic_id == topic.id)).all()
        task_id = [task.id for task in tasks]
        progress = len(db.scalars(select(User_progress).
                                  where((User_progress.user_id == user.id) &
                                        (User_progress.is_correct_1 == True) &
                                        (User_progress.task_id.in_(task_id)))).all())
        total.append(len(tasks))
        correct.append(progress)
    x = [i for i in range(1, 26)]
    plt1.bar(x, total, color='#eaff00')
    plt1.bar(x, correct, color='#02fa30')
    plt1.set_title('Решенные задачи по темам', color='#fcfcfc')
    plt1.set_xlabel('Номер темы', color='#fcfcfc')
    plt1.set_ylabel('Количество задач', color='#fcfcfc')
    plt1.tick_params(colors='#fcfcfc')  # цвет цифр на осях
    plt1.set_xticks(range(1, 26, 1))  # точность шкалы x
    for i in range(25):
        plt1.text(x[i] + 0.1, total[i] + 2, f'{correct[i]}', color='#eaff00')
    plt1.legend(['Неверно', 'Верно'], loc='center left', bbox_to_anchor=(1, 0.5))
    plt1.set_facecolor('#03420a')
    figure1.patch.set_facecolor('#03420a')
    #plt1.clf()
    return figure_to_response(figure1)


@app.get('/{stat_topics}/pie.png')
def pie(request: Request, stat_topics: str = 'all', db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    if stat_topics == 'all':
        correct_all = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == user.id) &
                                           (User_progress.is_correct_1 == True))).all())
        all = len(db.scalars(select(Task)).all())
    else:
        stat_topics = int(stat_topics)
        all = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
        all_tasks = [i.id for i in all]
        correct_all = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == user.id) &
                                           (User_progress.is_correct_1 == True) &
                                           (User_progress.task_id.in_(all_tasks)))).all())
        all = len(all)
    figure1 = Figure(figsize=(5, 5), dpi=100)
    plt1 = figure1.subplots()
    plt1.pie(
        [correct_all, all - correct_all],
        colors=['#02fa30', '#eaff00'],
        wedgeprops={'width': 0.3},
        autopct='%1.0f%%',
        pctdistance=0.5,
        textprops={'color': '#fcfcfc', 'weight': 'bold'}
    )
    plt1.legend(['Верно', 'Неверно'], loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4)
    plt1.set_title('Процент решенных задач', color='#fcfcfc')
    plt1.tick_params(colors='#fcfcfc')  # цвет цифр на осях
    plt1.set_facecolor('#03420a')
    figure1.patch.set_facecolor('#03420a')
    return figure_to_response(figure1)


@app.get('/user') #личный кабинет, статистика пользователя
def user(request: Request, stat_topics: str = 'all', db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    print(stat_topics)
    topics = db.scalars(select(Topic)).all()
    if user.role == 'user':
        #all, correct_all, topic_stats, own_topic_stats = graph(user = user, role = 'user', db = db)
        topic_stats = []
        correct_all = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == user.id) &
                                           (User_progress.is_correct_1 == True))).all())
        all = len(db.scalars(select(Task)).all())
        for topic in topics:
            tasks = db.scalars(select(Task).where(Task.topic_id == topic.id)).all()
            task_id = [task.id for task in tasks]
            progress = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == user.id) &
                                            (User_progress.is_correct_1 == True) &
                                            (User_progress.task_id.in_(task_id)))).all())
            if progress == len(tasks):
                status = 'Пройдено'
            elif progress > 0:
                status = 'Частично'
            else:
                status = 'Не начали'
            topic_stats.append({'name': topic.name, 'total': len(tasks), 'correct': progress, 'status': status})
        classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
        if user.role == 'admin':
            classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        else:
            classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
        own_topic_stats = {i: [] for i in classes}
        for i in classes:
            for j in i.own_topics:
                total = len(db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                       (User_progress_own.own_topic_id == j.id))).all())
                correct = len(db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                         (User_progress_own.own_topic_id == j.id) &
                                                                         (
                                                                                     User_progress_own.is_correct_1 == True))).all())
                kolvo = len(j.own_tasks)
                if correct == kolvo:
                    status = 'Пройдено'
                elif correct > 0:
                    status = 'Частично'
                else:
                    status = 'Не начали'
                own_topic_stats[i].append({'name': j.name, 'total': total, 'correct': correct, 'status': status})
        return templates.TemplateResponse(request = request, name = 'user.html',
                                          context = {'id': user.id, 'name': user.name, 'surname': user.surname,
                                                     'username': user.username, 'role': user.role,
                                                     'topic_stats': topic_stats, 'own_topic_stats': own_topic_stats,
                                                     'all': all, 'correct_all': correct_all,
                                                     'topics': topics, 'classes': classes, 'stat_topics': stat_topics})
    elif user.role == 'admin':
        classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        #own_topics = db.scalars(select(Own_topic).where(Own_topic.geometry_class.creator_id == user.id)).all()
        return templates.TemplateResponse(request=request, name='admin.html',
                                          context={'id': user.id, 'name': user.name, 'surname': user.surname,
                                                   'username': user.username, 'role': user.role, 'classes': classes,
                                                   'topics': topics})


@app.post('/stat/admin') #статистика админа (своя и по классам)
def admin_stat(request: Request, stat: str = Form('my'), stat_topics: str = Form('all'), db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    topics = db.scalars(select(Topic)).all()
    if stat == 'my':
        #all, correct_all, topic_stats, own_topic_stats = graph(user = user, role='admin', db=db, stat = stat)
        topic_stats = []
        correct_all = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == user.id) &
                                           (User_progress.is_correct_1 == True))).all())
        all = len(db.scalars(select(Task)).all())
        for topic in topics:
            tasks = db.scalars(select(Task).where(Task.topic_id == topic.id)).all()
            task_id = [task.id for task in tasks]
            progress = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == user.id) &
                                            (User_progress.is_correct_1 == True) &
                                            (User_progress.task_id.in_(task_id)))).all())
            if progress == len(tasks):
                status = 'Пройдено'
            elif progress > 0:
                status = 'Частично'
            else:
                status = 'Не начали'
            topic_stats.append({'name': topic.name, 'total': len(tasks), 'correct': progress, 'status': status})
        classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        own_topic_stats = {i: [] for i in classes}
        for i in classes:
            for j in i.own_topics:
                total = len(db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                       (User_progress_own.own_topic_id == j.id))).all())
                correct = len(db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                         (User_progress_own.own_topic_id == j.id) &
                                                                         (
                                                                                 User_progress_own.is_correct_1 == True))).all())
                kolvo = len(j.own_tasks)
                if correct == kolvo:
                    status = 'Пройдено'
                elif correct > 0:
                    status = 'Частично'
                else:
                    status = 'Не начали'
                own_topic_stats[i].append({'name': j.name, 'total': total, 'correct': correct, 'status': status})
        classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        return templates.TemplateResponse(request=request, name='admin.html',
                                          context={'id': user.id, 'name': user.name, 'surname': user.surname,
                                                   'username': user.username, 'role': user.role,
                                                   'topic_stats': topic_stats, 'own_topic_stats': own_topic_stats,
                                                   'all': all, 'correct_all': correct_all,
                                                   'stat': stat, 'classes': classes, 'topics': topics,
                                                   'stat_topics': stat_topics})

    else:
        stat = int(stat)

        geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == stat)).first()
        classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        topics = db.scalars(select(Topic)).all()
        members = []
        if stat_topics != 'all':
            tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
            task_id = [task.id for task in tasks]

        for i in geometry_class.members:
            if stat_topics == 'all':
                correct = len(db.scalars(select(User_progress).where((User_progress.user_id == i.id) &
                                                                     (User_progress.is_correct_1 == True))).all())
            else:
                stat_topics = int(stat_topics)
                correct = len(db.scalars(select(User_progress).
                                         where((User_progress.user_id == i.id) &
                                               (User_progress.is_correct_1 == True) &
                                               (User_progress.task_id.in_(task_id)))).all())
            members.append([i.id, i.name, i.surname, i.username, correct])
        members.sort(key=lambda x: x[4], reverse=True)
        #geometry_class, classes, topics, members = graph(user = user, role = user.role, db = db, stat = str(stat))
        return templates.TemplateResponse(request=request, name='admin.html',
                                          context={'id': user.id, 'name': user.name, 'surname': user.surname,
                                                   'username': user.username, 'role': user.role,
                                                   'stat': stat, 'classes': classes, 'topics': topics,
                                                   'members': members, 'stat_topics': stat_topics,
                                                   'class_name': geometry_class.name})


@app.get('/{stat}/{stat_topics}/bar_for_classes.png')
def bar_for_classes(request: Request, stat: int, stat_topics: str = 'all', db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == stat)).first()
    members = []
    if stat_topics != 'all':
        tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
        task_id = [task.id for task in tasks]

    for i in geometry_class.members:
        if stat_topics == 'all':
            correct = len(db.scalars(select(User_progress).where((User_progress.user_id == i.id) &
                                                                 (User_progress.is_correct_1 == True))).all())
        else:
            stat_topics = int(stat_topics)
            correct = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == i.id) &
                                           (User_progress.is_correct_1 == True) &
                                           (User_progress.task_id.in_(task_id)))).all())
        members.append([i.id, i.name, i.surname, i.username, correct])
    members.sort(key=lambda x: x[4], reverse=True)
    print(members)
    figure1 = Figure(figsize=(3.5, 3.5), dpi=100)
    plt1 = figure1.subplots()
    x = [i[1] + ' ' + i[2] for i in members]
    x_1 = [i for i in range(1, len(members) + 1)]
    y = [i[4] for i in members]
    plt1.bar(x, y, color='#eaff00')
    plt1.set_title('Статистика по ученикам', color='#fcfcfc')
    plt1.set_xlabel('Ученики', color='#fcfcfc')
    plt1.tick_params(colors='#fcfcfc')  # цвет цифр на осях
    for i in range(len(members)):
        plt1.text(x_1[i] - 1 + 0.1, y[i] + 0.1, f'{y[i]}', color='#eaff00')
    plt1.set_facecolor('#03420a')
    figure1.patch.set_facecolor('#03420a')
    return figure_to_response(figure1)

@app.post('/stat/admin/topics/{stat}')
def stat_topics1(request: Request, stat: int, stat_topics: str = Form(...), db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    #geometry_class, classes, topics, members = graph(user = user, role = 'admin', db = db, stat = str(stat), stat_topics = stat_topics)
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == stat)).first()
    classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
    topics = db.scalars(select(Topic)).all()
    members = []
    if stat_topics != 'all':
        tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
        task_id = [task.id for task in tasks]

    for i in geometry_class.members:
        if stat_topics == 'all':
            correct = len(db.scalars(select(User_progress).where((User_progress.user_id == i.id) &
                                                                 (User_progress.is_correct_1 == True))).all())
        else:
            stat_topics = int(stat_topics)
            correct = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == i.id) &
                                           (User_progress.is_correct_1 == True) &
                                           (User_progress.task_id.in_(task_id)))).all())
        members.append([i.id, i.name, i.surname, i.username, correct])
    members.sort(key=lambda x: x[4], reverse=True)
    return templates.TemplateResponse(request=request, name='admin.html',
                                      context={'id': user.id, 'name': user.name, 'surname': user.surname,
                                               'username': user.username, 'role': user.role,
                                               'stat': stat, 'classes': classes, 'topics': topics,
                                               'members': members, 'stat_topics': stat_topics,
                                               'class_name': geometry_class.name})


@app.get('/edit')
def edit(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    return templates.TemplateResponse(request = request, name = 'edit.html', context = {'username': user.username})

@app.post('/edit')
def edit_post(request: Request, name: str = Form(None), surname: str = Form(None),
              username: str = Form(None), password: str = Form(None), db: Session = Depends(get_db)):
    print(1)
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
    if username is not None:
        user_check = db.scalars(select(User).where(User.username == username)).first()
        if user_check:
            return templates.TemplateResponse(request=request, name='edit.html',
                                              context={'message': 'Пользователь с таким логином уже существует'})
        user.username = username
    print(user.username, username)
    if password is not None:
        user.password = password
    db.commit()
    db.refresh(user)
    return templates.TemplateResponse(request=request, name='edit.html',
                                      context={'username': user.username,
                                               'message': 'Данные пользователя успешно обновлены'})


@app.get('/settings')
def settings(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    if user.role == 'user':
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
    else:
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
    for i in all_classes:
        print(i.name)
        for j in i.members:
            print(j.username)
    return templates.TemplateResponse(request = request, name = 'settings.html',
                                      context = {'user': user, 'all_classes': all_classes})

@app.post('/settings')
def settings_post(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    if user.schedule == 'Обучение':
        user.schedule = 'Тестирование'
    else:
        user.schedule = 'Обучение'
    db.commit()
    db.refresh(user)
    if user.role == 'user':
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
    else:
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
    members = []
    for i in all_classes:
        for member in i.members:
            progress = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == member.id) &
                                            (User_progress.is_correct_1 == True))).all())
            members.append([member, progress])
    return templates.TemplateResponse(request=request, name='settings.html',
                                      context={'user': user, 'all_classes': all_classes, 'members': members})


@app.post('/class')
def geometry_class(request: Request, name: str = Form(...), password: str = Form(...), button: str = Form(None),db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    print(button)
    if button == 'create':
        f = 0
        geometry_class = db.scalars(select(Geometry_class).
                                    where((Geometry_class.name == name)
                                          & (Geometry_class.password == password))).first()
        if geometry_class is None:
            geometry_class = Geometry_class(name = name, password = password, creator_id = user.id, creator = user)
            user.created.append(geometry_class)
            f = 1
            db.add(geometry_class)
            db.commit()
            db.refresh(geometry_class)
            db.refresh(user)
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
        members = []
        for i in all_classes:
            for member in i.members:
                progress = len(db.scalars(select(User_progress).
                                          where((User_progress.user_id == member.id) &
                                                (User_progress.is_correct == True))).all())
                members.append([member, progress])
        print(all_classes)
        if f == 0:
            message = 'Такой класс уже есть'
        else:
            message = 'Класс создан'
        return templates.TemplateResponse(request=request, name='settings.html',
                                          context={'user': user, 'message': message,
                                                   'all_classes': all_classes, 'members': members})
    else:
        geometry_class = db.scalars(select(Geometry_class).
                                    where(Geometry_class.name == name)).first()
        if geometry_class is None:
            all_classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
            members = []
            for i in all_classes:
                for member in i.members:
                    progress = len(db.scalars(select(User_progress).
                                              where((User_progress.user_id == member.id) &
                                                    (User_progress.is_correct == True))).all())
                    members.append([member, progress])
            return templates.TemplateResponse(request=request, name='settings.html',
                                              context={'user': user,
                                                       'message': 'Такого класса не существует',
                                                       'all_classes': all_classes, 'members': members})
        if geometry_class.password != password:
            message = 'Неверный пароль'
        else:
            message = 'Вы присоединились к классу'
            print(geometry_class.creator.username)
            geometry_class.members.append(user)
            db.commit()
            db.refresh(geometry_class)
            print(geometry_class.creator.username)
        all_classes = db.scalars(select(Geometry_class).where(Geometry_class.members.contains(user))).all()
        members = []
        for i in all_classes:
            for member in i.members:
                progress = len(db.scalars(select(User_progress).
                                          where((User_progress.user_id == member.id) &
                                                (User_progress.is_correct == True))).all())
                members.append([member, progress])
        return templates.TemplateResponse(request=request, name='settings.html',
                                          context={'user': user,
                                                   'message': message, 'all_classes': all_classes, 'members': members})


@app.get('/theory/{topic_id}/{task_id}')
def theory(request: Request, topic_id: int, task_id: int, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    return templates.TemplateResponse(request = request, name = 'theory.html',
                                      context = {'topic_id': topic_id, 'task_id': task_id})



@app.get('/add_own_topic/{geometry_class_id}')
def add_own_topic(request: Request, geometry_class_id: int, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == geometry_class_id)).first()
    if user.id != geometry_class.creator_id:
        return templates.TemplateResponse(request = request, name = 'settings.html',
                                          context = {'message': 'Вы не являетесь создателем этого класса'})
    all_topics = db.scalars(select(Own_topic).where(Own_topic.creator_id == user.id)).all()
    return templates.TemplateResponse(request=request, name='add.html',
                                      context={'user': user, 'geometry_class_id': geometry_class_id,
                                               'all_topics': all_topics})


@app.post('/add_own_topic/{geometry_class_id}')
def add_own_topic_post(request: Request, geometry_class_id: int, name: str = Form(...),  db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == geometry_class_id)).first()
    if user.id != geometry_class.creator_id:
        return templates.TemplateResponse(request=request, name='settings.html',
                                         context={'message': 'Вы не являетесь создателем этого класса'})
    own_topic = db.scalars(select(Own_topic).where((Own_topic.creator_id == user.id) & (Own_topic.name == name))).first()
    all_topics = db.scalars(select(Own_topic).where(Own_topic.creator_id == user.id)).all()
    if own_topic is not None:
        return templates.TemplateResponse(request=request, name='add.html',
                                          context={'user': user, 'geometry_class_id': geometry_class_id,
                                                   'message': 'Такая тема уже есть', 'all_topics': all_topics})
    own_topic = Own_topic(name = name, creator_id = user.id, geometry_class_id = geometry_class_id)
    db.add(own_topic)
    db.commit()
    db.refresh(own_topic)
    all_topics = db.scalars(select(Own_topic).where(Own_topic.creator_id == user.id)).all()
    return templates.TemplateResponse(request=request, name='add.html',
                                      context={'user': user, 'geometry_class_id': geometry_class_id,
                                               'message': 'Тема создана', 'all_topics': all_topics})



@app.post('/add_own_task/{geometry_class_id}')
def add_own_task(request: Request, geometry_class_id: int, own_topic_id: int = Form(...),
                 name: str = Form(...), draft: UploadFile = File(...), text: str = Form(...),
                 otv: str = Form(...), solution: UploadFile = File(...), db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == geometry_class_id)).first()
    if user.id != geometry_class.creator_id:
        return templates.TemplateResponse(request=request, name='settings.html',
                                          context={'message': 'Вы не являетесь создателем этого класса'})
    own_topic = db.scalars(
        select(Own_topic).where(Own_topic.id == own_topic_id)).first()
    all_topics = db.scalars(select(Own_topic).where(Own_topic.creator_id == user.id)).all()
    if own_topic is None:
        return templates.TemplateResponse(request=request, name='add.html',
                                          context={'user': user, 'geometry_class_id': geometry_class_id,
                                                   'message': 'Такой темы нет', 'all_topics': all_topics})
    own_task = db.scalars(select(Own_task).where((Own_task.own_topic_id == own_topic_id) & (Own_task.name == name))).first()
    if own_task is not None:
        return templates.TemplateResponse(request=request, name='add.html',
                                          context={'user': user, 'geometry_class_id': geometry_class_id,
                                                   'message': 'Такая задача уже есть', 'all_topics': all_topics})
    if not draft.content_type.startswith('image/'):
        print(draft.content_type)
        return templates.TemplateResponse(request=request, name='add.html',
                                          context={'user': user, 'geometry_class_id': geometry_class_id,
                                                   'message': 'Чертеж должен быть картинкой', 'all_topics': all_topics})
    if not solution.content_type.startswith('image/'):
        return templates.TemplateResponse(request=request, name='add.html',
                                          context={'user': user, 'geometry_class_id': geometry_class_id,
                                                   'message': 'Решение должно быть картинкой', 'all_topics': all_topics})
    topic = db.scalars(select(Own_topic).where(Own_topic.id == own_topic_id)).first()
    kolvo = len(topic.own_tasks)

    draft_extension = os.path.splitext(draft.filename)[1] #достаем разрешение
    solution_extension = os.path.splitext(solution.filename)[1]
    unique_draft_filename = f'{uuid.uuid4()}{draft_extension}'
    unique_solution_filename = f'{uuid.uuid4()}{solution_extension}'
    draft_path = os.path.join(UPLOAD_DIR, unique_draft_filename)
    solution_path = os.path.join(UPLOAD_DIR, unique_solution_filename)
    with open(BASE_DIR / draft_path, 'wb') as buffer:
        shutil.copyfileobj(draft.file, buffer)
    with open(BASE_DIR / solution_path, 'wb') as buffer:
        shutil.copyfileobj(solution.file, buffer)

    own_task = Own_task(name=name, number=kolvo + 1, text=text, otv=otv, draft = f'uploads/{unique_draft_filename}',
                        solution = f'uploads/{unique_solution_filename}', creator_id=user.id, own_topic_id=own_topic_id)
    db.add(own_task)
    db.commit()
    db.refresh(own_task)
    print(own_task)
    return templates.TemplateResponse(request=request, name='add.html',
                                      context={'user': user, 'geometry_class_id': geometry_class_id,
                                               'all_topics': all_topics})


@app.get('/own_task/{own_topic_id}/{own_task_id}')
def own_task(request: Request, own_topic_id: int, own_task_id: int, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    topic = db.scalars(select(Own_topic).where(Own_topic.id == own_topic_id)).first()
    task = db.scalars(select(Own_task).where((Own_task.own_topic_id == own_topic_id) &
                                             (Own_task.number == own_task_id))).first()
    kolvo = len(topic.own_tasks)
    message = None
    return templates.TemplateResponse(request=request, name='own_task.html',
                                      context={'task': task, 'kolvo': kolvo,
                                               'topic_id': own_topic_id, 'task_id': own_task_id,
                                               'username': user.username, 'schedule': user.schedule,
                                               'message': message})

@app.post('/own_task/{own_topic_id}/{own_task_id}')
def own_task_post(request: Request, own_topic_id: int, own_task_id: int,
                  otv: str = Form(None), button: str = Form(None), db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    topic = db.scalars(select(Own_topic).where(Own_topic.id == own_topic_id)).first()
    task = db.scalars(select(Own_task).where((Own_task.own_topic_id == own_topic_id) &
                                             (Own_task.number == own_task_id))).first()
    kolvo = len(topic.own_tasks)
    message = None
    if button == 'next':
        if own_task_id == kolvo:
            progress = db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                  (User_progress_own.own_topic_id == own_topic_id) &
                                                                  (User_progress_own.is_correct == True))).all()
            print(progress)
            progress = len(progress)
            progresses = db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                                  (User_progress_own.own_topic_id == own_topic_id))).all()
            for i in progresses:
                i.saved = False
                i.is_correct_1 = i.is_correct
                i.is_correct = False
            db.commit()
            return templates.TemplateResponse(request=request, name='result.html',
                                              context={'kolvo': kolvo, 'username': user.username,
                                                       'progress': int(progress), 'schedule': user.schedule})
        else:
            return RedirectResponse(f'/own_task/{own_topic_id}/{own_task_id + 1}', status_code = 303)
    elif button == 'pred':
        return RedirectResponse(f'/own_task/{own_topic_id}/{own_task_id - 1}', status_code=303)
    elif button == 'save':
        progress = db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                          (User_progress_own.own_task_id == task.id))).first()
        if progress is None:
            progress = User_progress_own(user_id=user.id, own_topic_id = topic.id,
                                         own_task_id=task.id,
                                     is_correct=(otv == task.otv),
                                     is_correct_1 = (otv == task.otv))
            db.add(progress)
            db.commit()
            db.refresh(progress)
        else:
            if not progress.is_correct and otv == task.otv:
                progress.is_correct = True
                progress.is_correct_1 = True
                #progress.user_result = 1
            elif progress.is_correct and otv != task.otv:
                progress.is_correct = False
                progress.is_correct_1 = False
                #progress.user_result = 0
            db.commit()
            db.refresh(progress)
        progress.saved = True
        db.commit()
        db.refresh(progress)
        return templates.TemplateResponse(request=request, name='own_task.html',
                                          context={'task': task, 'kolvo': kolvo, 'task_id': own_task_id,
                                                   'topic_id': own_topic_id,
                                                   'username': user.username, 'otv': otv,
                                                   'button': button, 'schedule': user.schedule,
                                                   'message': 'Ответ сохранен'})
    elif button == 'check':
        result = ''
        color = ''
        if not otv:
            result = 'Выберите ответ'
            color = '#ff7803'
        elif otv == task.otv:
            result = 'Верно'
            color = '#02fa30'
        else:
            result = 'Неверно'
            color = '#ff0703'
        progress = db.scalars(select(User_progress_own).where((User_progress_own.user_id == user.id) &
                                                          (User_progress_own.own_task_id == task.id))).first()
        if progress is None:
            progress = User_progress_own(user_id=user.id, own_topic_id = topic.id,
                                        own_task_id=task.id,
                                        is_correct=(otv == task.otv),
                                        is_correct_1 = (otv == task.otv))
            db.add(progress)
            db.commit()
            db.refresh(progress)
        else:
            if not progress.is_correct and otv == task.otv:
                progress.is_correct = True
                progress.is_correct_1 = True
                #progress.user_result = 1
            elif progress.is_correct and otv != task.otv:
                progress.is_correct = False
                progress.is_correct_1 = False
                #progress.user_result = 0
            db.commit()
            db.refresh(progress)
        return templates.TemplateResponse(request=request, name='own_task.html',
            context={'result': result, 'task': task, 'color': color, 'kolvo': kolvo,
                     'topic_id': own_topic_id, 'task_id': own_task_id,
                     'username': user.username, 'otv': otv, 'button': button,
                     'schedule': user.schedule})


@app.get('/all')
def all(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    all_users = len(db.scalars(select(User)).all())
    users = db.scalars(select(User).where(User.role == 'user')).all()
    admins = db.scalars(select(User).where(User.role == 'admin')).all()
    for i in admins:
        print('admin:', i.name)
    members = []
    for i in users:
        all_classes = ''
        correct_balayan = len(db.scalars(select(User_progress).where((User_progress.user_id == i.id)
                                                             & (User_progress.is_correct_1 == True))).all())
        correct_own = len(db.scalars(select(User_progress_own).where((User_progress_own.user_id == i.id)
                                                             & (User_progress_own.is_correct_1 == True))).all())
        correct = correct_balayan + correct_own
        for j in i.classes:
            all_classes += j.name + ', '
        #print(all_classes)
        if all_classes:
            all_classes = all_classes[:-2]
        members.append([i.name, i.surname, all_classes, correct])
    members.sort(key = lambda x: x[3], reverse = True)
    if len(members) > 5:
        members = members[:5]


    active_teachers = []
    for i in admins:
        own_tasks = 0
        all_classes = ''
        for j in i.created:
            for k in j.own_topics:
                print(k.name)
                own_tasks += len(k.own_tasks)
            print(own_tasks)
            all_classes += j.name + ', '
        if all_classes:
            all_classes = all_classes[:-2]
        active_teachers.append([i.name, i.surname, own_tasks, all_classes])
    active_teachers.sort(key = lambda x: x[2], reverse = True)
    if len(active_teachers) > 5:
        active_teachers = active_teachers[:5]
    return templates.TemplateResponse(request = request, name = 'all.html',
                                      context = {'all_users': all_users, 'users': len(users),
                                                 'admins': len(admins), 'members': members,
                                                 'active_teachers': active_teachers})



app.mount('/uploads', StaticFiles(directory = BASE_DIR / 'uploads'), name = 'uploads')
app.mount("/", StaticFiles(directory=BASE_DIR / "static"), name="static")