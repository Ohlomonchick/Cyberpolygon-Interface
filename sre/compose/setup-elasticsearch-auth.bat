@echo off
echo 🚀 Полная настройка ELK Stack с аутентификацией для Cyberpolygon
echo.

echo 📋 Этот скрипт выполнит следующие шаги:
echo    1. Генерация SSL сертификатов
echo    2. Запуск ELK Stack
echo    3. Настройка пользователей и ролей
echo.

set /p continue="Продолжить? (y/n): "
if /i not "%continue%"=="y" (
    echo Отменено пользователем
    pause
    exit /b 0
)

echo.
echo 🔐 Шаг 1: Генерация сертификатов...
call init-certs.bat
if %errorlevel% neq 0 (
    echo ❌ Ошибка при генерации сертификатов
    pause
    exit /b 1
)

echo.
echo 🚀 Шаг 2: Запуск ELK Stack...
call run_elk.bat
if %errorlevel% neq 0 (
    echo ❌ Ошибка при запуске ELK Stack
    pause
    exit /b 1
)

echo.
echo ⏳ Ожидание готовности Elasticsearch...
timeout /t 30 > nul

echo.
echo 👥 Шаг 3: Настройка пользователей и ролей...
call setup-users.bat
if %errorlevel% neq 0 (
    echo ❌ Ошибка при настройке пользователей
    pause
    exit /b 1
)

echo.
echo 🎉 Настройка завершена успешно!
echo.
echo 📋 Созданные пользователи:
echo    👑 admin / admin123 (Superuser - полный доступ)
echo    📊 kibana_user / kibana123 (Kibana user - может создавать дашборды)
echo    👁️  readonly / readonly123 (Read-only user - только просмотр данных)
echo.
echo 🌐 Доступ:
echo    Elasticsearch: https://localhost:9200 (elastic/elastic)
echo    Kibana: https://localhost:5601 (используйте любого из созданных пользователей)
echo.
echo ⚠️  Это учетные данные для разработки. Измените их для продакшена!
echo.
pause
