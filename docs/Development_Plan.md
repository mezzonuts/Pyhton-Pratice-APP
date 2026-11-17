# Application Development Plan - PyForge
## Sprint-by-Sprint Feature Development Roadmap

---

## 5.1 Development Philosophy

### 5.1.1 Principles
- **Dogfooding**: Backend built with FastAPI using same standards we teach (PEP 8, type hints, tests)
- **Security First**: Sandbox isolation from Day 1, never trust user code
- **Offline-First**: Pyodide for Tier 0-1, server sandbox for Tier 2+
- **AI-Native**: Every feature considers AI integration (hints, review, generation)
- **Observable**: Structured logging, metrics, tracing from start

### 5.1.2 Definition of Done (Per Feature)
- [ ] Code passes all CI gates (lint, type, test, security)
- [ ] Unit tests ≥80% coverage, integration tests for APIs
- [ ] E2E test for critical user path
- [ ] Documentation updated (API docs, user guide if UI)
- [ ] Feature flagged for gradual rollout
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

---

## 5.2 Sprint Structure (14 Days = 2 Sprints × 7 Days)

### Sprint 1 (Days 1-7): Foundation & Tier 0
**Goal**: Working app with auth, Tier 0 missions, Pyodide sandbox, basic AI

| Day | Epic | Stories | Acceptance Criteria |
|---|---|---|---|
| **1** | **Project Setup** | Initialize repos, CI, Docker | `docker compose up` runs full stack |
| | | Next.js + FastAPI monorepo structure | All lint/type/test pass |
| | | PostgreSQL + Redis + Alembic | Migrations run automatically |
| | | GitHub Actions CI pipeline | PR → green CI |
| **2** | **Auth & User Model** | Email/password + OAuth (GitHub) | Register, login, logout work |
| | | JWT tokens (access + refresh) | Token refresh silent |
| | | User profile + tier/elo fields | Tier 0 default, ELO 1000 |
| | | Auth.js + FastAPI integration | Shared session, protected routes |
| **3** | **Tier 0 Curriculum Engine** | Mission data model (JSON/DB) | 14 missions defined |
| | | Daily mission scheduler (cron) | 00:00 WIB new mission |
| | | Mission API (GET today, GET history) | Returns ticket, starter code, tests |
| | | Tier progression logic | Auto-unlock Tier 1 at ELO 1100 |
| **4** | **Pyodide Sandbox (Client)** | Monaco Editor integration | Python syntax highlight, autocomplete |
| | | Pyodide load + REPL | `python -c "print(1+1)"` works in browser |
| | | Test runner (pytest in WASM) | Run user code vs hidden tests |
| | | Result display (pass/fail, output) | Show stdout, stderr, traceback |
| **5** | **Grader Pipeline (Client-side)** | Ruff lint in WASM (micropython port) | Basic syntax check |
| | | Functional test execution | All test cases pass/fail |
| | | Score calculation (simplified) | Grade A-F, XP reward |
| | | Streak & XP update API | Persist to backend |
| **6** | **AI Integration - 9Router/Ollama** | AI Settings page | Add/edit/delete providers |
| | | Connection test button | Validates `/v1/chat/completions` |
| | | Socratic Hint API (Tier 0) | Returns hint, not answer |
| | | Secure key storage (encrypted) | AES-256-GCM in DB |
| **7** | **Dashboard & Polish** | User dashboard | Streak, XP, ELO, Skill Radar |
| | | Mission history view | Past submissions, grades |
| | | Responsive UI + dark mode | Tailwind, mobile friendly |
| | | Sprint 1 Demo & Retro | All Tier 0 playable end-to-end |

**Sprint 1 Deliverable**: **Playable Tier 0** - User can register, get daily mission, code in browser, run tests via Pyodide, get AI hints, see progress.

---

### Sprint 2 (Days 8-14): Tier 1 + Server Sandbox + Grader
**Goal**: Multi-file missions, server-side grading, real sandbox, AI PR review

| Day | Epic | Stories | Acceptance Criteria |
|---|---|---|---|
| **8** | **Server Sandbox Infrastructure** | Docker runner image (Python 3.11 + tools) | `pytest`, `ruff`, `mypy` installed |
| | | gVisor runtime configuration | `--runtime=runsc` works |
| | | Resource limits (CPU, RAM, timeout) | Enforced at container level |
| | | Network isolation (`--network=none`) | No external connections |
| | | Job queue (Redis + BullMQ/Arq) | Async job processing |
| **9** | **Grader Pipeline (Server)** | Multi-stage grader orchestration | Lint → Format → Type → Test → Perf → Quality |
| | | Ruff + mypy + pytest execution | All tools run in sandbox |
| | | Performance benchmarking | Time/memory measurement |
| | | Code quality analyzer | Cyclomatic complexity, nesting |
| | | Grader result aggregation | Weighted score, grade S-F |
| **10** | **Multi-File Workspace** | Project structure generator | `ticket.md`, `app/`, `tests/`, `data/` |
| | | File tree navigation in Monaco | Tabs, explorer panel |
| | | Multi-file submission API | Zip or JSON file map |
| | | Hidden test files (grader only) | User sees only `test_public.py` |
| **11** | **Tier 1 Curriculum (28 missions)** | Data wrangling missions | JSON/CSV parsing, comprehensions |
| | | Error handling missions | try/except, custom exceptions |
| | | Big-O awareness missions | Complexity analysis in tests |
| | | Mission difficulty calibration | ELO targets 1100-1250 |
| **12** | **AI PR Reviewer** | Senior Engineer review prompt | Constructive, specific, educational |
| | | Review API integration | Trigger on grade ≥ B |
| | | Review display in UI | Side-by-side diff, comments |
| | | Feedback loop (re-submit) | User can iterate after review |
| **13** | **Boss Fight & Gamification** | Weekly incident scenario | Multi-file, time-boxed, story-driven |
| | | Streak freeze mechanics | Weekend claim, auto-apply |
| | | Skill Radar visualization | 5-dimension radar chart |
| | | Leaderboard (anonymous, opt-in) | Weekly/monthly tiers |
| **14** | **Integration Testing & Launch Prep** | Full E2E test suite | Playwright: auth → mission → grade → review |
| | | Load test sandbox queue | 50 concurrent submissions |
| | | Security audit (sandbox escape) | Pen-test attempts |
| | | Documentation complete | User guide, API docs, architecture |
| | | Sprint 2 Demo & Retro | Tier 0-1 complete, Tier 2 ready |

**Sprint 2 Deliverable**: **Production-Ready Tier 0-1** - Full grader pipeline, server sandbox, multi-file workspace, AI reviewer, weekly boss fights.

---

## 5.3 Post-MVP Roadmap (Sprints 3+)

### Sprint 3 (Week 3-4): Tier 2 - Engineering Standards
- OOP & Design Patterns missions (Strategy, Factory, Observer)
- PEP 8 / ruff integration in grader (strict mode)
- Type hinting missions (generics, protocols, overload)
- pytest deep dive (fixtures, parametrize, mocking)
- Virtual environment & dependency management
- Logging missions (structured logging, levels, correlation IDs)

### Sprint 4 (Week 5-6): Tier 3 - Real-Job Simulation
- REST API client missions (httpx, retry, rate limit, circuit breaker)
- ETL pipeline missions (dirty data, validation, transformation)
- Async Python missions (asyncio, aiohttp, concurrent.futures)
- Database missions (SQLAlchemy, migrations, query optimization)
- Concurrency missions (threading, multiprocessing, asyncio.gather)

### Sprint 5 (Week 7-8): Tier 4 - Senior Engineering
- Legacy code refactoring missions (strangler fig, characterization tests)
- Memory leak detection (tracemalloc, objgraph)
- Race condition debugging (threading, asyncio)
- Security hardening (SQLi, XSS, deserialization, secrets)
- PR Code Review simulation (AI as reviewer + reviewee)

### Sprint 6 (Week 9-10): Platform Hardening
- Team workspaces & private missions
- Custom curriculum builder (instructor UI)
- Advanced analytics (cohort, funnel, retention)
- Mobile-responsive polish
- Accessibility audit (WCAG 2.1 AA)
- Performance optimization (bundle size, API latency)

---

## 5.4 Technical Architecture Decisions (ADRs)

| ADR | Title | Decision | Status |
|---|---|---|---|
| **ADR-001** | Monorepo vs Polyrepo | Monorepo (single repo, shared CI) | ✅ Accepted |
| **ADR-002** | Authentication | Auth.js (NextAuth v5) + FastAPI JWT | ✅ Accepted |
| **ADR-003** | Sandbox Isolation | gVisor + Docker (server), Pyodide (client) | ✅ Accepted |
| **ADR-004** | AI Provider Protocol | OpenAI-compatible only | ✅ Accepted |
| **ADR-005** | Database Migrations | Alembic (async) | ✅ Accepted |
| **ADR-006** | State Management | Zustand (client) + TanStack Query (server) | ✅ Accepted |
| **ADR-007** | Real-time Updates | Server-Sent Events (SSE) for grader progress | ✅ Accepted |
| **ADR-008** | File Storage | Local filesystem (dev), S3-compatible (prod) | ✅ Accepted |
| **ADR-009** | Mission Storage | PostgreSQL JSONB (flexible schema) | ✅ Accepted |
| **ADR-010** | Grader Orchestration | Arq (Redis) for job queue | ✅ Accepted |

---

## 5.5 Team Structure & Roles

| Role | Responsibilities | Sprint 1-2 Focus |
|---|---|---|
| **Tech Lead** | Architecture, code review, unblocking | ADR decisions, CI/CD setup |
| **Backend Engineer (2)** | FastAPI, DB, Sandbox, Grader, AI | Auth, Grader, Sandbox, API |
| **Frontend Engineer (2)** | Next.js, Monaco, Dashboard, E2E | Editor, Dashboard, Mission UI |
| **DevOps Engineer** | CI/CD, Infra, Monitoring, Security | Pipeline, Staging, Deploy |
| **QA Engineer** | Test strategy, E2E, Security, Load | Test infra, Playwright, Sandbox tests |
| **Product Designer** | UX, UI, Gamification, Curriculum | Mission UX, Dashboard, Skill Radar |

---

## 5.6 Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Pyodide performance/memory limits | High | Medium | Fallback to server sandbox, optimize WASM load | Frontend |
| Sandbox escape vulnerability | Low | Critical | gVisor, regular pen-tests, bounty program | Backend/DevOps |
| AI provider API changes | Medium | Medium | Adapter pattern, version pinning, fallback chain | Backend |
| Curriculum content creation bottleneck | High | High | AI-assisted generation, template system | Product/Design |
| Grader pipeline latency >2s | Medium | High | Async processing, caching, tiered timeouts | Backend |
| User churn due to difficulty spikes | Medium | High | Adaptive difficulty, skip tokens, extensive playtesting | Product |
| Database migration failures | Low | High | Backward-compatible migrations, rollback tested | Backend |
| Third-party dependency vulnerabilities | Medium | High | Dependabot, weekly audit, pinned versions | DevOps |

---

## 5.7 Success Metrics (Per Sprint)

| Sprint | Metric | Target |
|---|---|---|
| **Sprint 1** | Tier 0 completion rate | > 80% |
| | Daily active users (beta) | > 20 |
| | Pyodide load time | < 3s |
| | AI hint relevance (user rating) | > 4/5 |
| **Sprint 2** | Tier 1 completion rate | > 75% |
| | Server sandbox success rate | > 99% |
| | Grader latency P95 | < 5s |
| | AI review helpfulness | > 4/5 |
| | Boss fight participation | > 60% |
| **Sprint 3+** | Tier progression rate | > 25% reach Tier 3 in 90 days |
| | 30-day retention | > 40% |
| | NPS (beta users) | > 50 |

---

## 5.8 Communication & Rituals

| Ritual | Frequency | Duration | Participants |
|---|---|---|---|
| **Daily Standup** | Daily | 15 min | All engineers |
| **Sprint Planning** | Bi-weekly | 2 hours | All |
| **Sprint Review** | Bi-weekly | 1 hour | All + Stakeholders |
| **Sprint Retrospective** | Bi-weekly | 1 hour | All engineers |
| **Architecture Review** | Weekly | 1 hour | Tech Lead + Senior |
| **Security Review** | Monthly | 2 hours | DevOps + Backend |
| **Curriculum Review** | Weekly | 1 hour | Product + Design + Eng |

---

## 5.9 Definition of Ready (Story Level)

A story is ready for sprint when:
- [ ] Clear acceptance criteria (Given/When/Then)
- [ ] Designs/mockups approved (if UI)
- [ ] API contract defined (OpenAPI spec)
- [ ] Dependencies identified and available
- [ ] Test strategy outlined (unit, integration, E2E)
- [ ] Security considerations documented
- [ ] Estimated (story points) by team
- [ ] No blocking dependencies

---

## 5.10 Definition of Done (Story Level)

A story is done when:
- [ ] Code merged to `staging` (PR approved, CI green)
- [ ] Unit tests pass (≥80% coverage on new code)
- [ ] Integration tests pass (if API)
- [ ] E2E test covers happy path (if UI)
- [ ] Documentation updated (API docs, user-facing)
- [ ] Feature flag implemented (if risky)
- [ ] Monitoring/alerting configured
- [ ] Rollback plan documented
- [ ] Deployed to staging and verified
- [ ] Product Owner acceptance

---

*Plan Version: 1.0 | Created: 2026-01-17 | Next Review: Sprint Planning*