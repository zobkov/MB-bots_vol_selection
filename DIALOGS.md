# Документация по диалогам бота

2. MenuSG.main → ApplicationSG.full_name (кнопка "Заполнить анкету")
3. ApplicationSG.personal_qualities → DepartmentSelectionSG.logistics (автоматически)
4. DepartmentSelectionSG.overview → ApplicationSG.motivation (через done/result)
5. ApplicationSG.overview → MenuSG.main (после отправки анкеты)труктура диалогов

### StartSG - Стартовый диалог
- `start` - приветственное окно с изображением и кнопкой перехода в меню

### MenuSG - Главное меню
- `main` - основное меню с информацией о статусе заявки
- `support` - контакты поддержки

### ApplicationSG - Анкета (первый этап)
- `full_name` - ввод ФИО
- `course` - выбор курса обучения
- `dormitory` - вопрос о проживании в общежитии
- `email` - ввод корпоративной почты
- `phone` - запрос контактного телефона
- `personal_qualities` - описание личных качеств (автоматически переходит к выбору отделов)
- `motivation` - описание мотивации
- `overview` - обзор всех ответов и подтверждение

### DepartmentSelectionSG - Выбор отделов
- `logistics` - оценка отдела Логистика
- `marketing` - оценка отдела Маркетинг
- `pr` - оценка отдела PR
- `program` - оценка отдела Программа
- `partners` - оценка отдела Партнеры
- `overview` - обзор выставленных оценок

## Переходы между диалогами

1. `/start` → StartSG.start → MenuSG.main
2. `/menu` → MenuSG.main
3. MenuSG.main → ApplicationSG.full_name (кнопка "Заполнить анкету")
4. ApplicationSG.departments → DepartmentSelectionSG.logistics
5. DepartmentSelectionSG.overview → ApplicationSG.motivation (через done/result)
6. ApplicationSG.overview → MenuSG.main (после отправки анкеты)

## Хранение данных

### dialog_data
В `dialog_manager.dialog_data` хранятся:
- `full_name` - ФИО пользователя
- `course` - код курса (1_bachelor, 2_bachelor, и т.д.)
- `course_display` - отображаемое название курса
- `dormitory` - булево значение проживания в общежитии
- `email` - корпоративная почта
- `phone` - номер телефона
- `personal_qualities` - текст о личных качествах
- `motivation` - текст мотивации
- `logistics_rating` - оценка отдела Логистика (1-5)
- `marketing_rating` - оценка отдела Маркетинг (1-5)
- `pr_rating` - оценка отдела PR (1-5)
- `program_rating` - оценка отдела Программа (1-5)
- `partners_rating` - оценка отдела Партнеры (1-5)

### middleware_data
Через middleware передаются:
- `config` - объект конфигурации
- `db` - объект подключения к базе данных

## Валидация

### Email
- Должен заканчиваться на `@spbu.ru`, `@student.spbu.ru` или `@gsom.spbu.ru`
- Проверяется в `email_check()`

### Телефон
- Принимается как текстовый ввод, так и через кнопку "Поделиться контактом"
- Обрабатывается в `on_phone_input()` и `on_contact_received()`

## Репозитории

### UserRepository
- `get_or_create_user()` - получение или создание пользователя
- `update_stage1_status()` - обновление статуса первого этапа
- `get_user_by_telegram_id()` - получение пользователя по telegram_id

### ApplicationRepository
- `create_application()` - создание заявки
- `parse_full_name()` - разделение ФИО на составные части
- `get_user_applications()` - получение заявок пользователя

## Команды

- `/start` - запуск бота (StartMode.RESET_STACK)
- `/menu` - переход в меню (StartMode.RESET_STACK)
