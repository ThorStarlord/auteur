"""Run the deterministic synthetic V1.1 harness qualification."""
import json
from execution_harness import qualify_synthetic

if __name__ == "__main__":
    print(json.dumps(qualify_synthetic(), indent=2, sort_keys=True))

