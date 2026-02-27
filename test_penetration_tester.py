import unittest
from unittest.mock import patch

from penetration_tester import PenetrationTester, ResponseSnapshot


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200, url: str = "http://target.local/test"):
        self.text = text
        self.status_code = status_code
        self.url = url


class PenetrationTesterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tester = PenetrationTester(timeout=3)

    def test_detect_reflected_xss(self) -> None:
        payload = "<script>alert(1)</script>"
        response_text = "<html><body>Echo: &lt;script&gt;alert(1)&lt;/script&gt;</body></html>"
        self.assertTrue(self.tester.detect_reflected_xss(response_text, payload))

    def test_compare_baseline_with_response_detects_sql_error(self) -> None:
        baseline_response = FakeResponse("<html>normal</html>", 200)
        baseline = ResponseSnapshot.from_response(baseline_response, response_time=0.15)

        injected_response = FakeResponse(
            "<html>You have an error in your SQL syntax near ''</html>",
            500,
        )
        comparison = self.tester.compare_baseline_with_response(
            baseline=baseline,
            response=injected_response,
            response_time=0.40,
        )

        self.assertTrue(comparison.status_code_changed)
        self.assertTrue(comparison.sql_error_detected)
        self.assertTrue(comparison.hash_changed)

    def test_send_sqli_payloads_marks_likely_sqli(self) -> None:
        baseline_response = FakeResponse("<html>normal catalog page</html>", 200)
        injected_response = FakeResponse(
            "<html>SQLSTATE[42000]: syntax error or access violation</html>",
            500,
        )

        with patch.object(
            PenetrationTester,
            "_send_request",
            side_effect=[
                (baseline_response, 0.10),
                (injected_response, 0.55),
            ],
        ):
            results = self.tester.send_sqli_payloads(
                url="http://target.local/items",
                params={"id": "1"},
                payloads=["' OR 1=1--"],
            )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].parameter, "id")
        self.assertTrue(results[0].likely_sqli)
        self.assertTrue(results[0].comparison.sql_error_detected)

    def test_detect_time_based_blind_sqli(self) -> None:
        normal_response = FakeResponse("<html>ok</html>", 200)

        # retries=2 and one payload => 2 baseline + 2 injected calls.
        with patch.object(
            PenetrationTester,
            "_send_request",
            side_effect=[
                (normal_response, 0.11),
                (normal_response, 0.13),
                (normal_response, 4.20),
                (normal_response, 4.10),
            ],
        ):
            results = self.tester.detect_time_based_blind_sqli(
                url="http://target.local/items",
                params={"id": "1"},
                payloads=["' AND SLEEP(5)--"],
                retries=2,
                min_delay_delta=2.0,
            )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].parameter, "id")
        self.assertTrue(results[0].likely_vulnerable)
        self.assertGreater(results[0].delay_delta, 2.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
