# Проверка и интерпретация результатов

1. `python3 -m unittest discover -s labs/tests -v` — offline regression. Должно быть 8 тестов: прежние 5 и новые 3.
2. `python3 labs/checks/check_fixtures.py` — SQLite проверит структуру и количество синтетических SQL-записей; Python AST проверит код Celery; текстовые проверки обнаружат отсутствие базовых guardrail. **Не является проверкой PostgreSQL, Redis, Celery runtime или схемы Kubernetes.**
3. `docker compose -f labs/stack/compose.yaml config --quiet` — проверка модели Compose без контейнеров; требует установленного Docker Compose.
4. GitHub Actions `integration-labs.yml` — при наличии Runner с Docker отдельно проверяет запуск PostgreSQL/Redis/Celery. Его успешность устанавливается только по фактическому run и логам.
5. Kubernetes runtime подтверждается только отдельным безопасным локальным экспериментом (kind), с сохранением `kubectl get`, `describe` и response.

Evidence для L3: до выполнения — гипотеза/прогноз, затем контекст/версия и одна команда, stdout/stderr/exit code, независимое подтверждение, ограничения и безопасный rollback. Встроенные PASS и CI сами по себе означают корректность тестового сценария, не усвоение навыка учеником.
