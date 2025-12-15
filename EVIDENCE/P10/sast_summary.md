P10 — SAST & Secrets: краткий триаж (Semgrep + Gitleaks)

Резюме
- Semgrep (SARIF): файл `EVIDENCE/P10/semgrep.sarif` присутствует, но содержит 0 findings.
- Gitleaks (JSON): файл `EVIDENCE/P10/gitleaks.json` присутствует и содержит пустой массив (0 findings).

Что сделано
- Добавлен workflow `.github/workflows/ci-sast-secrets.yml` для запуска Semgrep и Gitleaks в CI (docker). Триггеры: `push` по релевантным путям и `workflow_dispatch`.
- Добавлен минимальный набор собственных правил Semgrep: `security/semgrep/rules.yml`.
- Добавлен минимальный конфиг Gitleaks: `security/.gitleaks.toml` (allowlist для `EVIDENCE/`).
- Настроено сохранение артефактов в `EVIDENCE/P10` и загрузка их как P10_EVIDENCE в job.
- Проведён локальный запуск Semgrep и Gitleaks: оба отработали и записали отчёты в `EVIDENCE/P10/`.

Детали результатов
- Semgrep SARIF: `jq '[.runs[] | (.results // [])[]] | length' EVIDENCE/P10/semgrep.sarif` → 0
  - SARIF содержит структуру run, но поле `results` пусто — означает, что при указанной конфигурации правил и путях совпадений не обнаружено.
- Gitleaks JSON: `jq 'length' EVIDENCE/P10/gitleaks.json` → 0
  - Отчёт — пустой список, значит в рабочей копии репозитория не найдено секретов по текущим правилам.

Как воспроизвести локально

# Semgrep (Docker)
```bash
mkdir -p EVIDENCE/P10
docker run --rm -v "$PWD":/src returntocorp/semgrep:latest \
  semgrep ci --config p/ci --config /src/security/semgrep/rules.yml \
    --sarif --output /src/EVIDENCE/P10/semgrep.sarif --metrics=off || true
```

# Gitleaks (Docker)
```bash
mkdir -p EVIDENCE/P10
docker run --rm -v "$PWD":/repo zricethezav/gitleaks:latest \
  detect --no-banner --config=/repo/security/.gitleaks.toml \
    --source=/repo --report-format=json \
    --report-path=/repo/EVIDENCE/P10/gitleaks.json || true
```

Краткая классификация P10
- C1. Настройка SAST (Semgrep, SARIF): ★ 1 — Semgrep запускается (workflow + локальный запуск), используется профиль `p/ci`, отчёт в `EVIDENCE/P10/semgrep.sarif`. Дополнительно добавлены простые правила `security/semgrep/rules.yml` (вектор к ★★2).
- C2. Сканирование секретов (Gitleaks): ★ 1 — Gitleaks запускается, используется `security/.gitleaks.toml`, отчёт `EVIDENCE/P10/gitleaks.json` есть (пустой).
- C3. Артефакты и документация: ★★ 2 — добавлен этот summary `EVIDENCE/P10/sast_summary.md` + отчёты в `EVIDENCE/P10/`.
- C4. Триаж и работа с findings: ★ 1 — триаж выполнен: 0 findings Semgrep, 0 Gitleaks; план действий описан ниже.
- C5. Интеграция в CI и гигиена: ★ 1 — workflow минимально безопасен (permissions: contents: read), concurrency и timeout заданы.

если появятся findings
1. Semgrep findings:
   - Сначала классифицировать по severity (HIGH/MEDIUM/LOW).
   - Для HIGH — фиксить в срочном порядке (PR) или создать Issue с указанием срочности.
   - Для ложноположений — скорректировать правило в `security/semgrep/rules.yml` или добавить исключение.
2. Gitleaks findings:
   - Если это ложноположения (например, файлы в `EVIDENCE/` или автогенерация) — добавить путь или regex в `security/.gitleaks.toml` с комментарием.
   - Если найден реальный секрет — ротация, удаление из кода (замена на чтение из env/secret manager), зафиксировать PR и создать Issue по полной очистке истории (если нужно).

Команды для быстрой проверки отчётов (локально)
```bash
jq '[.runs[] | (.results // [])[]] | length' EVIDENCE/P10/semgrep.sarif

jq 'length' EVIDENCE/P10/gitleaks.json
```

---
