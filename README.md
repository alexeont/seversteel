# Тестовое задание для стажировки  IT HUB «Северсталь»
### Дополнительные фишки
- фильтрация реализована через fastapi-filter==2.0.0
- миграции бд через alembic==1.13.1
  
### Запуск
1. клонировать репозиторий, установить зависимости в виртуальное окружение
2. заполнить .env по примеру (.env.example) для подключения к своей бд на PostgreSQL
3. создать таблицы: `alembic upgrade head`
4. запустить сервер: `uvicorn main:app --reload`
5. API доступен в браузере по адресу `http://localhost:8000/docs`
