# 🎮 SRE Runner

SRE Runner is a Python/Pygame endless-runner game developed as the SRE Academy final project to demonstrate containerization, Kubernetes deployment, application observability, monitoring, visualization, and alerting.

The application is containerized with Docker and deployed to a local Kubernetes cluster using Minikube. Application-specific metrics are exposed in Prometheus format and scraped by Prometheus. Grafana provides visualization of those metrics, while Alertmanager handles application availability alerts.

---

## 🏗️ Architecture

```text
                      MINIKUBE

┌──────────────────────────────────────────────────┐
│                                                  │
│  default namespace                               │
│                                                  │
│  ┌─────────────────────────┐                     │
│  │     SRE Runner Pod      │                     │
│  │                         │                     │
│  │  Python + Pygame        │                     │
│  │  :9090/metrics          │                     │
│  └────────────┬────────────┘                     │
│               │                                  │
│               ▼                                  │
│       sre-runner Service                         │
│               │                                  │
├───────────────┼──────────────────────────────────┤
│               │                                  │
│  monitoring namespace                            │
│               │                                  │
│               ▼                                  │
│       ┌──────────────┐                            │
│       │  Prometheus  │                            │
│       │    :9090     │                            │
│       └──────┬───────┘                            │
│              │                                    │
│         ┌────┴─────┐                              │
│         ▼          ▼                              │
│   ┌──────────┐  ┌──────────────┐                  │
│   │ Grafana  │  │ Alertmanager │                  │
│   │  :3000   │  │    :9093     │                  │
│   └──────────┘  └──────────────┘                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Monitoring flow

```text
SRE Runner
    │
    │ /metrics
    ▼
Prometheus
    │
    ├──────────────► Grafana
    │                 dashboards
    │
    └──────────────► Alertmanager
                      alerts
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| pygame-ce | Game engine |
| Docker | Application containerization |
| Kubernetes | Container orchestration |
| Minikube | Local Kubernetes cluster |
| Prometheus | Metrics collection and monitoring |
| Grafana | Metrics visualization |
| Alertmanager | Alert management |
| Git | Version control |
| GitHub | Source repository |

---

## 🎮 Application

SRE Runner is an endless-runner game featuring:

- Ground obstacles
- Flying obstacles
- Jump mechanics
- Increasing game speed
- Score tracking
- High-score tracking
- Collision detection
- Prometheus application metrics

Ground obstacles are available from the beginning of the game. Flying obstacles are introduced as the score increases, requiring the player to react differently to each obstacle type.

---

## 📂 Repository Structure

```text
sre-runner/
├── game/
│   ├── main.py
│   └── metrics.py
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   │
│   └── monitoring/
│       ├── alertmanager.yaml
│       ├── grafana.yaml
│       ├── prometheus-config.yaml
│       ├── prometheus-deployment.yaml
│       ├── prometheus-rules.yaml
│       └── prometheus-service.yaml
│
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE.md
└── README.md
```

---

# 🚀 Running the Project

## Prerequisites

The project requires:

- Docker
- Minikube
- kubectl
- Python 3
- Git

For local game development, create a Python virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Run SRE Runner Locally

```bash
python game/main.py
```

Controls:

```text
SPACE    Jump
R        Restart after Game Over
```

---

# 🐳 Containerization

The application is packaged using Docker.

Build the image directly into Minikube:

```bash
minikube image build -t sre-runner:v2 .
```

Verify the image:

```bash
minikube image ls | grep sre-runner
```

---

# ☸️ Kubernetes Deployment

Start Minikube:

```bash
minikube start
```

Deploy SRE Runner:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verify:

```bash
kubectl get pods
kubectl get services
```

The SRE Runner application runs in the `default` namespace.

Its metrics endpoint is exposed internally through:

```text
http://sre-runner:9090/metrics
```

From another namespace, the fully qualified Kubernetes DNS name is:

```text
http://sre-runner.default.svc.cluster.local:9090/metrics
```

---

# 📊 Application Metrics

SRE Runner uses `prometheus-client` to expose application-specific metrics.

## Custom Metrics

### Games Started

```promql
sre_runner_games_started_total
```

Total number of game sessions started.

### Game Active

```promql
sre_runner_game_active
```

Values:

```text
1 = game active
0 = game over
```

### Current Score

```promql
sre_runner_current_score
```

### Current Speed

```promql
sre_runner_current_speed
```

### Obstacles Avoided

```promql
sre_runner_obstacles_avoided_total{type="ground"}
sre_runner_obstacles_avoided_total{type="flying"}
```

Both types:

```promql
sre_runner_obstacles_avoided_total
```

### Collisions

```promql
sre_runner_collisions_total{type="ground"}
sre_runner_collisions_total{type="flying"}
```

Both types:

```promql
sre_runner_collisions_total
```

---

# 🔥 Prometheus

Prometheus runs in the Kubernetes `monitoring` namespace.

Deploy the monitoring configuration:

```bash
kubectl apply -f k8s/monitoring/
```

Verify:

```bash
kubectl get pods -n monitoring
```

Access Prometheus locally:

```bash
kubectl port-forward -n monitoring service/prometheus-service 9090:9090
```

Then open:

```text
http://localhost:9090
```

Prometheus scrapes:

```text
sre-runner.default.svc.cluster.local:9090/metrics
```

## Check Application Availability

Prometheus automatically provides the `up` metric:

```promql
up{job="sre-runner"}
```

Values:

```text
1 = scrape successful
0 = scrape unsuccessful
```

---

# 📈 Grafana

Grafana is deployed in the `monitoring` namespace.

Access Grafana:

```bash
kubectl port-forward -n monitoring service/grafana-service 3000:3000
```

Open:

```text
http://localhost:3000
```

Default local-lab credentials:

```text
Username: admin
Password: admin
```

The Prometheus data source is automatically provisioned through a Kubernetes ConfigMap.

Internal Prometheus URL:

```text
http://prometheus-service.monitoring.svc.cluster.local:9090
```

## Dashboards

Two dashboards are provisioned:

### Example Dashboard

Includes the CPU Usage example from the SRE Academy exercise.

### SRE Runner Dashboard

Provides application-specific visualization for:

- Game Active
- Current Score
- Current Speed
- Games Started
- Ground and flying collisions
- Ground and flying obstacles avoided

---

# 🚨 Alertmanager

Alertmanager runs in the `monitoring` namespace and receives alerts generated by Prometheus.

Access Alertmanager:

```bash
kubectl port-forward -n monitoring service/alertmanager-service 9093:9093
```

Then open:

```text
http://localhost:9093
```

## SRE Runner Availability Alert

Prometheus evaluates:

```promql
up{job="sre-runner"} == 0
```

The alert must remain active for:

```text
1 minute
```

before firing.

Alert:

```text
SRERunnerDown
```

Severity:

```text
critical
```

Description:

```text
Prometheus has been unable to scrape SRE Runner for more than 1 minute.
```

---

# 🧪 Incident Simulation

Application failure was tested by scaling SRE Runner to zero replicas:

```bash
kubectl scale deployment sre-runner --replicas=0
```

This produces the following sequence:

```text
SRE Runner unavailable
        ↓
Prometheus scrape fails
        ↓
up{job="sre-runner"} = 0
        ↓
SRERunnerDown PENDING
        ↓
1 minute
        ↓
SRERunnerDown FIRING
        ↓
Alertmanager receives incident
```

Restore the application:

```bash
kubectl scale deployment sre-runner --replicas=1
```

After recovery:

```text
SRE Runner running
        ↓
Prometheus scrape succeeds
        ↓
up{job="sre-runner"} = 1
        ↓
Alert resolves
```

Check SRE Runner:

```bash
kubectl get pods
```

---

# 🔍 Alertmanager API Verification

Active Alertmanager alerts can also be verified through its API:

```bash
curl -s http://localhost:9093/api/v2/alerts
```

If `jq` is installed:

```bash
curl -s http://localhost:9093/api/v2/alerts | jq
```

During the incident test, this displays the active `SRERunnerDown` alert and its `critical` severity.

---

# 🛑 Starting and Stopping the Environment

The complete Minikube environment can be stopped without deleting the project:

```bash
minikube stop
```

Restart:

```bash
minikube start
```

Verify:

```bash
kubectl get pods
kubectl get pods -n monitoring
```

Do not use:

```bash
minikube delete
```

unless the intention is to destroy the local Kubernetes cluster.

---

# 📸 Project Evidence

1. SRE Runner running locally
2. Kubernetes SRE Runner pod running
3. Prometheus, Grafana, and Alertmanager pods running
4. Prometheus SRE Runner target showing `UP`
5. Prometheus queries displaying `sre_runner_*` metrics
6. SRE Runner Grafana Dashboard
7. `SRERunnerDown` alert in `FIRING` state
8. Alert received by Alertmanager
9. Successful recovery to `up = 1`

Screenshots can be stored under:

```text
docs/images/
```

Example:

```text
docs/
└── images/
    ├── sre-runner-game.png
    ├── kubernetes-pods.png
    ├── prometheus-target.png
    ├── prometheus-metrics.png
    ├── grafana-dashboard.png
    ├── prometheus-alert.png
    └── alertmanager-alert.png
```

---

# 🔧 Useful Commands

Check SRE Runner:

```bash
kubectl get pods
kubectl get services
```

Check monitoring:

```bash
kubectl get pods -n monitoring
kubectl get services -n monitoring
```

Check SRE Runner logs:

```bash
kubectl logs -l app=sre-runner
```

Check Prometheus logs:

```bash
kubectl logs -l app=prometheus -n monitoring
```

Check Grafana logs:

```bash
kubectl logs -l app=grafana -n monitoring
```

Check Alertmanager logs:

```bash
kubectl logs -l app=alertmanager -n monitoring
```

---

# 💰 Cost

This project is designed to run at **$0 infrastructure cost**.

Minikube is used instead of managed Kubernetes services such as AKS, GKE, or EKS, allowing the entire Kubernetes and observability stack to run locally.

---

# 🔮 Future Improvements

Potential improvements include:

- Persistent Prometheus storage
- Persistent Grafana storage
- Slack, Microsoft Teams, or email Alertmanager notifications
- Kubernetes health probes
- Kubernetes resource requests and limits
- Helm packaging
- Terraform-based infrastructure
- Argo CD / GitOps deployment
- CI/CD with GitHub Actions
- Additional alerts based on application behavior
- cAdvisor container metrics
- Web-based game client for interactive Kubernetes gameplay

---

# 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

# 📄 License

See [LICENSE.md](LICENSE.md) for license information.
