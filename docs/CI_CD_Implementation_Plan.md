# CI/CD Implementation Plan - PyForge
## Detailed Execution Plan for Pipeline Setup

---

## 4.1 CI/CD Implementation Roadmap

### Sprint 1 (Week 1-2): Core CI Foundation
**Goal**: Running CI pipeline with lint, type-check, unit tests on every PR

| Day | Task | Owner | Deliverable |
|---|---|---|---|
| 1 | Setup GitHub Actions workflow structure | DevOps | `.github/workflows/ci.yml` skeleton |
| 2 | Configure Python linting (ruff) | Backend | `backend/pyproject.toml` ruff config |
| 3 | Configure TypeScript linting (eslint/prettier) | Frontend | `frontend/eslint.config.js`, `.prettierrc` |
| 4 | Configure mypy strict mode | Backend | `backend/pyproject.toml` mypy config |
| 5 | Configure TypeScript strict mode | Frontend | `frontend/tsconfig.json` strict flags |
| 6 | Write backend unit test infrastructure | Backend | `backend/tests/conftest.py`, fixtures |
| 7 | Write frontend test infrastructure | Frontend | `frontend/vitest.config.ts`, test utils |
| 8 | Implement pytest coverage gate (≥80%) | Backend | Coverage config in pyproject.toml |
| 9 | Implement vitest coverage gate (≥80%) | Frontend | Coverage config in vitest.config.ts |
| 10 | Integrate all stages in CI workflow | DevOps | Working `ci.yml` with matrix jobs |
| 11 | Add pre-commit hooks | All | `.pre-commit-config.yaml` |
| 12 | Local CI simulation script | DevOps | `scripts/ci-local.sh` |
| 13 | Test & debug pipeline | All | Green CI on sample PR |
| 14 | Document CI usage in README | DevOps | `docs/CI_USAGE.md` |

**Definition of Done Sprint 1:**
- [ ] PR to staging triggers CI
- [ ] All 6 stages execute (lint → type → test → security → build → e2e)
- [ ] Quality gates block merge on failure
- [ ] Local `./scripts/ci-local.sh` matches CI results
- [ ] Pre-commit catches issues before push

---

### Sprint 2 (Week 3-4): Security & Container Scanning
**Goal**: Complete security scanning + Docker builds in pipeline

| Day | Task | Owner | Deliverable |
|---|---|---|---|
| 15 | Integrate Bandit SAST | Backend | Bandit step in CI, baseline exclusions |
| 16 | Integrate pip-audit | Backend | Dependency scanning step |
| 17 | Integrate npm audit | Frontend | Dependency scanning step |
| 18 | Integrate gitleaks | DevOps | Secret detection with custom rules |
| 19 | Create multi-stage Dockerfiles | All | `Dockerfile` per service (builder→runner) |
| 20 | Configure docker buildx bake | DevOps | `docker-bake.hcl` for multi-image builds |
| 21 | Integrate Trivy container scanning | DevOps | Trivy step per image, SARIF upload |
| 22 | Configure SBOM generation | DevOps | SPDX JSON per image |
| 23 | Add hadolint for Dockerfiles | DevOps | Lint stage extended |
| 24 | Add yamllint/markdownlint | DevOps | Config files linting |
| 25 | Security gate thresholds tuning | Security | Documented exception process |
| 26 | Test with vulnerable dependencies | All | Verify gates catch known CVEs |
| 27 | Document security workflow | DevOps | `docs/SECURITY_PIPELINE.md` |
| 28 | Sprint 2 retrospective | All | Lessons learned, improvements |

**Definition of Done Sprint 2:**
- [ ] All security tools run in CI
- [ ] Docker images build successfully
- [ ] Trivy scans pass (0 HIGH/CRITICAL)
- [ ] SBOM generated for each image
- [ ] Secret detection catches test secrets

---

### Sprint 3 (Week 5-6): Staging Deployment & E2E
**Goal**: Auto-deploy to staging on merge, run E2E smoke tests

| Day | Task | Owner | Deliverable |
|---|---|---|---|
| 29 | Provision staging infrastructure | DevOps | K8s namespace / Docker Swarm stack |
| 30 | Create docker-compose.staging.yml | DevOps | Staging compose override |
| 31 | Write database migration automation | Backend | Alembic in migrations container |
| 32 | Create cd-staging.yml workflow | DevOps | Deploy on merge to staging |
| 33 | Write Playwright E2E smoke tests | QA/Frontend | `frontend/tests/e2e/smoke.spec.ts` |
| 34 | Configure Playwright in CI | DevOps | Browser install, test execution |
| 35 | Add health check endpoints | Backend | `/health`, `/ready` with DB/Redis checks |
| 36 | Integrate E2E in staging deploy | DevOps | Post-deploy test step |
| 37 | Add Slack/Discord notifications | DevOps | Deployment status alerts |
| 38 | Test full PR → staging flow | All | End-to-end verification |
| 39 | Configure staging secrets (GitHub Environments) | DevOps | Protected secrets per env |
| 40 | Load test staging | QA | Baseline performance metrics |
| 41 | Document staging access | DevOps | `docs/STAGING_GUIDE.md` |
| 42 | Sprint 3 retrospective | All | Process improvements |

**Definition of Done Sprint 3:**
- [ ] Merge to staging → auto deploy
- [ ] Migrations run automatically
- [ ] Health checks pass
- [ ] E2E smoke tests pass
- [ ] Team notified of deployment status

---

### Sprint 4 (Week 7-8): Production Deployment & Release
**Goal**: Blue-Green production deploy, release artifacts for self-hosted

| Day | Task | Owner | Deliverable |
|---|---|---|---|
| 43 | Provision production infrastructure | DevOps | K8s cluster / managed services |
| 44 | Configure Blue-Green namespaces | DevOps | `blue`/`green` deployments |
| 45 | Write cd-production.yml workflow | DevOps | Manual approval + deploy |
| 46 | Configure ingress/service switching | DevOps | Traffic routing automation |
| 47 | Implement health check & rollback | DevOps | PrometheusRule / Flagger config |
| 48 | Configure monitoring (Prometheus/Grafana) | DevOps | Dashboards + alert rules |
| 49 | Integrate Sentry (backend + frontend) | All | Error tracking with source maps |
| 50 | Create release.yml workflow | DevOps | Tag-triggered release build |
| 51 | Generate release artifacts | DevOps | docker-compose.yml, .env.example, etc. |
| 52 | Test self-hosted install from release | QA | `docker compose up -d` works |
| 53 | Configure cosign image signing | DevOps | Keyless signing for supply chain |
| 54 | Write runbooks for rollback scenarios | DevOps | `docs/RUNBOOKS/` |
| 55 | Disaster recovery drill | All | Simulated incident response |
| 56 | Sprint 4 retrospective & docs | All | Complete CI/CD documentation |

**Definition of Done Sprint 4:**
- [ ] Production deploy via Blue-Green
- [ ] Auto-rollback on health check failure
- [ ] Release creates GitHub Release with artifacts
- [ ] Self-hosted install verified
- [ ] Monitoring + alerting operational
- [ ] Runbooks documented and tested

---

## 4.2 Technical Implementation Details

### 4.2.1 Repository Structure for CI/CD

```
pyforge/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Main CI pipeline
│   │   ├── cd-staging.yml      # Staging deployment
│   │   ├── cd-production.yml   # Production deployment
│   │   ├── release.yml         # Release artifact creation
│   │   ├── security.yml        # Scheduled security scans
│   │   └── dependabot.yml      # Dependency updates
│   ├── dependabot.yml
│   └── pull_request_template.md
├── backend/
│   ├── pyproject.toml          # ruff, mypy, pytest, coverage config
│   ├── Dockerfile              # Multi-stage build
│   ├── Dockerfile.migrations   # Migration runner
│   ├── .dockerignore
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── sandbox/
│   │   └── ai_providers/
│   └── app/
│       └── health.py           # Health check endpoint
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── eslint.config.js
│   ├── .prettierrc
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   ├── Dockerfile
│   ├── .dockerignore
│   └── tests/
│       ├── unit/
│       ├── components/
│       └── e2e/
├── sandbox/
│   ├── Dockerfile.runner       # Sandbox runner image
│   └── tests/
├── docker-bake.hcl             # Buildx bake definition
├── docker-compose.yml          # Base compose (production-ready)
├── docker-compose.staging.yml  # Staging overrides
├── docker-compose.dev.yml      # Development overrides
├── .env.example
├── init.sql
├── scripts/
│   ├── ci-local.sh
│   ├── deploy-staging.sh
│   └── deploy-production.sh
├── .pre-commit-config.yaml
├── docs/
│   ├── CI_USAGE.md
│   ├── SECURITY_PIPELINE.md
│   ├── STAGING_GUIDE.md
│   └── RUNBOOKS/
└── README.md
```

### 4.2.2 Key Configuration Files

#### `backend/pyproject.toml` (CI-relevant sections)
```toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E", "F", "I", "W", "UP", "B", "C4", "SIM", "T20", "PIE",
    "PT", "FLY", "NPY", "RET", "ARG", "PTH", "ERA", "PD", "PGH",
    "PL", "TRY", "ASYNC", "LOG", "NPY", "TCH", "INT", "RSE",
]
ignore = ["E501", "B008"]
per-file-ignores = {
    "tests/*": ["S101", "SLF001", "PLR2004"],
    "migrations/*": ["D100", "D101", "D102", "D103", "D104", "D107"]
}

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
show_error_codes = true
pretty = true

[[tool.mypy.overrides]]
module = ["tests.*", "alembic.*"]
strict = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-xvs",
    "--strict-markers",
    "--strict-config",
    "--cov=app",
    "--cov-fail-under=80",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--junitxml=junit.xml",
]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "migrations/*", "*/conftest.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[tool.bandit]
exclude_dirs = ["tests", "migrations"]
skips = ["B101", "B601"]  # assert_used, shell_check (context-dependent)
```

#### `frontend/package.json` (CI-relevant scripts)
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:run": "vitest run",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:components": "vitest run --config vitest.component.config.ts",
    "test:e2e": "playwright test",
    "test:e2e:smoke": "playwright test --project=chromium --grep @smoke",
    "test:e2e:staging": "playwright test --config playwright.staging.config.ts",
    "postinstall": "playwright install --with-deps chromium"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/node": "^20.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "eslint-config-next": "^14.0.0",
    "eslint-plugin-prettier": "^5.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0",
    "@vitest/coverage-v8": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jsdom": "^23.0.0"
  }
}
```

#### `docker-bake.hcl`
```hcl
group "default" {
  targets = ["frontend", "backend", "sandbox-runner", "migrations"]
}

target "frontend" {
  context = "./frontend"
  dockerfile = "Dockerfile"
  tags = [
    "ghcr.io/ORG/pyforge/frontend:latest",
    "ghcr.io/ORG/pyforge/frontend:${GIT_SHA}",
  ]
  platforms = ["linux/amd64", "linux/arm64"]
  cache-to = ["type=gha,mode=max"]
  cache-from = ["type=gha"]
  args = {
    NEXT_PUBLIC_API_URL = "https://api.pyforge.dev"
  }
}

target "backend" {
  context = "./backend"
  dockerfile = "Dockerfile"
  tags = [
    "ghcr.io/ORG/pyforge/backend:latest",
    "ghcr.io/ORG/pyforge/backend:${GIT_SHA}",
  ]
  platforms = ["linux/amd64", "linux/arm64"]
  cache-to = ["type=gha,mode=max"]
  cache-from = ["type=gha"]
}

target "sandbox-runner" {
  context = "./sandbox"
  dockerfile = "Dockerfile.runner"
  tags = [
    "ghcr.io/ORG/pyforge/sandbox-runner:latest",
    "ghcr.io/ORG/pyforge/sandbox-runner:${GIT_SHA}",
  ]
  platforms = ["linux/amd64"]
  cache-to = ["type=gha,mode=max"]
  cache-from = ["type=gha"]
}

target "migrations" {
  context = "./backend"
  dockerfile = "Dockerfile.migrations"
  tags = [
    "ghcr.io/ORG/pyforge/migrations:latest",
    "ghcr.io/ORG/pyforge/migrations:${GIT_SHA}",
  ]
  platforms = ["linux/amd64"]
}
```

### 4.2.3 GitHub Actions Workflow Templates

#### `.github/workflows/ci.yml` (Complete)
```yaml
name: CI Pipeline
on:
  pull_request:
    branches: [staging, main]
  push:
    branches: [staging, main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==========================================
  # STAGE 1: LINT & FORMAT (Parallel Matrix)
  # ==========================================
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: python
            working-directory: ./backend
            run: |
              ruff check .
              ruff format --check .
          - name: frontend
            working-directory: ./frontend
            run: |
              pnpm lint
              pnpm format:check
          - name: docker
            working-directory: .
            run: |
              hadolint Dockerfile* backend/Dockerfile* frontend/Dockerfile* sandbox/Dockerfile*
          - name: configs
            working-directory: .
            run: |
              yamllint .github .gitlab *.yml *.yaml 2>/dev/null || true
              markdownlint docs/**/*.md 2>/dev/null || true
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        if: matrix.name == 'python'
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install ruff
        if: matrix.name == 'python'
        run: pip install ruff==0.4.0
      - name: Set up Node
        if: matrix.name == 'frontend'
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Install frontend deps
        if: matrix.name == 'frontend'
        run: cd frontend && pnpm install --frozen-lockfile
      - name: Install hadolint
        if: matrix.name == 'docker'
        run: |
          wget -O /tmp/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
          chmod +x /tmp/hadolint
          sudo mv /tmp/hadolint /usr/local/bin/hadolint
      - name: Install config linters
        if: matrix.name == 'configs'
        run: |
          pip install yamllint markdownlint-cli
      - name: Run lint
        working-directory: ${{ matrix.working-directory }}
        run: ${{ matrix.run }}

  # ==========================================
  # STAGE 2: TYPE CHECK (Parallel)
  # ==========================================
  type-check:
    name: Type Check
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: python
            working-directory: ./backend
            run: mypy --strict --show-error-codes .
          - name: frontend
            working-directory: ./frontend
            run: pnpm typecheck
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        if: matrix.name == 'python'
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install deps
        if: matrix.name == 'python'
        run: |
          pip install -e .[dev]
          pip install mypy==1.9.0
      - name: Set up Node
        if: matrix.name == 'frontend'
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Install frontend deps
        if: matrix.name == 'frontend'
        run: cd frontend && pnpm install --frozen-lockfile
      - name: Run type check
        working-directory: ${{ matrix.working-directory }}
        run: ${{ matrix.run }}

  # ==========================================
  # STAGE 3: TESTS (Parallel Suites)
  # ==========================================
  test:
    name: Tests
    runs-on: ubuntu-latest
    needs: [lint, type-check]
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: backend-unit
            working-directory: ./backend
            services:
              postgres:
                image: postgres:15-alpine
                env:
                  POSTGRES_PASSWORD: test
                  POSTGRES_DB: pyforge_test
                ports: [5432:5432]
                options: >-
                  --health-cmd="pg_isready -U postgres"
                  --health-interval=10s
                  --health-timeout=5s
                  --health-retries=5
              redis:
                image: redis:7-alpine
                ports: [6379:6379]
                options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=5
            run: |
              pytest tests/unit -xvs --cov=app --cov-fail-under=80 --cov-report=xml --junitxml=junit.xml
            artifacts:
              - coverage.xml
              - junit.xml
              - htmlcov/
          - name: backend-integration
            working-directory: ./backend
            services:
              postgres:
                image: postgres:15-alpine
                env:
                  POSTGRES_PASSWORD: test
                  POSTGRES_DB: pyforge_test
                ports: [5432:5432]
              redis:
                image: redis:7-alpine
                ports: [6379:6379]
            run: |
              pytest tests/integration -xvs --cov=app --cov-append --cov-report=xml
            artifacts:
              - coverage.xml
          - name: sandbox-security
            working-directory: ./backend
            run: |
              pytest tests/sandbox -xvs -k "security"
            timeout-minutes: 10
          - name: ai-providers
            working-directory: ./backend
            run: |
              pytest tests/ai_providers -xvs
          - name: frontend-unit
            working-directory: ./frontend
            run: |
              pnpm test:run --coverage
            artifacts:
              - coverage/
              - junit.xml
          - name: frontend-components
            working-directory: ./frontend
            run: |
              pnpm test:components
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        if: matrix.name != 'frontend-unit' && matrix.name != 'frontend-components'
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install backend deps
        if: matrix.name != 'frontend-unit' && matrix.name != 'frontend-components'
        run: |
          cd backend && pip install -e .[dev,test]
      - name: Set up Node
        if: matrix.name == 'frontend-unit' || matrix.name == 'frontend-components'
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Install frontend deps
        if: matrix.name == 'frontend-unit' || matrix.name == 'frontend-components'
        run: cd frontend && pnpm install --frozen-lockfile
      - name: Run tests
        working-directory: ${{ matrix.working-directory }}
        run: ${{ matrix.run }}
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/pyforge_test
          REDIS_URL: redis://localhost:6379/0
          PYTHONPATH: ${{ matrix.working-directory }}
      - name: Upload coverage
        if: matrix.artifacts != null
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.name }}
          path: ${{ matrix.working-directory }}/${{ matrix.artifacts }}
          retention-days: 7

  # ==========================================
  # STAGE 4: SECURITY SCAN
  # ==========================================
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: [test]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install security tools
        run: |
          pip install bandit==1.7.5 pip-audit==2.7.0 gitleaks==8.18.0
      - name: Run Bandit (Python SAST)
        run: |
          bandit -r backend/app -f json -o bandit-report.json -ll
          HIGH=$(jq '[.results[] | select(.severity=="HIGH")] | length' bandit-report.json)
          MEDIUM=$(jq '[.results[] | select(.severity=="MEDIUM")] | length' bandit-report.json)
          if [ "$HIGH" -gt 0 ] || [ "$MEDIUM" -gt 0 ]; then
            echo "::error::Bandit found $HIGH HIGH and $MEDIUM MEDIUM issues"
            cat bandit-report.json | jq '.results[] | select(.severity=="HIGH" or .severity=="MEDIUM")'
            exit 1
          fi
      - name: Run pip-audit
        run: |
          cd backend && pip-audit --desc --format=json --output=../pip-audit.json
          HIGH=$(jq '[.vulnerabilities[] | select(.fix_versions != null) | .aliases[]? | select(startswith("GHSA"))] | length' ../pip-audit.json)
          # Check for HIGH/CRITICAL via GHSA severity mapping
          CRITICAL_COUNT=$(python3 -c "
import json, sys
with open('../pip-audit.json') as f:
    data = json.load(f)
crit = sum(1 for v in data.get('vulnerabilities', [])
           for a in v.get('aliases', [])
           if a.startswith('GHSA') and any(s in a.lower() for s in ['critical', 'high']))
sys.exit(1 if crit > 0 else 0)
")
          if [ $? -ne 0 ]; then
            echo "::error::pip-audit found CRITICAL/HIGH vulnerabilities"
            exit 1
          fi
      - name: Run npm audit
        run: |
          cd frontend && npm audit --json > ../npm-audit.json 2>&1 || true
          HIGH=$(jq '[.vulnerabilities[] | select(.severity=="high" or .severity=="critical")] | length' ../npm-audit.json)
          if [ "$HIGH" -gt 0 ]; then
            echo "::error::npm audit found $HIGH HIGH/CRITICAL vulnerabilities"
            exit 1
          fi
      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          args: detect --source=. --verbose --report-format=json --report-path=gitleaks-report.json

  # ==========================================
  # STAGE 5: BUILD & TRIVY SCAN
  # ==========================================
  build:
    name: Build & Scan Images
    runs-on: ubuntu-latest
    needs: [security]
    permissions:
      contents: read
      packages: write
      security-events: write
    strategy:
      fail-fast: false
      matrix:
        include:
          - name: frontend
            context: ./frontend
            dockerfile: Dockerfile
          - name: backend
            context: ./backend
            dockerfile: Dockerfile
          - name: sandbox-runner
            context: ./sandbox
            dockerfile: Dockerfile.runner
          - name: migrations
            context: ./backend
            dockerfile: Dockerfile.migrations
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.name }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=
            type=raw,value=latest,enable={{is_default_branch}}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.dockerfile }}
          push: ${{ github.event_name != 'pull_request' }}
          load: ${{ github.event_name == 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
      - name: Trivy Scan
        if: github.event_name != 'pull_request'
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.tags }}
          format: 'sarif'
          output: 'trivy-${{ matrix.name }}.sarif'
          severity: 'HIGH,CRITICAL'
          ignore-unfixed: true
          vuln-type: 'os,library'
      - name: Upload Trivy Results
        if: github.event_name != 'pull_request'
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-${{ matrix.name }}.sarif'

  # ==========================================
  # STAGE 6: E2E SMOKE TESTS
  # ==========================================
  e2e-smoke:
    name: E2E Smoke Tests
    runs-on: ubuntu-latest
    needs: [build]
    if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: pyforge_test
        ports: [5432:5432]
        options: >-
          --health-cmd="pg_isready -U postgres"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
      redis:
        image: redis:7-alpine
        ports: [6379:6379]
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=5
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml
      - name: Install frontend deps
        run: cd frontend && pnpm install --frozen-lockfile
      - name: Install Playwright
        run: cd frontend && pnpm exec playwright install --with-deps chromium
      - name: Start Application Stack
        run: |
          docker compose -f docker-compose.ci.yml up -d --wait
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/pyforge_test
          REDIS_URL: redis://localhost:6379/0
      - name: Run Smoke Tests
        run: |
          cd frontend && pnpm test:e2e:smoke
        env:
          BASE_URL: http://localhost:3000
          API_URL: http://localhost:8000
      - name: Upload Playwright Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/test-results/
          retention-days: 7

  # ==========================================
  # QUALITY GATE SUMMARY
  # ==========================================
  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [lint, type-check, test, security, build, e2e-smoke]
    if: always()
    steps:
      - name: Check all jobs passed
        run: |
          FAILED=0
          for job in lint type-check test security build e2e-smoke; do
            RESULT=$(echo "${{ needs.$job.result }}" | tr '[:upper:]' '[:lower:]')
            if [ "$RESULT" != "success" ]; then
              echo "::error::Job $job failed with result: $RESULT"
              FAILED=1
            fi
          done
          if [ $FAILED -eq 1 ]; then
            exit 1
          fi
      - name: All quality gates passed ✅
        run: echo "All quality gates passed! Ready to merge."
```

---

## 4.3 Resource Requirements

| Resource | Specification | Estimated Cost |
|---|---|---|
| **GitHub Actions Minutes** | ~2000 min/month (private repo) | Included in GitHub Team/Enterprise |
| **Container Registry** | GHCR (10GB free, then $0.008/GB) | ~$5-10/month |
| **Staging Environment** | 2x t3.medium (EC2) or equivalent | ~$60/month |
| **Production Environment** | K8s managed (EKS/GKE) or 3x t3.large | ~$200-500/month |
| **Monitoring** | Prometheus/Grafana Cloud (free tier) | $0-50/month |
| **Sentry** | Team plan (100k events/month) | $26/month |
| **Total Estimated** | | **~$300-600/month** |

---

## 4.4 Success Metrics for CI/CD

| Metric | Target | Measurement |
|---|---|---|
| **CI Pipeline Duration** | < 10 minutes (P95) | GitHub Actions workflow timing |
| **CI Success Rate (main)** | > 95% | Passed runs / Total runs |
| **Mean Time to Feedback** | < 5 minutes | PR open → first CI result |
| **Deployment Frequency** | Daily (staging), Weekly (prod) | Deployments per period |
| **Change Failure Rate** | < 5% | Failed deployments / Total |
| **MTTR (Production)** | < 30 minutes | Incident open → resolved |
| **Security Scan Pass Rate** | 100% (blocking) | No HIGH/CRITICAL in main |

---

## 4.5 Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Flaky E2E tests block deploy | Medium | High | Retry logic, quarantine flaky tests, separate smoke vs full E2E |
| Docker build cache misses | Low | Medium | Buildx cache (GHCR), layer optimization |
| Security tool false positives | Medium | Low | Baseline suppressions, regular review |
| Staging environment drift | Low | High | IaC (Terraform), GitOps (ArgoCD/Flux) |
| Secrets rotation failure | Low | Critical | Automated rotation, emergency access procedure |
| Dependency supply chain attack | Low | Critical | Pin versions, verify signatures, Dependabot |

---

*Plan Version: 1.0 | Created: 2026-01-17 | Review: Sprint Planning*