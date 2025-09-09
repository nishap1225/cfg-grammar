import json
from dataclasses import dataclass
from typing import Set, Dict, Any, Optional, List
from clients import generate_query, query_db
from pandas import DataFrame
from tabulate import tabulate


@dataclass
class TestCase:
    """Represents a single evaluation test case"""

    natural_language: str
    expected_sql: str
    expected_columns: Set[str]
    expected_data: Optional[DataFrame] = None  # Expected results


@dataclass
class EvalResult:
    """Results for a single test case"""

    test_case: TestCase
    generated_sql: str
    success: bool
    schema_matches: bool
    data_correct: bool
    error_message: Optional[str] = None
    actual_results: Optional[List[Dict]] = None


class CFGSQLEvaluator:
    """Evaluates CFG-constrained SQL generation"""

    def __init__(
        self,
        query_generator: generate_query.QueryGenerator,
        query_db_client: query_db.QueryDB,
    ):
        self.query_gen = query_generator
        self.query_db = query_db_client

    def generate_sql(self, natural_language: str) -> str:
        supporting_prompt = f"Generate a query for the Tinybird baby_names dataset for the following request: {natural_language}. Do not impose any constraints beyond what is described in the request."
        query = self.query_gen.generate_query(supporting_prompt)
        return query

    def execute_query(self, sql: str) -> (DataFrame, Exception):
        """Execute SQL query and return results"""
        try:
            result = self.query_db.query_db(sql)
            return result, None
        except Exception as e:
            return None, e

    def check_schema_match(
        self, actual_data: DataFrame, expected_columns: List
    ) -> bool:
        """Check if returned data includes expected columns"""
        return expected_columns.issubset(set(actual_data.columns))

    def check_data_correctness(
        self, actual_data: DataFrame, expected_data: DataFrame
    ) -> bool:
        """Check if actual data includes expected results"""
        for col in expected_data.columns:
            expected_vals = set(
                expected_data[col].dropna().unique()
            )  # Get unique set of non-null values in epxected_data
            actual_vals = set(actual_data[col].dropna().unique())

            # Fail if expected values aren't a subset of actual
            if not expected_vals.issubset(actual_vals):
                return False
        return True

    def evaluate_single_case(
        self, test_case: TestCase
    ) -> EvalResult:  # , use_cfg: bool) -> EvalResult:
        """Evaluate a single test case"""
        # Generate SQL
        generated_sql = self.generate_sql(test_case.natural_language)

        # Execute query
        actual_results, error_message = self.execute_query(generated_sql)

        # Check successful execution
        success = not error_message

        # Check schema match
        schema_matches = False
        if not error_message:
            schema_matches = self.check_schema_match(
                actual_results, test_case.expected_columns
            )

        # Check data correctness
        data_correct = False
        if not error_message and schema_matches:
            data_correct = self.check_data_correctness(
                actual_results, test_case.expected_data
            )

        return EvalResult(
            test_case=test_case,
            generated_sql=generated_sql,
            success=success,
            schema_matches=schema_matches,
            data_correct=data_correct,
            error_message=error_message,
            actual_results=actual_results,
        )

    def run_evaluation(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Run full evaluation suite"""
        cfg_results = []

        for test_case in test_cases:
            cfg_result = self.evaluate_single_case(test_case)  # , use_cfg=True)
            cfg_results.append(cfg_result)

        # Calculate metrics
        def calculate_metrics(results: List[EvalResult]) -> Dict[str, float]:
            total = len(results)
            return {
                "success_rate": sum(r.success for r in results) / total,
                "schema_compliance_rate": sum(r.schema_matches for r in results)
                / total,
                "accuracy_rate": sum(r.data_correct for r in results) / total,
            }

        cfg_metrics = calculate_metrics(cfg_results)

        return {
            "cfg_results": cfg_results,
            "cfg_metrics": cfg_metrics,
        }

    def test_cases(self) -> List[TestCase]:
        """Create test cases"""
        cases = [
            TestCase(
                natural_language="What's the most popular baby name in 2015 for boys?",
                expected_sql="SELECT child_s_first_name FROM baby_names WHERE year_of_birth = 2015 AND gender='MALE' ORDER BY `count` DESC LIMIT 1 FORMAT CSVWithNames",
                expected_columns={"child_s_first_name"},
            ),
            TestCase(
                natural_language="What's the top hispanic name for boys and girls in 2021?",
                expected_sql="SELECT gender, child_s_first_name, count FROM baby_names WHERE year_of_birth = 2021 AND ethnicity = 'HISPANIC' AND rank = 1 FORMAT CSVWithNames",
                expected_columns={"child_s_first_name", "gender"},
            ),
            TestCase(
                natural_language="What are the top 5 girl names in 2012, regardless of ethnicity?",
                expected_sql="SELECT DISTINCT child_s_first_name, count FROM baby_names WHERE year_of_birth = '2012' AND gender = 'FEMALE' ORDER BY count DESC LIMIT 5 FORMAT CSVWithNames",
                expected_columns={"child_s_first_name", "count"},
            ),
            TestCase(
                natural_language="Which year had the highest number of babies named Sophia?",
                expected_sql="SELECT year_of_birth FROM baby_names WHERE child_s_first_name = 'SOPHIA' GROUP BY year_of_birth ORDER BY SUM(count) DESC LIMIT 1 FORMAT CSVWithNames",
                expected_columns={"year_of_birth"},
            ),
            TestCase(
                natural_language="How many children were named Kevin in 2012?",
                expected_sql="SELECT SUM(count) FROM baby_names WHERE child_s_first_name = 'KEVIN' AND year_of_birth = '2012' FORMAT CSVWithNames",
                expected_columns={"SUM(count)"},
            ),
        ]

        for case in cases:
            case.expected_data = self.query_db.query_db(case.expected_sql)

        return cases
