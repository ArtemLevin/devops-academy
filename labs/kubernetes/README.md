# Лабораторная: Kubernetes Pod → Deployment → Service → probes

**Уроки:** 43–45. **Цель:** отличить готовность к приёму трафика от признаков неисправности, требующих рестарта, и проследить соответствие селекторов Service и меток Pod.

Схема: **namespace `academy-synthetic`**, Deployment `academy-web` (один `nginx:1.27-alpine`), ClusterIP Service `academy-web`, readiness/liveness HTTP GET `/`, request 20m CPU/16Mi RAM, limit 200m CPU/64Mi RAM. Данные и учётные записи учащихся не используются.

## Безопасность

Сначала убедитесь, что `kubectl config current-context` указывает на **локальный учебный kind-кластер**. Любая команда `apply` меняет Kubernetes-состояние. Нельзя применять YAML к рабочему cluster/context. Создание kind-кластера расходует локальные ресурсы. **Не выполняйте `kind delete cluster` или `kubectl delete namespace` без отдельного разрешения**. Манифесты содержат фиксированное учебное пространство имён, поэтому можно точно определить область воздействия.

## Ход работы по одному действию

1. По тексту `deployment.yaml` предскажите, какие три объекта будут созданы, а какие — отсутствуют до `apply`.
2. Прочитайте конфигурацию: `cat labs/kubernetes/deployment.yaml` (только чтение).
3. Сверьте, что `Service.spec.selector.app` совпадает с `Deployment.spec.template.metadata.labels.app`.
4. **После подтверждения изолированного контекста и согласования изменения:** `kubectl apply -f labs/kubernetes/namespace.yaml`.
5. Затем: `kubectl apply -f labs/kubernetes/deployment.yaml` и отдельно `kubectl apply -f labs/kubernetes/service.yaml`.
6. Наблюдение: `kubectl -n academy-synthetic get deployment,pods,svc`.
7. Диагностика: `kubectl -n academy-synthetic describe pod <POD_NAME>` — для уже наблюдённого имени Pod. Проверьте Events, Ready и Restart Count.
8. Отдельная проверка HTTP через `kubectl -n academy-synthetic port-forward service/academy-web 8080:80` с локального компьютера возможна только после подтверждения корректного контекста; используйте второй терминал для curl `http://127.0.0.1:8080/`.

**Различайте:** readiness failure исключает Pod из endpoint-ов Service, а liveness failure может привести к перезапуску контейнера. `kubectl apply` success не равен Ready. Периодическая проверка `GET /` подходит лишь этому учебному nginx и не доказывает исправность внешних зависимостей.

## Проверки и ограничения CI

- `python -m unittest discover -s labs/tests -v` выполняет **только структурные offline-инварианты** манифестов, не Kubernetes schema validation.
- `kubectl apply --dry-run=client -f labs/kubernetes/` может потребовать настроенный kubeconfig и доступ к OpenAPI-схеме кластера; отсутствие контекста — ожидаемый блокер. Поэтому в GitHub Actions этот шаг намеренно не выполняется.
- Фактические READY/RESTARTS/Service endpoints следует проверять в локальном kind-кластере и сохранять как evidence отдельно.

## Задание L3

В новом учебном Deployment один Pod работает (`Running`), но Service не передаёт запросы. Без подсказки определите, какие независимые проверки различат ошибку selector, неуспешную readinessProbe и отсутствие EndpointSlice. Не меняйте манифесты до фиксации гипотез, плана изменения и отката.

Документация: [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [Service](https://kubernetes.io/docs/concepts/services-networking/service/), [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
