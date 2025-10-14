# RISKS — Реестр рисков (L×I) и план обработки

**Формат:** RiskID | Описание | Связь (Flow / NFR) | L | I | Risk=L×I | Стратегия | Владелец | Срок | Критерий закрытия

> Оценки: L (Likelihood) 1..5, I (Impact) 1..5. Risk — произведение.

| RiskID | Описание | Связь (F / NFR) | L | I | Risk | Стратегия | Владелец | Срок | Критерий закрытия |
|--------|----------|------------------|---:|---:|-----:|----------|---------|------|-------------------|
| R1 | Спам/злоупотребление POST (создание большого числа записей) | F3, NFR-08 | 3 | 3 | 9 | Снизить | @dev-team | 2025-10-21 | Rate limit (GW/middleware) включён; интеграционный тест (k6) |
| R2 | Потеря данных — текущее in-memory `wishes_db` теряет данные при перезапуске | F7, NFR-07 | 4 | 5 | 20 | Снизить/Избежать | @dev-team | 2025-10-20 | Перенести на персистентную БД (Postgres) + ежедневные бэкапы; RPO ≤1ч |
| R3 | Неавторизованный доступ / отсутствие аутентификации (чувствительные операции) | F1..F5, NFR-06 | 3 | 5 | 15 | Снизить | @dev-team | 2025-10-18 | JWT auth реализован; e2e: rejected on protected endpoints |
| R4 | XSS / malicious content в полях (title/notes/link) | F3,F4, NFR-10 | 2 | 4 | 8 | Снизить | @dev | 2025-10-22 | Input validation + escaping; unit tests на валидацию |
| R5 | DoS через массовые запросы / expensive queries | F1..F5, NFR-03,NFR-08 | 3 | 4 | 12 | Снизить | @infra | 2025-10-21 | Rate limiting + circuit breaker; нагрузочные тесты p95/p99 |
| R6 | Разглашение внутренней информации в ошибках/логах | F1..F6, NFR-04 | 2 | 3 | 6 | Снизить | @dev | 2025-10-18 | Unified error handler + log masking; ZAP baseline |
| R7 | Уязвимости зависимостей (libs, containers) | CI, NFR-05 | 3 | 4 | 12 | Снизить/Перенести | @sec | 2025-10-24 | Snyk/Trivy в CI; SLA по исправлению High≤7дн |
| R8 | Состояние гонки / некорректность при параллельных запросах (in-memory) | SVC, NFR-09 | 4 | 3 | 12 | Снизить/Избежать | @dev | 2025-10-20 | Перенос на транзакционную БД / atomic operations; интеграционные тесты |
| R9 | Утечка данных из бэкапов или логов | DB/Backup, NFR-07 | 3 | 5 | 15 | Снизить | @ops | 2025-10-25 | Шифрование бэкапов + доступ через IAM; регулярный аудит |
| R10 | Неправильные конфигурации (debug=true, отсутствие TLS) в проде | Infra, NFR-03,NFR-06 | 2 | 5 | 10 | Снизить/Избежать | @ops | 2025-10-18 | Policy as code; checklist deploy; CI gating |
| R11 | Недостаточное покрытие тестами → регрессии безопасности | Codebase, NFR-10 | 2 | 4 | 8 | Снизить | @qa | 2025-10-30 | Unit coverage >=80%; CI: pytest-cov |
| R12 | Недостаточная мониторинг/алёртинг (неусмотренные деградации) | MON, NFR-03,NFR-04 | 3 | 4 | 12 | Снизить | @ops | 2025-10-22 | Dashboards + Alertmanager; SLA alerts configured |

## Приоритеты и quick wins
- **Срочно (High risk / high impact):** R2 (in-memory → DB + бэкап), R3 (auth), R9 (backup шифрование).
- **Быстрые выигрыши:** unified error handler (R6), pydantic strict validation (R4), rate limiting middleware (R1,R5).

## План обработки (примерный)
1. **Sprint 1 (в течение 1–2 недель):**
   - Включить rate limiting на GW / добавить библиотеку (R1,R5).
   - Реализовать unified error handler, убрать stacktraces (R6).
   - Добавить basic JWT auth (защита write операций) — минимум NFR-06 (R3).
2. **Sprint 2:**
   - Перенос хранилища на персистентную БД (Postgres) + backup config (R2,R9).
   - Внедрить Snyk/Trivy в CI (R7).
3. **Ops / непрерывно:**
   - Настройка метрик / alerting (R12), SLA-мониторинг (NFR-03).
   - Политика исправления (NFR-05).

## Владелец/Ответственность
- `@arinasirotinkina` — реализация фич и исправление уязвимостей в коде.

---

## Примеры критериев закрытия (конкретные артефакты)
- "Rate limit middleware добавлен + тест k6 подтверждает ограничение"
- "JWT auth: все write endpoints возвращают 401 без токена; e2e тесты в CI"
- "Snyk в CI: critical vulnerabilities absent; процесс ремедиации описан"
- "DB backup: ежедневный backup + восстановление в тестовом окружении прошло успешно"
