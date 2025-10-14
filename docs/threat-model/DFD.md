# DFD — Threat model (меревая диаграмма в Mermaid)

**Описание:** DFD уровня «контекст + логика + хранение данных» для сервиса Wishlist (FastAPI). Отмечены границы доверия, внешние участники, хранилища, протоколы и пронумерованы потоки F1…F8.

```mermaid
flowchart LR
  %% External actors
  A[User (Browser / Mobile)] -->|F1: HTTPS GET /wishes| GW[API Gateway / LB]
  A -->|F2: HTTPS GET /wishes/search| GW
  A -->|F3: HTTPS POST /wishes| GW
  A -->|F4: HTTPS PUT /wishes/{id}| GW
  A -->|F5: HTTPS DELETE /wishes/{id}| GW

  subgraph Edge["Trust Boundary: Edge (client <-> edge)"]
    style Edge stroke:#333,stroke-width:2px
    GW -->|F6: Reverse proxy -> FastAPI| SVC[FastAPI Service (wishes)]
  end

  subgraph Core["Trust Boundary: Core (app logic)"]
    style Core stroke:#333,stroke-width:2px
    SVC -->|F7: Read/Write (in-memory) / planned DB| DB[(Database / Persistence)]
    SVC -->|F8: Metrics / Logging -> Monitoring| MON[Prometheus / ELK]
  end

  %% Notes
  classDef ext fill:#f9f,stroke:#333;
  class A ext;

  %% Legend
  %% F1..F5 : client API flows
  %% F6 : proxy / edge to service
  %% F7 : service to storage
  %% F8 : telemetry flows

```
