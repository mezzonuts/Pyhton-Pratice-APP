# Business Requirements Document (BRD) - PyForge
## Platform Latihan Python Berbasis Real-Job Simulation

---

### 1.1 Ringkasan Eksekutif & Visi

**Masalah:** Mayoritas platform belajar Python terjebak pada dua ekstrem:
- **Terlalu teoritis**: Tutorial hell dengan soal aritmatika membosankan, jauh dari realitas kerja
- **Terlalu kompetitif**: Langsung melompat ke LeetCode-style algoritma yang tidak relevan dengan pekerjaan sehari-hari

**Visi Produk:** Membangun platform latihan Python harian berbasis **skenario dunia kerja nyata (real-job simulation)** dari level nol hingga standar engineering internasional (PEP 8, type hinting, unit testing, debugging, clean architecture), dengan **biaya operasional AI mendekati nol** melalui arsitektur **Bring Your Own AI / Local Gateway** (9Router, Ollama, OpenAI-compatible).

**Nama Kode Produk:** PyForge (menempa skill Python seperti besi di api)

---

### 1.2 Tujuan Bisnis & KPI (Success Metrics)

| Tujuan Bisnis | Indikator Keberhasilan (KPI) | Target |
|---|---|---|
| **Keterikatan Harian (Habit)** | Daily Active Usage & 7-Day Streak Retention | > 60% pengguna aktif minimal 15 menit/hari |
| **Kualitas Pembelajaran (Anti-Boring)** | Mission Completion Rate | > 75% misi harian diselesaikan tanpa drop-off |
| **Kesiapan Standar Internasional** | Skor Kualitas Kode (Linter + Test Coverage + Complexity) | Rata-rata skor standar industri ≥ 85/100 di Tier 3+ |
| **Efisiensi Biaya AI** | AI Operational Cost per User | $0 (menggunakan endpoint lokal/9Router milik user) |
| **Retensi Jangka Panjang** | 30-Day Retention Rate | > 40% |
| **Konversi ke Tier Tinggi** | Persentase user mencapai Tier 3+ dalam 90 hari | > 25% |

---

### 1.3 Target Pengguna (User Personas)

| Persona | Deskripsi | Pain Points | Kebutuhan Utama |
|---|---|---|---|
| **The Zero-Base Starter** | Belum pernah ngoding sama sekali, mudah bosan dengan teori panjang, butuh feedback instan dan bahasa yang membumi | Tidak tahu mulai dari mana, takut error, butuh motivasi harian | Onboarding visual, error messaging ramah, Tier 0 micro-missions, ELI5 AI mode |
| **The Tutorial-Stuck Learner** | Bisa sintaks dasar (if, for, def), tapi blank total saat diminta menyelesaikan masalah bisnis atau membaca kode orang lain | "Tutorial hell", tidak bisa transfer knowledge ke project nyata | Multi-file workspace, Jira-style tickets, real data scenarios, code navigation practice |
| **The Global-Ready Aspiring Engineer** | Ingin naik level ke standar kerja internasional (production-grade, async, API integration, testing, refactoring, code review) | Kurang exposure ke best practices, code review, debugging production | Tier 3-4 simulations, PR reviewer AI, performance profiling, legacy refactoring |

---

### 1.4 Batasan & Asumsi Bisnis (Constraints & Assumptions)

| Kategori | Detail |
|---|---|
| **AI Cost Neutrality** | Aplikasi **tidak mengunci user ke satu provider AI berbayar**. Wajib mendukung protokol **OpenAI-Compatible API** sehingga bisa terhubung ke: 9Router (http://localhost:20128/v1) untuk auto-fallback & penghematan token, Ollama, LM Studio, maupun API cloud (OpenAI/Anthropic/Gemini). |
| **Arsitektur Eksekusi Lokal/Hybrid** | Karena 9Router berjalan di localhost user (127.0.0.1:20128), aplikasi harus dapat dijalankan secara: **self-hosted/local (Docker/Desktop)** ATAU **client-side fetch dengan CORS** agar localhost user tetap dapat diakses tanpa mempublikasikan local gateway ke internet. |
| **Platform Target** | Web App (Next.js/React) + Desktop wrapper (Tauri/Electron) untuk akses localhost sandbox |
| **Bahasa** | Python only (Fase 1), Indonesian primary language |
| **Monetisasi** | Freemium: Core features free, Advanced tiers (Tier 3+), Team/Enterprise features paid |
| **Compliance** | GDPR-ready, data lokal di device user (no cloud dependency for core features) |

---

### 1.5 Ruang Lingkup (Scope)

#### In-Scope (Fase 1 - MVP + Core)
- ✅ **Kurikulum bertingkat (Tier 0–4)**: 16+ minggu terstruktur
- ✅ **Sandbox eksekusi Python aman**: Pyodide (client) + Docker containers (server)
- ✅ **Mesin gamifikasi harian**: Streak, XP, Skill Radar, ELO Rating, Boss Fight
- ✅ **Simulator tiket kerja nyata**: Jira-style tickets, Acceptance Criteria, Multi-file workspace
- ✅ **Integrasi multi-provider AI**: Socratic Mentor + Automated PR Reviewer + Dynamic Problem Generator
- ✅ **Automated International Grader**: pytest + ruff + mypy + performance benchmarking
- ✅ **Self-hosted deployment**: docker-compose one-command setup
- ✅ **Offline-first capability**: Pyodide untuk Tier 0-1 basic exercises

#### Out-of-Scope (Fase 1)
- ❌ Video streaming course panjang
- ❌ Fitur sosial/forum publik besar (hanya leaderboard anonymized)
- ❌ Sertifikasi berbayar pihak ketiga
- ❌ Bahasa pemrograman selain Python
- ❌ Mobile app native (responsive web only)
- ❌ Real-time collaboration/multiplayer coding

#### Future Phases
- **Fase 2**: Team workspaces, code review collaboration, hiring portal integration
- **Fase 3**: Multi-language support (JS/TS, Go, Rust), AI-generated curriculum
- **Fase 4**: Enterprise SSO, advanced analytics, custom curriculum builder

---

### 1.6 Model Bisnis & Monetisasi

| Tier | Harga | Fitur |
|---|---|---|
| **Free (Forever)** | $0 | Tier 0-2 access, Pyodide sandbox, Basic AI (local only), Streak & XP, Community support |
| **Pro** | $15/bln | Tier 3-4 access, Server sandbox, Cloud AI providers, Advanced analytics, Priority support |
| **Team/Enterprise** | Custom | Private workspaces, Custom curriculum, SSO/SAML, Dedicated sandbox runners, SLA |

---

### 1.7 Risk Assessment & Mitigation

| Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|
| User tidak punya GPU/local AI | Tinggi | Tidak bisa pakai AI features | Pyodide fallback, free tier cloud AI trial, 9Router free tier |
| Sandbox escape / RCE | Rendah | Critical security breach | --network=none, --read-only, gVisor/Kata Containers, regular pen-test |
| Kurikulum terlalu sulit/mudah | Sedang | Churn tinggi | Adaptive difficulty, skip unlocked, extensive playtesting |
| Biaya server sandbox melonjak | Sedang | Burn rate tinggi | Spot instances, auto-scale to zero, user-provided runners |

---

### 1.8 Dependencies & Integration Points

| Komponen | Teknologi | Catatan |
|---|---|---|
| **Frontend** | Next.js 14+, React 18, TypeScript, Tailwind, Monaco Editor | App Router, Server Components |
| **Backend** | FastAPI (Python 3.11+), SQLAlchemy 2.0, Pydantic v2 | Async first, OpenAPI auto-docs |
| **Database** | PostgreSQL 15+ (primary), Redis 7+ (cache/queue) | Alembic migrations |
| **Sandbox (Client)** | Pyodide 0.26+ (WebAssembly) | WASM, ~6MB initial load |
| **Sandbox (Server)** | Docker + gVisor, Python 3.11, pytest, ruff, mypy | Isolated, no network, resource limits |
| **AI Gateway** | 9Router, Ollama, LM Studio, OpenAI-compatible | User-provided endpoints |
| **Auth** | NextAuth.js v5 / Auth.js | Email/password, OAuth (GitHub, Google) |
| **Deployment** | Docker Compose (local), Kubernetes (cloud) | GitHub Actions CI/CD |
| **Monitoring** | Sentry, Prometheus, Grafana | Self-hosted friendly |

---

### 1.9 Success Criteria for MVP Launch

- [ ] **Tier 0-1 complete**: 20+ micro-missions, all passing grader
- [ ] **Daily engine working**: Streak, XP, random mission generator
- [ ] **AI integration working**: 9Router + Ollama + OpenAI tested
- [ ] **Sandbox secure**: Pyodide + Docker server both functional
- [ ] **Self-hosted deployable**: `docker compose up -d` works on fresh machine
- [ ] **CI/CD green**: All quality gates passing
- [ ] **Documentation complete**: User guide, API docs, architecture docs
- [ ] **Beta test**: 50+ users, >70% completion rate Tier 0