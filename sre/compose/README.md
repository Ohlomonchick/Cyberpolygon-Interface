# Cyberpolygon Docker Compose Setup

Этот docker-compose файл настраивает PostgreSQL 15 и ELK Stack 9.1.1 для проекта Cyberpolygon.

## 🗄️ PostgreSQL

### Особенности
- PostgreSQL 15
- Порт: 5431 (внешний) -> 5432 (внутренний)
- Настроен для подключения отовсюду (`listen_addresses='*'`)
- Оптимизированные настройки производительности
- Постоянное хранение данных в Docker volume

## 📊 ELK Stack 9.1.1 (Упрощенная версия)

### Компоненты
- **Elasticsearch 9.1.1** - поисковая система и аналитика
- **Logstash 9.1.1** - обработка и трансформация логов
- **Kibana 9.1.1** - веб-интерфейс для визуализации
- **Filebeat 9.1.1** - сбор логов с хоста

### Особенности
- Без SSL/TLS шифрования (упрощено)
- Отключена безопасность для упрощения настройки
- Оптимизированные настройки памяти
- Автоматическая обработка логов

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

Скопируйте файл переменных окружения:
```bash
cp env.example .env
```

При необходимости отредактируйте `.env` файл:
```bash
# PostgreSQL
POSTGRES_PASSWORD=your_secure_password

# ELK Stack
ELASTIC_PASSWORD=your_elastic_password
```

### 2. Исправление прав доступа (только для Windows)

**Для Windows:**
```bash
fix-filebeat-permissions.bat
```

### 3. Запуск ELK Stack

**Для Windows:**
```bash
run_elk.bat
```

**Для Linux/macOS:**
```bash
docker-compose up -d elasticsearch logstash kibana filebeat
```

### 4. Запуск сервисов

**Только PostgreSQL:**
```bash
docker-compose up -d postgres
```

**Только ELK Stack:**
```bash
run_elk.bat
```

**Все сервисы:**
```bash
docker-compose up -d
```

### 5. Проверка статуса
```bash
docker-compose ps
```

## 🗄️ Подключение к базе данных

### Через psql (внутри контейнера):
```bash
docker-compose exec postgres psql -U postgres -d cyberpolygon
```

### Через внешний клиент:
- Host: `localhost`
- Port: `5431`
- Database: `cyberpolygon`
- Username: `postgres`
- Password: `postgres` (или значение из .env)

### Пример подключения через Python:
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5431,
    database="cyberpolygon",
    user="postgres",
    password="postgres"
)
```

## 📊 Доступ к ELK Stack

### Elasticsearch
- URL: `http://localhost:9200`
- Аутентификация: не требуется
- Проверка статуса: `curl http://localhost:9200/_cluster/health`

### Kibana
- URL: `http://localhost:5601`
- Аутентификация: включена по умолчанию (требует настройки пользователей)

### Logstash API
- URL: `http://localhost:9600`
- Проверка статуса: `curl http://localhost:9600/_node/stats`
- Порт Beats: `5044`

## 🛠️ Управление

### Остановка всех сервисов:
```bash
docker-compose down
```

### Остановка с удалением данных:
```bash
docker-compose down -v
```

### Остановка только ELK Stack:
```bash
stop_elk.bat
```

### Просмотр логов:
```bash
# PostgreSQL
docker-compose logs postgres

# ELK Stack
docker-compose logs elasticsearch
docker-compose logs logstash
docker-compose logs kibana
docker-compose logs filebeat
```

### Перезапуск:
```bash
docker-compose restart [service_name]
```

## ⚙️ Настройки производительности

### PostgreSQL
Docker-compose включает оптимизированные настройки PostgreSQL:
- `shared_buffers`: 256MB
- `effective_cache_size`: 1GB
- `work_mem`: 4MB
- `maintenance_work_mem`: 64MB
- `max_connections`: 200

### ELK Stack
- **Elasticsearch**: 512MB heap (`ES_JAVA_OPTS=-Xms512m -Xmx512m`)
- **Logstash**: 256MB heap (`LS_JAVA_OPTS=-Xms256m -Xmx256m`)
- **Filebeat**: оптимизирован для сбора логов

Эти настройки подходят для большинства средних нагрузок. Для продакшена рекомендуется настроить под конкретные требования.

## 🔐 Безопасность

### PostgreSQL
⚠️ **Важно**: В продакшене обязательно измените пароль по умолчанию и настройте соответствующие правила доступа.

### ELK Stack
- SSL/TLS шифрование отключено для упрощения
- Максимально минимальная конфигурация Kibana
- Безопасность включена по умолчанию в Kibana 9.1.1
- ⚠️ **Важно**: Для продакшена рекомендуется настроить SSL/TLS и аутентификацию!
- Подходит для разработки и тестирования

## 📝 Дополнительная документация

- [ELK Stack Configuration](elk-configs/README.md) - подробная документация по настройке ELK
- [Migration Script](migrate_data.py) - скрипт для миграции данных из SQLite в PostgreSQL
