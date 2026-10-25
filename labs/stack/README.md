# Лабораторный стенд: Docker Compose → PostgreSQL → Redis → Celery

**Модули курса:** 07–09 (Docker/Compose), 19–21 (PostgreSQL, Redis/Celery, идемпотентность). **Цель:** развернуть отдельно от рабочих проектов три зависимых сервиса, предъявить наблюдения о готовности, выполнить SQL-инвариант и получить результат асинхронной задачи. Стенд целиком синтетический.

## Модель и границы

```
client --task_id--> redis:6379/0 <-- worker: academy.square(7)
       <-- result 49 via redis:6379/1

PostgreSQL: academy.demo_events (две фиктивные записи)
```

- `db` — PostgreSQL `17-alpine`, healthcheck `pg_isready`, **данные хранятся в отдельном именованном volume**.
- `redis` — `7-alpine`, healthcheck `redis-cli ping`, persistence намеренно выключена: **это стенд для изучения эфемерности**, не шаблон production.
- `worker` — Celery `5.5.3` (Redis broker/backend) в контейнере с непривилегированным UID 65532; задача `square` является чистой функцией, что позволяет безопасно повторять доставку.
- `client` — одноразовый процесс, отправляющий число 7 и ожидающий ответ 49 не более 40 секунд.
- Контейнеры подключены **только к внутренней сети Compose**, порты **не публикуются на Windows/хосте**. Image build потребует скачивания базовых образов и PyPI-пакетов.
- Пароль в compose.yaml фиктивный (`academy_local_example_only`). **Никогда не используйте в production**; не смешивайте стенд с реальными данными.

## Предусловия и safety gate

Работайте в отдельной копии `devops-academy` под Ubuntu/WSL2 с Docker Desktop. Перед созданием контейнеров убедитесь, что Docker context указывает на Ваш локальный Docker Desktop, а не на удалённый сервер. Используем **только** каталог `labs/stack`, project name `academy-synthetic-lab`, сеть `private` и volume `academy_pgdata`. Никакого `docker system prune`, `down -v`, SQL `DROP`, `docker volume rm` без отдельного разрешения. Для проверки доступности Docker команда чтения: `docker info --format '{{.Name}}'` (запускайте её только если Docker работает).

## Пошаговое выполнение (каждый шаг — одна команда, ожидайте результат)

1. **Прогноз.** Назовите предполагаемые роли `db`, `redis`, `worker`, `client`; сформулируйте два независимых признака исправности. Объясните, почему `pg_isready` ещё не доказывает наличия таблицы.
2. **Проверка конфигурации:** `docker compose -f labs/stack/compose.yaml config --quiet`. Успех — код `0`, пустой stdout. Эта команда не создаёт контейнеров. При ошибке проверьте `services`/`volumes`, не меняйте рабочие compose-файлы.
3. **Создание изолированного окружения** (возможно только после Вашего решения запустить стенд): `docker compose -f labs/stack/compose.yaml up -d --build db redis worker`. Область воздействия — только перечисленные учебные ресурсы; Docker скачивает пакеты. Признак старта — отсутствие ненулевого кода, но **это ещё не доказательство функционирования**.
4. **Состояния контейнеров:** `docker compose -f labs/stack/compose.yaml ps`. Проверьте `healthy` для `db`/`redis`; если worker завершился — изучите логи без изменения данных.
5. **SQL-инвариант:** `docker compose -f labs/stack/compose.yaml exec -T db psql -U academy -d academy -tAc 'SELECT count(*) FROM demo_events;'`. Ожидаем **2**. `pg_isready` подтверждает готовность принимать соединения, SQL — наличие и доступность конкретной таблицы.
6. **Асинхронное выполнение:** `docker compose -f labs/stack/compose.yaml run --rm client`. Ожидаем `actual=49; expected=49` и `PASS`. По `task_id` можно проследить отдельный запрос в логах; worker выполняет задачу, а клиент получает результат через backend.
7. **Повторяемость:** повторите шаг 6 и сравните `task_id` и результат. `task_id` меняется, результат чистой функции остаётся 49.
8. **Неудаляющее завершение:** `docker compose -f labs/stack/compose.yaml down`. Контейнеры и сеть убираются, **именованный volume PostgreSQL сохраняется**.

**Откат и данные:** `down` оставляет учебный volume. Если впоследствии понадобится полностью удалить учебные данные, сначала запишите список ресурсов, подтвердите project name и получите явное разрешение для `down --volumes` (это удалит только *volume данного Compose-проекта*, но операция всё равно необратима для его содержимого). Никогда не применяйте это к реальным окружениям.

## Диагностические сценарии

| Симптом | Гипотеза | Безопасная проверка | Что она доказывает |
|---|---|---|---|
| `db` не healthy | init/connection не готов | `docker compose -f labs/stack/compose.yaml logs --tail=50 db` | Сообщения запуска/отказа, не SQL-инвариант |
| `run client` завершился timeout | worker не обрабатывает | `docker compose -f labs/stack/compose.yaml logs --tail=60 worker` | Было ли выполнение/ошибка |
| Celery вернул 49 | задача выполнена | сравнить task_id и результат | Путь брокер→worker→backend сработал для одного задания |
| После `down` данные сохранились | named volume | снова проверить count после повторного up | Сохранность двух синтетических записей; не гарантия backup |
| Повторное создание db не дополнило seed | init скрипты только при пустом volume | проверить count и состояние volume | Entry point не выполняет init.sql заново на уже инициализированных данных |

## Новая самостоятельная задача L3

Смоделируйте мысленно задержку исполнения задачи при здоровом Redis и PostgreSQL. Самостоятельно выберите **не менее двух независимых наблюдений**, локализуйте участок пути `client → broker → worker → result backend`, укажите ограничения каждого вывода и подтвердите реальным stdout/stderr **на отдельном учебном стенде**. Отказы и изменения стенда проводите только после согласования безопасного плана восстановления.

**L3 не присваивается автоматически по зелёному smoke-тесту:** требуется Ваше самостоятельное объяснение, новая задача, проверка и план восстановления.

Источники: [Compose depends_on/healthcheck](https://docs.docker.com/reference/compose-file/services/), [PostgreSQL initialization](https://docs.docker.com/guides/postgresql/), [Celery tasks/acknowledgement](https://docs.celeryq.dev/en/stable/userguide/tasks.html).
