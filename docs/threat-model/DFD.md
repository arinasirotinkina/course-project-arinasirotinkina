# DFD — Threat model (меревая диаграмма в Mermaid)

**Описание:** DFD уровня «контекст + логика + хранение данных» для сервиса Wishlist (FastAPI). Отмечены границы доверия, внешние участники, хранилища, протоколы и пронумерованы потоки F1…F8.

```mermaid
flowchart LR
  %% External actors (упрощённо, без фигурных скобок и слешей)
  A[User] -->|F1 GET| GW[API Gateway]
  A -->|F2 SEARCH| GW
  A -->|F3 POST| GW
  A -->|F4 PUT| GW
  A -->|F5 DELETE| GW

  subgraph Edge["Trust Boundary: Edge"]
    GW -->|F6 proxy to app| SVC[FastAPI Service]
  end

  subgraph Core["Trust Boundary: Core"]
    SVC -->|F7 DB read/write| DB[(Database)]
    SVC -->|F8 metrics/logs| MON[Monitoring]
  end

```

F1..F5 : client API flows

F6 : proxy / edge to service

F7 : service to storage

F8 : telemetry flows
