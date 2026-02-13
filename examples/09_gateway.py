"""Phase 7: Submit an evaluation via the FastAPI gateway."""

import httpx

from src.config import GATEWAY_HOST, GATEWAY_PORT

GATEWAY_URL = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"


def main():
    with httpx.Client(timeout=120) as client:
        # Health check
        resp = client.get(f"{GATEWAY_URL}/health")
        print(f"Health: {resp.json()}")

        # Submit evaluation
        idea = (
            "An AI-powered indoor farming platform that optimizes crop yields "
            "using computer vision and IoT sensors. Target market is urban "
            "restaurants wanting hyper-local produce."
        )
        print(f"\nSubmitting: {idea[:60]}...")
        resp = client.post(f"{GATEWAY_URL}/evaluate", json={"idea": idea})
        resp.raise_for_status()
        result = resp.json()

        print(f"\nEvaluation ID: {result['id']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Average Score:  {result['average_score']:.1f}/10")
        for ev in result["evaluations"]:
            print(f"  {ev['agent_name']:>10}: {ev['score']}/10")

        # List all evaluations
        resp = client.get(f"{GATEWAY_URL}/evaluations")
        print(f"\nStored evaluations: {len(resp.json())}")

        # Retrieve by ID
        resp = client.get(f"{GATEWAY_URL}/evaluations/{result['id']}")
        print(f"Retrieved: {resp.json()['id']}")


if __name__ == "__main__":
    main()
