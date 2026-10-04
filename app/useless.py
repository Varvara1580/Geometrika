#функция user после вызова ф-ии graph
'''topic_stats = []
        total = []
        correct = []
        correct_all = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == user.id) &
                                            (User_progress.is_correct_1 == True))).all())
        print(correct_all)
        incorrect_all = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == user.id) &
                                            (User_progress.is_correct_1 == False))).all())
        print(incorrect_all)
        all = len(db.scalars(select(Task)).all())
        print(all)
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
            total.append(len(tasks))
            correct.append(progress)
        x = [i for i in range(1, 26)]
        print(len(correct))
        plt.figure(figsize = (11.5, 2.5), dpi = 100)
        plt.bar(x, total, color = '#eaff00')
        plt.bar(x, correct, color = '#02fa30')
        plt.title('Решенные задачи по темам', color = '#fcfcfc')
        plt.xlabel('Номер темы', color = '#fcfcfc')
        plt.ylabel('Количество задач', color = '#fcfcfc')
        plt.tick_params(colors = '#fcfcfc') #цвет цифр на осях
        plt.xticks(range(1, 26, 1)) # точность шкалы x
        for i in range(25):
            plt.text(x[i] + 0.1, total[i] + 2, f'{correct[i]}', color = '#eaff00')
        plt.legend(['Неверно', 'Верно'], loc='center left', bbox_to_anchor=(1, 0.5))
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/bar/{user.id}.png', dpi = 100)
        plt.clf()



        plt.figure(figsize=(5, 5), dpi=100)
        plt.pie(
            #[correct_all, incorrect_all, all - correct_all - incorrect_all],
            #colors = ['#02fa30', '#ff0703', '#ff7803'],
            #labels = ['Верно', 'Неверно', 'Не решено']
            [correct_all, all - correct_all],
            colors=['#02fa30', '#eaff00'],
            #labels = ['Верно', 'Неверно'],
            wedgeprops = {'width': 0.3},
            autopct = '%1.0f%%',
            pctdistance = 0.5,
            textprops = {'color': '#fcfcfc', 'weight': 'bold'}
        )
        plt.legend(['Верно', 'Неверно'], loc = 'upper center', bbox_to_anchor = (0.5, -0.01), ncol = 4)
        plt.title('Процент решенных задач', color = '#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/pie/{user.id}.png', dpi = 100)
        plt.clf()'''













#функция user_stat после вызова ф-ии graph
'''if stat_topics == 'all':
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
    plt.figure(figsize=(5, 5), dpi=100)
    plt.pie(
        [correct_all, all - correct_all],
        colors=['#02fa30', '#eaff00'],
        # labels = ['Верно', 'Неверно'],
        wedgeprops={'width': 0.3},
        autopct='%1.0f%%',
        pctdistance=0.5,
        textprops={'color': '#fcfcfc', 'weight': 'bold'}
    )
    plt.legend(['Верно', 'Неверно'], loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4)
    plt.title('Процент решенных задач', color='#fcfcfc')
    plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
    ax = plt.gca()
    ax.set_facecolor('#03420a')
    fig = plt.gcf()
    fig.patch.set_facecolor('#03420a')
    plt.savefig(f'static/img/graph/pie/{user.id}.png', dpi=100)
    plt.clf()

    topics = db.scalars(select(Topic)).all()
    topic_stats = []
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
        topic_stats.append({'name': topic.name, 'total': len(tasks), 'correct': progress, 'status': status})'''







#функция admin_stat после вызова ф-ии graph
'''topics = db.scalars(select(Topic)).all()
        topic_stats = []
        total = []
        correct = []
        correct_all = len(db.scalars(select(User_progress).
                                     where((User_progress.user_id == user.id) &
                                           (User_progress.is_correct_1 == True))).all())
        print(correct_all)
        incorrect_all = len(db.scalars(select(User_progress).
                                       where((User_progress.user_id == user.id) &
                                             (User_progress.is_correct_1 == False))).all())
        print(incorrect_all)
        all = len(db.scalars(select(Task)).all())
        print(all)
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
            total.append(len(tasks))
            correct.append(progress)
        x = [i for i in range(1, 26)]
        print(len(correct))
        plt.figure(figsize=(11.5, 2.5), dpi=100)
        plt.bar(x, total, color='#eaff00')
        plt.bar(x, correct, color='#02fa30')
        plt.title('Решенные задачи по темам', color='#fcfcfc')
        plt.xlabel('Номер темы', color='#fcfcfc')
        plt.ylabel('Количество задач', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        plt.xticks(range(1, 26, 1))  # точность шкалы x
        for i in range(25):
            plt.text(x[i] + 0.1, total[i] + 2, f'{correct[i]}', color='#eaff00')
        plt.legend(['Неверно', 'Верно'], loc='center left', bbox_to_anchor=(1, 0.5))
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/bar/{user.id}.png', dpi=100)
        plt.clf()

        plt.figure(figsize=(5, 5), dpi=100)
        plt.pie(
            # [correct_all, incorrect_all, all - correct_all - incorrect_all],
            # colors = ['#02fa30', '#ff0703', '#ff7803'],
            # labels = ['Верно', 'Неверно', 'Не решено']
            [correct_all, all - correct_all],
            colors=['#02fa30', '#eaff00'],
            # labels = ['Верно', 'Неверно'],
            wedgeprops={'width': 0.3},
            autopct='%1.0f%%',
            pctdistance=0.5,
            textprops={'color': '#fcfcfc', 'weight': 'bold'}
        )
        plt.legend(['Верно', 'Неверно'], loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4)
        plt.title('Процент решенных задач', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/pie/{user.id}.png', dpi=100)
        plt.clf()'''






#функция stat_topics после вызова ф-ии graph
'''print('1234567890', stat_topics)
    geometry_class = db.scalars(select(Geometry_class).where(Geometry_class.id == stat)).first()
    classes = db.scalars(select(Geometry_class).where(Geometry_class.creator_id == user.id)).all()
    topics = db.scalars(select(Topic)).all()
    members = []
    if stat_topics == 'all':
        all = len(db.scalars(select(Task)).all())
    else:
        tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
        task_id = [task.id for task in tasks]
        all = len(db.scalars(select(Task).where(Task.id.in_(task_id))).all())


    for i in geometry_class.members:
        if stat_topics == 'all':
            correct = len(db.scalars(select(User_progress).where((User_progress.user_id == i.id) &
                                                                 (User_progress.is_correct_1 == True))).all())
        else:
            stat_topics = int(stat_topics)
            tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
            task_id = [task.id for task in tasks]
            correct = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == i.id) &
                                            (User_progress.is_correct_1 == True) &
                                            (User_progress.task_id.in_(task_id)))).all())
        members.append([i.id, i.name, i.surname, i.username, correct])
    members.sort(key = lambda x: x[4], reverse = True)
    print(members)
    x = [i[1] + ' ' + i[2] for i in members]
    x_1 = [i for i in range(1, len(members) + 1)]
    y = [i[4] for i in members]
    print(x)
    print(x_1)
    print(y)

    <<<<x = [i for i in range(1, 26)]
    plt.figure(figsize=(3.5, 3.5), dpi=100)
    for i in range(len(members)):
        if members[i][4] >= 0.75 * all:
            color = '#02fa30'
        elif 0.5 <= members[i][4] < 0.75:
            color = '#eaff00'
        else:
            color = '#ff0703'
        plt.bar([members[i][1] + ' ' + members[i][2]], [members[i][4]], color = color)
        plt.text(x[i] + 0.1, members[i][4] + 2, f'{members[i][4]}', color = color)>>>>

    plt.figure(figsize=(3.5, 3.5), dpi=100)
    plt.bar(x, y, color ='#eaff00')
    plt.title('Статистика по ученикам', color='#fcfcfc')
    plt.xlabel('Ученики', color='#fcfcfc')
    plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
    for i in range(len(members)):
        plt.text(x_1[i] - 1 + 0.1, y[i] + 0.1, f'{y[i]}', color='#eaff00')
    ax = plt.gca()
    ax.set_facecolor('#03420a')
    fig = plt.gcf()
    fig.patch.set_facecolor('#03420a')
    plt.savefig(f'static/img/graph/bar/admin/{user.id}.png', dpi=100)
    plt.clf()'''







#ф-я graph, после ф-ии task_post и до ф-ии figure_to_response
'''def graph(user: User, role: str, db: Session, stat_topics: str = 'all', stat: str = 'my'):
    topics = db.scalars(select(Topic)).all()
    if role == 'user' or (role == 'admin' and stat == 'my'): #своя статистика
        if stat_topics == 'all':
            correct_all = len(db.scalars(select(User_progress).
                                         where((User_progress.user_id == user.id) &
                                               (User_progress.is_correct_1 == True))).all())
            #incorrect_all = len(db.scalars(select(User_progress).
            #                               where((User_progress.user_id == user.id) &
            #                                     (User_progress.is_correct_1 == False))).all())
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

        topic_stats = []
        total = []
        correct = []
        print(all)
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
            total.append(len(tasks))
            correct.append(progress)
        x = [i for i in range(1, 26)]
        print(len(correct))
        plt.figure(figsize=(11.5, 2.5), dpi=100)
        plt.bar(x, total, color='#eaff00')
        plt.bar(x, correct, color='#02fa30')
        plt.title('Решенные задачи по темам', color='#fcfcfc')
        plt.xlabel('Номер темы', color='#fcfcfc')
        plt.ylabel('Количество задач', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        plt.xticks(range(1, 26, 1))  # точность шкалы x
        for i in range(25):
            plt.text(x[i] + 0.1, total[i] + 2, f'{correct[i]}', color='#eaff00')
        plt.legend(['Неверно', 'Верно'], loc='center left', bbox_to_anchor=(1, 0.5))
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/bar/{user.id}.png', dpi=100)
        plt.clf()

        plt.figure(figsize=(5, 5), dpi=100)
        plt.pie(
            # [correct_all, incorrect_all, all - correct_all - incorrect_all],
            # colors = ['#02fa30', '#ff0703', '#ff7803'],
            # labels = ['Верно', 'Неверно', 'Не решено']
            [correct_all, all - correct_all],
            colors=['#02fa30', '#eaff00'],
            # labels = ['Верно', 'Неверно'],
            wedgeprops={'width': 0.3},
            autopct='%1.0f%%',
            pctdistance=0.5,
            textprops={'color': '#fcfcfc', 'weight': 'bold'}
        )
        plt.legend(['Верно', 'Неверно'], loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4)
        plt.title('Процент решенных задач', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/pie/{user.id}.png', dpi=100)
        plt.clf()

        if role == 'admin':
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


        return all, correct_all, topic_stats, own_topic_stats
    else: #статистика по классам
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
                #tasks = db.scalars(select(Task).where(Task.topic_id == stat_topics)).all()
                #task_id = [task.id for task in tasks]
                correct = len(db.scalars(select(User_progress).
                                         where((User_progress.user_id == i.id) &
                                               (User_progress.is_correct_1 == True) &
                                               (User_progress.task_id.in_(task_id)))).all())
            members.append([i.id, i.name, i.surname, i.username, correct])
        members.sort(key=lambda x: x[4], reverse=True)
        print(members)
        x = [i[1] + ' ' + i[2] for i in members]
        x_1 = [i for i in range(1, len(members) + 1)]
        y = [i[4] for i in members]
        plt.figure(figsize=(3.5, 3.5), dpi=100)
        plt.bar(x, y, color='#eaff00')
        plt.title('Статистика по ученикам', color='#fcfcfc')
        plt.xlabel('Ученики', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        for i in range(len(members)):
            plt.text(x_1[i] - 1 + 0.1, y[i] + 0.1, f'{y[i]}', color='#eaff00')
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/bar/admin/{user.id}.png', dpi=100)
        plt.clf()
        return geometry_class, classes, topics, members'''



#ф-я user, в первом if, после формирования topic_stats
'''plt.figure(figsize=(5, 5), dpi=100)
        plt.pie(
            # [correct_all, incorrect_all, all - correct_all - incorrect_all],
            # colors = ['#02fa30', '#ff0703', '#ff7803'],
            # labels = ['Верно', 'Неверно', 'Не решено']
            [correct_all, all - correct_all],
            colors=['#02fa30', '#eaff00'],
            # labels = ['Верно', 'Неверно'],
            wedgeprops={'width': 0.3},
            autopct='%1.0f%%',
            pctdistance=0.5,
            textprops={'color': '#fcfcfc', 'weight': 'bold'}
        )
        plt.legend(['Верно', 'Неверно'], loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4)
        plt.title('Процент решенных задач', color='#fcfcfc')
        plt.tick_params(colors='#fcfcfc')  # цвет цифр на осях
        ax = plt.gca()
        ax.set_facecolor('#03420a')
        fig = plt.gcf()
        fig.patch.set_facecolor('#03420a')
        plt.savefig(f'static/img/graph/pie/{user.id}.png', dpi=100)
        plt.clf()'''



#ф-я graph, после ф-ии user и до ф-ии admin_stat
'''@app.post('/stat/pie_topics') #изменение графика pie по темам
def pie_topics(request: Request, stat_topics: str = Form(...), db: Session = Depends(get_db)):
    user = get_user(request, db)
    if user is None:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'message': 'Вы не вошли в систему'})
    topics = db.scalars(select(Topic)).all()
    all, correct_all, topic_stats, own_topic_stats = graph(user = user, role='user', db=db, stat_topics = stat_topics)
    return templates.TemplateResponse(request=request, name='user.html',
                                      context={'id': user.id, 'name': user.name, 'surname': user.surname,
                                               'username': user.username, 'role': user.role,
                                               'topic_stats': topic_stats, 'own_topic_stats': own_topic_stats,
                                               'all': all, 'correct_all': correct_all, 'topics': topics,
                                               'stat_topic': stat_topics})'''






#ф-я settings, до for
'''members = [[j for j in all_classes] for i in range(len(all_classes))]
    for i in range(len(all_classes)):
        for member in all_classes[i].members:
            progress = len(db.scalars(select(User_progress).
                                      where((User_progress.user_id == member.id) &
                                            (User_progress.is_correct_1 == True))).all())
            members[i].append([member, progress])
    all_1 = []
    for i in all_classes:
        own_topics = db.scalars(select(Own_topic).where(Own_topic.geometry_class_id == i.id))'''