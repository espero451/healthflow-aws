# HealthFlow AWS (LocalStack)

Experimental healthcare workflow demo replicating an AWS-style event-driven architecture locally using LocalStack, AWS CDK (TypeScript), Lambda microservices, and React UI.

### Architecture

```
[Patient UI] ---> [API Gateway] ---> [Lambda Commands] ---> [EventBridge]
     |                                       |                    |
     |                                       |                    v
     |                                       |                  [SQS]
     |                                       |                    |
     v                                       v                    v
[Clinician UI] <--- [Query Lambda] <--- [Read Models] <--- [Worker Lambda]
                                             |
                                             v
                                        [DynamoDB]
```

<!-- ### What matches DearHealth

- Event-driven microservices style with API Gateway, Lambda, EventBridge, SQS, DynamoDB.
- Infrastructure as code with AWS CDK and TypeScript.
- CQRS-style projections and event store in DynamoDB.
- Model Definition framework in TypeScript (minimal demo).
- Playwright e2e/API tests.
- React patient + clinician UIs. -->

### Project Structure

```
healthflow-aws/
  docker-compose.yml      # LocalStack container and storage volume
  infra/                  # AWS CDK (TypeScript) stack definition
  services/               # Lambda handlers + shared Python helpers
  frontend/               # React patient + clinician apps (Vite)
  tools/                  # Local dev helpers (API URL, seed users, run fronts)
  model-defs/             # Minimal model definition framework demo
  tests/                  # Playwright e2e/API tests
```

## Prerequisites

- Docker
- Node.js 18+
- Python 3.11+
- LocalStack CLI (`localstack`) and AWS CLI (`awslocal`)
- AWS CDK Local (`cdklocal`)

### Deploy

```bash
./tools/deploy.sh
```

<!-- ### Deploy infra to LocalStack

```bash
cd infra
npm install
LOCALSTACK_ENDPOINT=http://localhost:4566 cdklocal bootstrap
AWS_S3_FORCE_PATH_STYLE=1 LOCALSTACK_ENDPOINT=http://localhost:4566 \
  cdklocal deploy --all --require-approval never
```

Note: when `LOCALSTACK_ENDPOINT` is set, the API Gateway custom authorizer is disabled to avoid LocalStack CloudFormation limitations. Auth is still enforced when deploying to AWS.

**Get API Gateway URL**

```bash
python3 scripts/get_api_url.py
```

**Seed clinician user**

```bash
python3 scripts/seed_clinician.py
```

**Run frontends**

```bash
bash scripts/run_frontends.sh
``` -->

### Run Playwright tests

```bash
export API_BASE_URL=$(python3 scripts/get_api_url.py)
export UI_BASE_URL=http://localhost:5173

cd tests
npm install
npx playwright install
npm run test
```

### Model Definition framework

```bash
cd model-defs
npm install
npm run generate
```

### Notes

- LocalStack emulates AWS services on `http://localhost:4566`.
- The patient account is created on first login; clinician users are seeded via `./tools/seed_clinician.py` script.
- DynamoDB stores raw events plus read-model tables for queries.
