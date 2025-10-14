
```markdown
# STRIDE — Threats mapping (для ключевых потоков/элементов)
Для каждой строки указана: Поток/Элемент → Угроза (STRIDE) → Риск (ид) → Контроль → Ссылка на NFR → Проверка / Артефакт

> Обязательно: набор угроз покрывает ключевой контур проекта (>=12 угроз).

| № | Поток / Элемент | Угроза (STRIDE) | Риск (ID) | Контроль (меры) | Ссылка на NFR | Проверка / Артефакт |
|---:|-----------------|------------------|----------|------------------|---------------|---------------------|
| 1 | F1 GET /wishes | I: Информационное раскрытие — неконтролируемый возврат данных (например, internal fields) | R3 | Явная схема ответа (Pydantic `WishResponse`), фильтрация полей, минимизация полей в ответе | NFR-10, NFR-04 | Unit/e2e тесты на модели ответа; contract tests |
| 2 | F2 GET /wishes/search | S: Spoofing — подмена запроса (например, подмена заголовка X-User без проверки) | R3 | Аутентификация/авторизация (JWT) или API keys для защищённых действий | NFR-06 | e2e + тесты авторизации |
| 3 | F3 POST /wishes | T: Tampering — инъекция/манипуляция содержимым (JS/HTML в title/notes) | R4 | Валидация входа (pydantic), очистка/escape полей при рендере; Content Security при фронте | NFR-10 | Unit tests на валидацию; SAST |
| 4 | F4 PUT /wishes/{id} | R: Repudiation — пользователь отрицает операцию (нет логов изменений) | R6 | Аудит лог: записывать who/when/what для изменений; request id | NFR-04, NFR-10 | Логи в ELK; интеграционные тесты логирования |
| 5 | F5 DELETE /wishes/{id} | D: Denial of Service — массовые удаления/спам запросов | R5 | Rate limiting на уровне GW/middleware; soft-delete + ретрансляция | NFR-08, NFR-03 | K6 нагрузочные тесты; метрики 5xx/пиков |
| 6 | GW (API Gateway) | S: Spoofing / E:Privilege Escalation через незакрытые маршруты | R3,R10 | Проверка маршрутов, WAF, население CORS, auth middleware | NFR-06, NFR-08 | Автотесты маршрутов; ZAP baseline |
| 7 | SVC (FastAPI) internal | E: Elevation of Privilege — неправильно настроенные роли/эндпоинты | R10 | RBAC/ACL, минимальные права, проверка входных параметров | NFR-06 | e2e ролевая проверка |
| 8 | DB (F7) | T: Tampering — несанкционированное изменение/удаление данных | R2 | Персистентность в защищённом DB, бэкапы, IAM, RBAC | NFR-07, NFR-05 | Backup restore test; DB audit |
| 9 | DB (F7) | I: Информация — утечка данных из бэкапов/логов | R9 | Шифрование at-rest/in-transit; ограничение доступа к бэкапам | NFR-07 | Проверка шифрования, аудиты доступа |
|10 | MON (F8) | I: Leakage — логирование секретов (например, link с токеном) | R6 | Маскирование секретов в логах; structured logging | NFR-04, NFR-10 | Log scan (regex) в CI; прогоны SAST |
|11 | In-memory `wishes_db` (implementation) | D: DoS / race — конкурентные операции приводят к inconsistent state | R8 | Перейти на DB/atomic операции; синхронизация (locks) или использовать thread/process safe storage | NFR-09, NFR-03 | Load tests; code review |
|12 | CI/CD pipeline (сканеры) | T/I: Vulnerability found in deps -> выполнение контейнера с уязвимым образов | R7 | Интеграция Snyk/Trivy, policy-as-code, auto-fix PRs | NFR-05 | CI: Snyk/Trivy report включён; policy check |
|13 | Error responses (any endpoint) | I: Detailed error messages раскрывают внутренности (stacktrace) | R6 | Unified error handler (RFC7807 style), убрать stacktrace в проде | NFR-04, NFR-10 | Contract tests; manual review |
|14 | File/Link field (`link`) | I/T: Malicious links (drive-by download, XSS) | R4 | URL validation, мета-проверка (rel="noopener", target), content sanitization | NFR-10 | Unit tests url validation |

**Примечание по приоритетам:**
- Контроли, помеченные как срочные: NFR-06 (аутентификация), NFR-08 (rate limiting), NFR-07 (бэкапы).
- Быстрые выигрыши (quick wins): unified error handler; pydantic strict validation; добавить rate limit middleware.
