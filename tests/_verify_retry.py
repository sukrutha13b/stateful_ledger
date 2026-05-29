import sys
sys.path.insert(0, '.')
from engine.gemini_client import _parse_retry_delay

test_cases = [
    ("429 RESOURCE_EXHAUSTED 'retryDelay': '46s'", 48.0),
    ("429 RESOURCE_EXHAUSTED retryDelay: 26.2s", 28.2),
    ("some other error", 5.0),
    ("RESOURCE_EXHAUSTED no delay info", 60.0),
]

all_ok = True
for err, expected in test_cases:
    result = _parse_retry_delay(err)
    status = "OK" if abs(result - expected) < 1 else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] input={err[:50]!r}  -> {result}s  (expected ~{expected}s)")

print("\nSyntax OK, module imports fine.")
sys.exit(0 if all_ok else 1)
