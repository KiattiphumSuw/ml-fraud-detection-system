# ML Fraud Detection System

## Project Overview

This project builds a machine learning model and serves it via a REST API to detect fraudulent financial transactions. It includes:

- Data exploration and preprocessing
- A classification model for fraud detection
- A RESTful API service to provide fraud predictions
- A database for storing detected frauds
- A Kafka-ready architecture for real-time deployment

---

## Project Structure

The following is a simplified tree overview to give you an idea of the project layout:

```
.
├── notebook
│   ├── EDA_fraud_transaction.ipynb # Exploratory Data Analysis
│   └── Traning_fraud_transaction.ipynb # Model training and evaluation
├── data
│   └──  fraud_mock.csv # Sample transaction dataset
├── weight
│   └── fraud_detection_rf_model.joblib # Trained model weights
├── api
│   ├── controllers
│   │   └── frauds_controller.py
│   ├── dependencies
│   │   └── dependencies.py # dependency injection here
│   ├── routes
│   │   ├── frauds_route.py
│   │   └── swagger_route.py
│   └── services
│       └── frauds_service.py
├── lib
│   ├── common
│   │   ├── constant.py
│   │   └── logger.py
│   ├── config
│   │   ├── secret.py
│   │   └── settings.py
│   ├── models
│   │   ├── api_model.py # dataclass and pydantic class for quality code
│   │   └── transaction_record_model.py
│   └── repositories
│       └── fraud_repository.py # define dependency injection here
├── docker
│   └── Dockerfile
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── config.yaml
├── server.py
├── Makefile
└── README.md
```

### ! Add data before start runing !

- add : `fraud_mock.csv` into folder `data`
- add : `fraud_detection_rf_model.joblib` into folder `weight`

### Set Up the Virtual Environment Before Running the Notebook

For macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows:

```bash
python3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

After activating the environment, open your Jupyter notebook and select the environment named .venv from the kernel list.

---

## EDA Instructions

To explore and analyze the dataset, open:<br> `notebook/EDA_fraud_transaction.ipynb`.
<br>Click **Run All** in Jupyter to execute all cells and view visual insights.

## Train the Model Instructions

To train the fraud detection model and export the weights:<br> `notebook/Traning_fraud_transaction.ipynb`
<br>Run the notebook to train the model and save the output to the `weight/` directory.

## Start the API Service

Add `.env` file with this content:

```
DB_USER=scb
DB_PASSWORD=scb
```

We’ve simplified the launch process. Just run:

```bash
docker compose build
docker compose up -d
```

To stop the service:

```bash
docker compose down
```

Once running, you can access the interactive API docs at the root endpoint: <br>
`http://localhost:8080/`

![picture](picture/Document_Testing_Endpoint.png)

Alternative documentation is available at: <br>
`http://localhost:8080/redoc`
![picture](picture/Alternative_Endpoint_Document.png)

## System Architecture

![picture](picture/Fraudulent_Transaction_Detection_ML_System.png)

### Fraud Detection System Architecture:

A scalable, production-grade real-time fraud detection pipeline designed for cloud-native deployment with observability, security, and maintainability in mind.

---

#### 1. Data Zone – Real-Time Streaming Ingestion

| Component    | Description                                                                                                                                                      |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Producer** | Emits real-time financial transaction logs.                                                                                                                      |
| **Kafka**    | Acts as a distributed streaming platform. Supports multiple consumers including the fraud detection service. Durable, fault-tolerant, and horizontally scalable. |
| **Security** | Uses ACLs (Access Control Lists) to restrict topic access. TLS encryption ensures secure data streaming.                                                         |

---

More Security with
**Data Tagging for Privacy Compliance (e.g., PDPA, GDPR)**:

- Sensitive fields like `src_acc`, `dst_acc`, and `amount` can be **tagged as private** or **classified with metadata** (e.g., `pii:true`, `data_sensitivity:high`).
- This tagging allows downstream consumers (e.g., the fraud model, auditors, or monitoring tools) to:

  - Mask/redact values when exporting data for external use (e.g., audit trails, dashboards).

- **Row-Level Security / Field Masking**
  - This ensures that only authorized roles (e.g., auditors) can view full details.
  - This is essential for complying with **data protection laws** like PDPA (Thailand), GDPR (EU), or CCPA (California).

In short, security isn't just about keeping Kafka up and locked — it's about **context-aware data protection** where **sensitive personal transaction data is clearly tagged, masked, and access-controlled across the system**.

---

#### 2. Staging Zone – Temporary Data Buffer

| Component           | Description                                                                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Azure Cosmos DB** | NoSQL store that buffers transaction data between Kafka and downstream processors. Supports global distribution, low-latency, and JSON-native format. |
| **Use Case**        | Decouples Kafka from the feature engineering pipeline. Serves as a temporary stateful store.                                                          |

---

#### 3. Process Zone – Feature Engineering & Feature Store

| Component                 | Description                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Azure Functions**       | Stateless serverless compute that transforms raw transactions into model features. |
| **Feast (Feature Store)** | Maintains feature consistency across training and inference.                       |

---

#### 4. ML Zone – Model Training and Registry

| Component                                | Description                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **MLflow**                               | Tracks experiments, manages models, and maintains a model registry.                                    |
| **Model Training Job (Azure Functions)** | Periodically retrains fraud models based on new labeled data. Triggers deployment of validated models. |
| **Security**                             | MLflow access restricted via Role-Based Access Control (RBAC). Audit logs ensure traceability.         |

---

#### 5. Model Serving Zone – Inference Pipeline

| Component                | Description                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| **Azure Container Apps** | Hosts containerized FastAPI inference services. Auto-scales based on request volume.                                  |
| **FastAPI**              | Lightweight, async-capable REST API for fraud prediction. Fetches features and runs inference using the latest model. |
| **Load Balancer**        | Distributes requests to multiple FastAPI replicas, enabling high availability.                                        |
| **Cache DB**             | Stores frequent queries to minimize inference latency and reduce redundant compute.                                   |
| **Container Registry**   | Stores container images for model inference. Used in CI/CD pipelines for versioned, reproducible deployments.         |
| **Security**             | mTLS between services, JWT-based auth on public APIs. Secrets managed securely (e.g., Azure Key Vault).               |

---

#### 6. App & Auditor Interface

| Component                 | Description                                                                            |
| ------------------------- | -------------------------------------------------------------------------------------- |
| **Mobile/Web App**        | Users can query fraud predictions. Auditors can view and update flagged cases.         |
| **Case Updates**          | Auditor updates are written back into a database or published to Kafka for state sync. |
| **Latency Consideration** | Responses optimized via caching, asynchronous I/O, and lightweight model serving.      |

---

#### 7. Monitoring Zone – Observability & Alerts

| Component        | Description                                                              |
| ---------------- | ------------------------------------------------------------------------ |
| **Prometheus**   | Collects time-series metrics from APIs, models, and infrastructure.      |
| **Grafana**      | Visualizes key metrics for ML, infra, and fraud performance.             |
| **Alertmanager** | Triggers alerts via Slack, email, or other channels based on thresholds. |

---

### Key Monitoring Categories

#### 1. ML Model Performance

- **Inference latency (p95)**: Detects performance bottlenecks.
- **Model confidence distribution**: Flags unusual prediction behavior.
- **Drift indicators**: Sudden drop in precision or recall.
- **Alert**: Model recall < 85% → Notify ML team.

#### 2. Infrastructure & Runtime

- **API latency & error rate**: Ensures real-time responsiveness.
- **CPU & memory usage**: Detects resource saturation.
- **Kafka consumer lag**: Indicates stream processing delay.
- **Alert**: `/predict` latency > 1s (p95) for 5 min → Alert backend.

#### 3. Business Metrics

- **Fraud Catch Rate** = TP / (TP + FN)
- **Flagged transactions per hour**: Monitor volume and fraud trends.
- **Auditor activity rate**: Measures investigation throughput.
- **Alert**: Fraud Catch Rate < 80% → Trigger investigation.

#### Summary

This monitoring setup focuses on high-impact indicators:

- Keeps the model accurate and responsive.
- Maintains system reliability and low latency.
- Ensures fraud detection remains effective in real-time operations.

#### 8. Developer Zone – CI/CD & Validation

| Component          | Description                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------- |
| **GitHub Actions** | Automates linting, testing, building Docker images, and deploying updated services or models. |
| **Pydantic**       | Strict input validation schema to ensure runtime safety and minimize memory usage errors.     |
| **Security**       | Secrets passed via GitHub Encrypted Secrets. CI actions enforce branch protection rules.      |

---

#### Summary Table

| Area                 | Scaling                             | Fault Tolerance          | Security                  |
| -------------------- | ----------------------------------- | ------------------------ | ------------------------- |
| Kafka + Cosmos DB    | Partitioned consumers, async writes | Replayable, distributed  | Topic ACLs, TLS           |
| FastAPI + Azure Apps | Horizontal auto-scaling             | Load-balanced, resilient | mTLS, OAuth2              |
| MLflow + Registry    | Versioned, reproducible             | Model backup + rollback  | RBAC + Audit logs         |
| Prometheus + Grafana | Sharded storage                     | Alert failover           | Read-only viewer accounts |
| CI/CD                | Parallel workflows                  | Rollback on fail         | Encrypted secrets         |

---

#### Key Considerations

- **Latency**: Real-time prediction enabled via fast APIs, caching, and efficient feature lookup.
- **Memory Usage**: Serverless functions and container-based services run isolated, freeing memory after execution.
- **Scalability**: Kafka, Cosmos, and containerized inference ensure independent horizontal scaling.
- **Security**: End-to-end encryption, RBAC, secure registries, and strong audit trail policies.
- **Deployment-Readiness**: CI/CD pipelines ensure reliable, versioned releases with zero-downtime updates.

### Business Recommendations

- Monitor accounts with multiple fraud attempts
- Minimize false negatives to avoid missed frauds
- Assign a fraud risk score to each transaction
- Use predictions to flag accounts for proactive investigation
- Fix upstream issues: many transactions show logical inconsistencies (e.g., incorrect balances)
