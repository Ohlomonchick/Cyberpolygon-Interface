# 🚀 Быстрый старт ELK Stack 9.1.1 (Упрощенная версия)

## Шаг 1: Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env при необходимости
```

## Шаг 2: Исправление прав доступа (только для Windows)
```bash
fix-filebeat-permissions.bat
```

## Шаг 3: Запуск ELK Stack
```bash
run_elk.bat
```

## Шаг 4: Проверка работы
- **Kibana**: http://localhost:5601 (аутентификация включена по умолчанию)
- **Elasticsearch**: http://localhost:9200 (без аутентификации)
- **Logstash API**: http://localhost:9600

## Остановка
```bash
stop_elk.bat
```

## Полезные команды
```bash
# Просмотр логов
docker-compose logs elasticsearch
docker-compose logs logstash
docker-compose logs kibana

# Статус сервисов
docker-compose ps

# Перезапуск
docker-compose restart elasticsearch
```

## 🔑 Аутентификация
- **Elasticsearch**: аутентификация отключена для упрощения
- **Kibana**: аутентификация включена по умолчанию (требует настройки пользователей)
- Подходит для разработки и тестирования

⚠️ **Для продакшена рекомендуется настроить аутентификацию для всех компонентов!**
