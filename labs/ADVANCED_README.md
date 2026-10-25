# Практический трек 2: Docker, PostgreSQL, Celery, GitHub Actions, Kubernetes

Этот комплект расширяет учебные занятия **07–09, 13–15, 19–21 и 43–45**. Он не зависит от рабочих репозиториев и использует синтетические данные.

| Компонент | Инструмент | Проверяемый инвариант | Ограничение |
|---|---|---|---|
| Docker Compose | `config --quiet`, `ps` | конфигурация валидна; db/redis healthy | startup не подтверждает бизнес-функцию |
| PostgreSQL | `psql ... SELECT count(*)` | 2 синтетических события | готовность не равна восстановлению/backup |
| Redis/Celery | `run --rm client` | `academy.square(7) = 49` | не тестирует реальную очередь проекта |
| GitHub Actions | `integration-labs.yml` | offline unit + Docker integration в эфемерном runner | успешность CI только по фактическому run |
| Kubernetes | YAML для namespace/deployment/service | статические guardrails; probe/config | без kind/кластерного эксперимента нет runtime evidence |

## Порядок самостоятельной практики

Сначала [offline-проверки](checks/README.md), затем [Compose-стенд](stack/README.md); [Kubernetes](kubernetes/README.md) изучается позже в рамках недели 15. Все инструкции разделены на короткие команды: выполняйте только один шаг за раз и анализируйте фактический вывод перед продолжением.

Публичная библиотека: [labs-advanced.html](../labs-advanced.html). Базовые упражнения 04–06 остаются в [labs/README.md](README.md).

## Safety

Проверить Docker context и kubectl context; не менять реальные сервисы; не использовать пароли, ключи, рабочие дампы и данные учеников. Работа с Kubernetes возможна только в заведомо локальном кластере. Очистка volumes и namespaces запрещена без согласования даже для синтетической лаборатории.
