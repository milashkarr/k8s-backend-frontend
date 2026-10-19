# Kubernetes Backend-Frontend Demo

Backend-frontend приложение в Kubernetes (Minikube). Backend реплицирован (3 реплики)
и доступен только внутри кластера. Frontend доступен снаружи через Ingress.

## Компоненты

| Компонент | Тип | Доступ |
|-----------|-----|--------|
| `backend-deployment` | Deployment, 3 реплики | — |
| `backend-service` | ClusterIP | только внутри кластера |
| `frontend-deployment` | Deployment, 2 реплики | — |
| `frontend-service` | ClusterIP | внутри кластера (через Ingress) |
| `frontend-ingress` | Ingress (nginx, без host) | снаружи |

## Структура

```
backend/      — Flask-приложение, Dockerfile, requirements.txt
frontend/     — Flask-приложение, Dockerfile, requirements.txt
k8s/          — deployment/service/ingress манифесты
```

## Требования

- Minikube
- kubectl
- Docker Desktop (запущен)

## Запуск

```bash
minikube start --driver=docker
minikube addons enable ingress
kubectl get pods -n ingress-nginx          # дождаться Running

minikube image build -t backend-app:1.0.0 ./backend
minikube image build -t frontend-app:1.0.0 ./frontend

kubectl apply -f k8s/

# ingress-контроллер в LoadBalancer (для minikube tunnel)
kubectl patch svc ingress-nginx-controller -n ingress-nginx \
  -p '{"spec":{"type":"LoadBalancer"}}'

# в ОТДЕЛЬНОМ терминале, не закрывать:
minikube tunnel
```

> На Windows с драйвером Docker `minikube tunnel` пробрасывает LoadBalancer
> на `127.0.0.1`, поэтому внешний адрес — `http://127.0.0.1/`.

## Тестирование

```powershell
# Frontend + Backend (снаружи)
curl.exe http://127.0.0.1/

# Репликация backend — hostname меняется (3 реплики)
1..6 | ForEach-Object { (Invoke-RestMethod http://127.0.0.1/).backend_response.hostname }

# Backend недоступен снаружи
kubectl get svc backend-service     # TYPE=ClusterIP, EXTERNAL-IP=<none>

# Backend доступен изнутри кластера
kubectl run curl-test --rm -it --image=curlimages/curl --restart=Never -- curl -s http://backend-service:8080/
```

Ожидаемый ответ:
```json
{
  "frontend": "Hello from FRONTEND! ^-^",
  "backend_response": {
    "message": "Hello from BACKEND! :-)",
    "hostname": "backend-deployment-9b46d569d-r5nq5"
  }
}
```

## Self-healing и масштабирование

```bash
kubectl delete pod <backend-pod-name>          # Deployment пересоздаст
kubectl scale deployment backend-deployment --replicas=5
kubectl get pods
```

## Очистка

```bash
kubectl delete -f k8s/
minikube addons disable ingress
minikube stop
```
