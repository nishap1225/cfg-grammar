#!/usr/bin/env python3
"""
Local evaluation script for CFG Grammar SQL generation.
Expects environment variables: OPENAI_API_KEY and TINYBIRD_TOKEN
"""

import os
import sys
from clients import generate_query, query_db, evaluation


def main():
    """Run local evaluation of CFG SQL generation"""

    # Check for required environment variables
    openai_token = os.getenv("OPENAI_API_KEY")
    tinybird_token = os.getenv("TINYBIRD_TOKEN")

    if not openai_token:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    if not tinybird_token:
        print("❌ Error: TINYBIRD_TOKEN environment variable not set")
        sys.exit(1)

    print("🚀 Initializing clients...")

    # Initialize clients
    try:
        query_generator = generate_query.QueryGenerator(openai_token)
        query_db_client = query_db.QueryDB(tinybird_token)
        evaluator = evaluation.CFGSQLEvaluator(query_generator, query_db_client)
        print("✅ Clients initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing clients: {e}")
        sys.exit(1)

    # Get test cases
    try:
        test_cases = evaluator.test_cases()
    except Exception as e:
        print(f"❌ Error loading test cases: {e}")
        sys.exit(1)

    # Display test cases
    print("\n📝 Test Cases:")
    print("-" * 80)
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case.natural_language}")
        print(f"   Expected columns: {', '.join(case.expected_columns)}")
        print()

    print("🔄 Running evaluation...")
    print("-" * 80)

    # Run evaluation
    try:
        results = evaluator.run_evaluation(test_cases)
        print("✅ Evaluation completed")
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        sys.exit(1)

    # Display results
    print("\n📊 Evaluation Results:")
    print("=" * 80)

    # Overall metrics
    metrics = results["cfg_metrics"]
    print(f"Success Rate:        {metrics['success_rate']:.1%}")
    print(f"Schema Compliance:   {metrics['schema_compliance_rate']:.1%}")
    print(f"Data Accuracy:       {metrics['accuracy_rate']:.1%}")

    print("\n📋 Detailed Results:")
    print("-" * 80)

    # Individual test results
    for i, result in enumerate(results["cfg_results"], 1):
        status_icon = "✅" if result.success else "❌"
        schema_icon = "✅" if result.schema_matches else "❌"
        data_icon = "✅" if result.data_correct else "❌"

        print(f"\nTest {i}: {result.test_case.natural_language}")
        print(f"  Overall: {status_icon}  Schema: {schema_icon}  Data: {data_icon}")

        if result.error_message:
            print(f"  Error: {result.error_message}")

        print(f"  Generated SQL: {result.generated_sql}")

        if result.actual_results is not None and not result.actual_results.empty:
            print(f"  Actual results shape: {result.actual_results.shape}")
            if len(result.actual_results) <= 5:
                print("  Sample results:")
                print(result.actual_results.to_string(index=False))
            else:
                print("  Sample results (first 5 rows):")
                print(result.actual_results.head().to_string(index=False))

    print("\n" + "=" * 80)
    print("🎉 Evaluation complete!")


if __name__ == "__main__":
    main()
