# ELK Stack 9.1.1 Configuration (Simplified without SSL)

Этот каталог содержит упрощенные конфигурации для ELK Stack (Elasticsearch, Logstash, Kibana) версии 9.1.1 без SSL, адаптированные для проекта Cyberpolygon.

## 🚀 Быстрый старт

### 1. Запуск ELK Stack

**Для Windows:**
```bash
run_elk.bat
```

**Для Linux/macOS:**
```bash
docker-compose up -d elasticsearch logstash kibana filebeat
```

**Примечание:** В упрощенной версии SSL сертификаты не требуются, что значительно упрощает настройку и запуск.

### 2. Настройка переменных окружения

Скопируйте файл переменных окружения:
```bash
cp ../env.example ../.env
```

Отредактируйте `.env` файл при необходимости:
```bash
# Измените пароль Elasticsearch
ELASTIC_PASSWORD=your_secure_password
```

### 3. Запуск ELK Stack

```bash
docker-compose up -d elasticsearch logstash kibana filebeat
```

## 📋 Компоненты

### Elasticsearch 9.1.1
- **Порт**: 9200 (HTTP), 9300 (Transport)
- **Конфигурация**: `elasticsearch/elasticsearch.yml`
- **Особенности**:
  - Отключена безопасность для упрощения (xpack.security.enabled=false)
  - Без SSL/TLS шифрования
  - Оптимизированные настройки памяти
  - Single-node кластер

### Logstash 9.1.1
- **Порты**: 5044 (Beats), 9600 (API)
- **Конфигурация**: `logstash/logstash.yml`
- **Пайплайны**:
  - `main.conf` - основной пайплайн для обработки логов от Filebeat

### Kibana 9.1.1
- **Порт**: 5601
- **Конфигурация**: `kibana/kibana.yml`
- **Особенности**:
  - HTTP подключение к Elasticsearch
  - Максимально минимальная конфигурация
  - Отключена телеметрия
  - Безопасность включена по умолчанию
  - Только основные настройки сервера

### Filebeat 9.1.1
- **Конфигурация**: `filebeat/filebeat.yml`
- **Функции**:
  - Сбор системных логов
  - Сбор логов приложений
  - Метаданные Docker и Kubernetes
  - Отправка в Logstash

## 🔐 Безопасность

### Упрощенная конфигурация
- SSL/TLS шифрование отключено для упрощения настройки
- Аутентификация отключена (xpack.security.enabled=false)
- Подходит для разработки и тестирования

⚠️ **Важно**: Для продакшена рекомендуется включить SSL/TLS и аутентификацию!

## 📊 Мониторинг

### Проверка статуса Elasticsearch
```bash
curl http://localhost:9200/_cluster/health
```

### Проверка статуса Logstash
```bash
curl http://localhost:9600/_node/stats
```

### Доступ к Kibana
Откройте в браузере: http://localhost:5601

## 🔧 Настройка

### Индексы
По умолчанию создаются следующие индексы:
- `logstash-YYYY.MM.dd` - логи через Logstash
- `filebeat-YYYY.MM.dd` - логи через Filebeat

### Шаблоны индексов
Автоматически создаются шаблоны с настройками:
- 1 шард
- 0 реплик (для разработки)

## 🐛 Устранение неполадок

### Проблемы с SSL
1. Убедитесь, что сертификаты сгенерированы
2. Проверьте права доступа к файлам сертификатов
3. Проверьте конфигурацию SSL в файлах конфигурации

### Проблемы с памятью
1. Увеличьте `ES_JAVA_OPTS` в docker-compose.yml
2. Увеличьте `LS_JAVA_OPTS` для Logstash
3. Проверьте доступную память на хосте

### Проблемы с подключением
1. Проверьте, что все сервисы запущены
2. Проверьте сетевые настройки Docker
3. Проверьте логи контейнеров: `docker-compose logs [service_name]`

### Проблемы с логированием Kibana
1. Убедитесь, что используется правильная структура логирования для версии 9.1.1
2. Проверьте, что в `kibana.yml` используется `logging.root.level` вместо `logging.level`
3. Убедитесь, что все настройки соответствуют документации Kibana 9.1.1

### Проблемы с устаревшими настройками Kibana
1. В Kibana 9.1.1 настройка `xpack.security.enabled` больше не поддерживается
2. Настройка `kibana.defaultAppId` также не поддерживается в версии 9.1.1
3. Удалите все устаревшие настройки из `kibana.yml`
4. Используйте максимально минимальную конфигурацию для избежания ошибок валидации

## 📝 Логи

### Просмотр логов
```bash
# Все сервисы
docker-compose logs

# Конкретный сервис
docker-compose logs elasticsearch
docker-compose logs logstash
docker-compose logs kibana
docker-compose logs filebeat
```

### Уровни логирования
- Elasticsearch: INFO
- Logstash: INFO
- Kibana: INFO
- Filebeat: INFO

## 🔄 Обновление

При обновлении версий ELK Stack:
1. Сделайте бэкап данных Elasticsearch
2. Обновите версии в docker-compose.yml
3. Проверьте совместимость конфигураций
4. Протестируйте на тестовой среде

## 📚 Дополнительные ресурсы

- [Elasticsearch 9.1.1 Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/9.1/index.html)
- [Logstash 9.1.1 Documentation](https://www.elastic.co/guide/en/logstash/9.1/index.html)
- [Kibana 9.1.1 Documentation](https://www.elastic.co/guide/en/kibana/9.1/index.html)
- [Filebeat 9.1.1 Documentation](https://www.elastic.co/guide/en/beats/filebeat/9.1/index.html)
