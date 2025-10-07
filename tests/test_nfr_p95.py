import math
import time

import pytest
from fastapi.testclient import TestClient

from app.main import app

CLIENT_REQUESTS = 100  # число запросов для выборки
P95_THRESHOLD_SECONDS = 0.2  # 200 ms


def compute_p95(samples):
    if not samples:
        return 0.0
    s = sorted(samples)
    n = len(s)
    idx = int(math.ceil(0.95 * n)) - 1
    idx = max(0, min(idx, n - 1))
    return s[idx]


@pytest.mark.integration
def test_p95_get_wishes():

    client = TestClient(app)

    times = []
    for _ in range(CLIENT_REQUESTS):
        start = time.perf_counter()
        resp = client.get("/wishes/")
        elapsed = time.perf_counter() - start

        assert resp.status_code == 200

        times.append(elapsed)

    p95 = compute_p95(times)
    print(f"samples={len(times)}, p95_s={p95:.6f}, p95_ms={p95*1000:.2f}")

    assert (
        p95 <= P95_THRESHOLD_SECONDS
    ), f"p95 latency breach: {p95*1000:.2f} ms > {P95_THRESHOLD_SECONDS*1000:.0f} ms"
