"""Phase 10: Demonstrate PII sanitization and output secret filtering.

Shows regex-based PII redaction and secret-leak detection.
These complement the LlamaStack shields (which classify but don't redact).
"""

from src.security.sanitizer import sanitize
from src.security.output_filter import scan_output


def main():
    # Test 1: PII sanitization
    print("TEST 1: PII Sanitization")
    print("=" * 60)
    text_with_pii = (
        "Our CEO John can be reached at john.doe@startup.com or "
        "call 555-123-4567. His SSN is 123-45-6789. "
        "Payment card: 4111 1111 1111 1111. "
        "Server at 10.0.1.42."
    )
    print(f"Input:  {text_with_pii}")
    result = sanitize(text_with_pii)
    print(f"Output: {result.sanitized}")
    print(f"Redactions ({len(result.redactions)}):")
    for r in result.redactions:
        print(f"  {r['type']:>12}: {r['matched']}")

    # Test 2: Output secret filtering
    print(f"\n{'=' * 60}")
    print("TEST 2: Output Secret Filtering")
    print("=" * 60)

    clean_output = "The startup has strong market potential with 60% margins."
    result = scan_output(clean_output)
    print(f"Clean text: passed={result.passed}")

    # Build test strings at runtime to avoid triggering GitHub secret scanning
    fake_key = "api_key=" + "fake_test_key_" + "x" * 20
    output_with_secret = f"Analysis complete. Note: {fake_key} was found in the configuration."
    result = scan_output(output_with_secret)
    print(f"With secret: passed={result.passed}")
    for d in result.detections:
        print(f"  Detected: {d['type']} at position {d['position']}")

    # AWS key pattern: AKIA + 16 alphanumeric chars
    fake_aws = "AKIA" + "X" * 16
    output_with_key = f"Deploy using {fake_aws} credentials."
    result = scan_output(output_with_key)
    print(f"With AWS key: passed={result.passed}")
    for d in result.detections:
        print(f"  Detected: {d['type']} at position {d['position']}")


if __name__ == "__main__":
    main()
