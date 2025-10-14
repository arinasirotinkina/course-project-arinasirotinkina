# RISKS — Реестр рисков (L×I) и план обработки

> Оценки: L (Likelihood) 1..5, I (Impact) 1..5. Risk — произведение.
>
| RiskID | Описание | Связь (F / NFR) | L | I | Risk | Стратегия | Владелец | Срок | Критерий закрытия |
|--------|----------|------------------|---:|---:|-----:|----------|----------|------|-------------------|
| R1 | Спам POST (массовое создание) | F3, NFR-08 | 3 | 3 | 9 | Снизить | @arinasirotinkina | 2025-10-21 | Rate limit включён; k6 smoke |
| R2 | Потеря данных (in-memory) | F7, NFR-07 | 4 | 5 | 20 | Снизить | @arinasirotinkina | 2025-10-20 | Миграция на Postgres + ежедневный бэкап |
| R3 | Нет аутентификации на write | F1..F5, NFR-06 | 3 | 5 | 15 | Снизить | @arinasirotinkina | 2025-10-18 | JWT/API key на write; e2e тесты |
| R4 | XSS / вредоносный контент | F3,F4, NFR-10 | 2 | 4 | 8 | Снизить | @arinasirotinkina | 2025-10-22 | Валидация+санитайзинг; unit тесты |
| R5 | DoS / дорогие запросы | F1..F5, NFR-03,NFR-08 | 3 | 4 | 12 | Снизить | @arinasirotinkina | 2025-10-21 | Rate limit + нагрузочные p95/p99 |
| R6 | Утечка внутренних данных в ошибках | F1..F6, NFR-04 | 2 | 3 | 6 | Снизить | @arinasirotinkina | 2025-10-18 | Unified error handler; лог-маскирование |
| R7 | Уязвимости зависимостей | CI, NFR-05 | 3 | 4 | 12 | Снизить | @arinasirotinkina | 2025-10-24 | Snyk/Trivy в CI; план ремедиации |
| R8 | Гонки / неконсистентность (in-memory) | SVC, NFR-09 | 4 | 3 | 12 | Снизить | @arinasirotinkina | 2025-10-20 | Перенос на транзакционную БД; интеграц. тесты |
| R9 | Утечка из бэкапов/логов | DB/Backup, NFR-07 | 3 | 5 | 15 | Снизить | @arinasirotinkina | 2025-10-25 | Шифрование бэкапов; аудит доступа |
| R10 | Неправильные конфигурации в проде | Infra, NFR-03,NFR-06 | 2 | 5 | 10 | Снизить | @arinasirotinkina | 2025-10-18 | Policy-as-code + CI gating |
| R11 | Низкое покрытие тестами | Codebase, NFR-10 | 2 | 4 | 8 | Снизить | @arinasirotinkina | 2025-10-30 | Unit coverage ≥80% в CI |
| R12 | Отсутствие мониторинга/алёртов | MON, NFR-03,NFR-04 | 3 | 4 | 12 | Снизить | @arinasirotinkina | 2025-10-22 | Dashboards и Alertmanager настроены |

## Приоритеты и quick wins
- **Срочно (High risk / high impact):** R2 (in-memory → DB + бэкап), R3 (auth), R9 (backup шифрование).
- **quick wins:** unified error handler (R6), pydantic strict validation (R4), rate limiting middleware (R1,R5).
