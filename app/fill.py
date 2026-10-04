from fastapi import Depends
from app.Models import Topic, Task
import json
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column


def read_txt():
    with open('topic_name.txt', 'r', encoding ='utf-8') as f:
        a = [i.strip() for i in f]
    return a

def read_task():
    with open('otv.json', 'r', encoding ='utf-8') as f:
        b = json.load(f)
    return b

def init_db(db: Session):
    print(1)
    topics_name = read_txt()
    tasks_content = read_task()
    topics = db.scalars(select(Topic)).all()
    if len(topics) == 0:
        topics = None
    if topics is None:
        for i in range(len(topics_name)):
            topic = Topic(name = topics_name[i])
            print(topic)
            db.add(topic)
            db.commit()
            db.refresh(topic)
        tasks = db.scalars(select(Task)).all()
        print(tasks)
        print(3)
        if len(tasks) == 0:
            tasks = None
        print(tasks)
        if tasks is None:
            for topic_number in tasks_content:
                id = topic_number
                topic = tasks_content[topic_number]
                for task_number in topic:
                    var = topic[task_number]
                    task = Task(
                        number = int(task_number),
                        name = task_number,
                        var_1 = var[0],
                        var_2 = var[1],
                        var_3 = var[2],
                        var_4 = var[3],
                        otv = var[4],
                        #draft = ,
                        #solution = pass,
                        topic_id = id
                    )
                    db.add(task)
                    db.commit()
                    db.refresh(task)
    print(2)