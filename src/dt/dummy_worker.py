import json
import sys
import time


def main() -> None:
    request = json.loads(sys.stdin.read())

    time.sleep(2)

    result = {
        "status": "ok",
        "action_length": len(request.get("actions", []))
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()