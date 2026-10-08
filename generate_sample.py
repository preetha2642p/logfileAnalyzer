#!/usr/bin/env python3
"""Generate a realistic sample log: python generate_sample.py [lines] > sample.log"""
import random, sys

SOURCES = ["auth", "db", "api", "cache", "scheduler", "payments", "mailer"]
LEVELS = ["INFO"] * 5 + ["DEBUG"] * 2 + ["WARN"] * 2 + ["ERROR"]
MESSAGES = ["User 4821 logged in", "Request served in 143ms", "Cache hit for key 77",
            "Connection timeout after 30s", "Retrying job 912 attempt 3", "Disk usage at 91%",
            "Payment 5521 declined by gateway", "Slow query took 2400ms",
            "Invalid token for session 330", "Health check passed", "Null reference in handler 12"]


def generate(n: int = 800, seed: int = 42) -> str:
    rnd, rows = random.Random(seed), []
    for i in range(1, n + 1):
        h = 3 if i % 97 == 0 else int(8 + rnd.random() * rnd.random() * 14)
        rows.append(f"2026-10-07 {h:02d}:{rnd.randrange(60):02d}:{rnd.randrange(60):02d} "
                    f"{rnd.choice(LEVELS)} [{rnd.choice(SOURCES)}] {rnd.choice(MESSAGES)}")
    return "\n".join(sorted(rows, key=lambda r: r[11:])) + "\n"


if __name__ == "__main__":
    sys.stdout.write(generate(int(sys.argv[1]) if len(sys.argv) > 1 else 800))
