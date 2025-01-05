# База данных по правилам DnD

Проект направлен на улучшение RAG-компоненты (Retrieval-Augmented Generation) Агента-помощника для Dungeons and Dragons (DnD). Включает сбор, обработку и сохранение данных из официальных правил, бестиария, предметов и заклинаний.

---

## Содержание

1. [Сбор данных (парсинг)](#сбор-данных-парсинг)
2. [Препроцессинг и контроль качества данных](#препроцессинг-и-контроль-качества-данных)
3. [База данных](#база-данных)

---

## Сбор данных (парсинг)

**Каталог:** `./parsing/`

Происходит автоматический парсинг данных с сайта [dnd.su](https://dnd.su).  

### Что парсится:
- Основные и продвинутые правила:
  - `dop_info.py` — дополнительные сведения.
  - `mechanics.py` — игровые механики.
- Бестиарий (`bestiary.py`).
- Предметы (`items.py`).
- Заклинания (`spells.py`).

### Бэклог:
- Провести рефакторинг кода.
- Добавить парсинг классов.

---

## Препроцессинг и контроль качества данных

**Каталог:** `./preprocessing/`

### Основные задачи:
- Генерация отдельных признаков из текста.
- Небольшой EDA (Exploratory Data Analysis).
- Заполнение пропусков в данных.

### Бэклог:
- рефакторинг

---

## База данных

**Каталог:** `./database/`

### Реализовано:
- Создание баз данных для:
  - Бестиария.
  - Заклинаний.
  - Предметов
  - Правил

### Бэклог:

- Провести рефакторинг.


---

## Дэшборды

**Каталог:** `./dashboards/`

### Реализовано:
- Общая часть:
  -Первые 5 строк датафрейма и статистика по Null-ам.
  ![general_1](/images/general_1.png)
- Метрики косинусного расстояния
  ![general_2](/images/general_2.png)
- Для таблицы бестиария метрика среднего количество способностей, чтобы отслеживать дубликаты:
  ![creature_1](/images/creature_1.png)
- Для таблицы предметов метрика средней цены предметов, чтобы отслеживать выбросы:
  ![items_1](/images/items_1.png)
- Для таблицы правил метрика средней длины чанка в предложениях, чтобы отслеживать проблемы с чанкингом:
  ![rules_1](/images/rules_1.png)
- Для таблицы заклинаний распределения по школам и уровням, чтобы отслеживать смену распределений:
  ![spells_1](/images/spells_1.png)


## Установка и запуск

### Требования:
- Python 3.12+
- Установленные зависимости из poetry

### Установка:
1. Клонируйте репозиторий:
   ```bash
   git clone <URL_репозитория>
   cd <имя_репозитория>


