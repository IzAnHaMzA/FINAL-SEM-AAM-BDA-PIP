import unittest

from app import ALL_QUESTIONS, ML_MUST_STUDY, ML_UNITS, PIP_UNITS, SUBJECTS, app, evaluate_answer


class StudyAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_homepage_loads(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Study Dashboard", response.data)
        self.assertIn(b"AAM", response.data)
        self.assertIn(b"PIP", response.data)
        self.assertIn(b"BDA", response.data)

    def test_subject_page_loads(self) -> None:
        response = self.client.get("/subject/pip")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PIP Unit-Wise Marks", response.data)
        self.assertIn(b"Histogram &amp; Histogram Equalization", response.data)

    def test_tasks_page_loads(self) -> None:
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Weekly Task Tracker", response.data)
        self.assertIn(b"typed 5 times and read 7 times", response.data.lower())

    def test_bda_subject_page_loads(self) -> None:
        response = self.client.get("/subject/bda")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BDA Unit-Wise Marks", response.data)
        self.assertIn(b"What is Hadoop", response.data)

    def test_aam_subject_page_loads(self) -> None:
        response = self.client.get("/subject/aam")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AAM", response.data)
        self.assertIn(b"Explain Support Vector Machines. Explain the working, types and Python code", response.data)

    def test_unit_page_loads(self) -> None:
        response = self.client.get("/subject/pip/unit/2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image Enhancement", response.data)
        self.assertIn(b"Histogram and Histogram Equalization", response.data)
        self.assertIn(b"Diagram Space", response.data)

    def test_legacy_unit_route_redirects_to_ml(self) -> None:
        response = self.client.get("/unit/4", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/subject/aam/unit/4", response.headers["Location"])

    def test_legacy_ml_routes_redirect_to_aam(self) -> None:
        subject_response = self.client.get("/subject/ml", follow_redirects=False)
        unit_response = self.client.get("/subject/ml/unit/4", follow_redirects=False)
        self.assertEqual(subject_response.status_code, 302)
        self.assertEqual(unit_response.status_code, 302)
        self.assertIn("/subject/aam", subject_response.headers["Location"])
        self.assertIn("/subject/aam/unit/4", unit_response.headers["Location"])

    def test_units_and_must_study_counts(self) -> None:
        self.assertEqual(len(ML_UNITS), 5)
        self.assertEqual(len(PIP_UNITS), 5)
        self.assertEqual(len(ML_MUST_STUDY), 10)
        self.assertEqual(len(SUBJECTS), 3)
        self.assertIn("aam", SUBJECTS)
        self.assertIn("bda", SUBJECTS)
        self.assertEqual(len(ALL_QUESTIONS), 82)
        self.assertEqual(ALL_QUESTIONS[14]["question"], "Explain Support Vector Machines. Explain the working, types and Python code")

    def test_bda_has_full_26_questions(self) -> None:
        bda_questions = [question for question in ALL_QUESTIONS if question["id"] >= 201]
        self.assertEqual(len(bda_questions), 26)

    def test_every_question_has_five_examples(self) -> None:
        self.assertTrue(all(len(question["examples"]) == 5 for question in ALL_QUESTIONS))

    def test_important_questions_have_four_extra_points(self) -> None:
        important_standard = [
            question for question in ALL_QUESTIONS
            if question.get("star") and question["type"] == "standard" and question["id"] < 100
        ]
        self.assertTrue(all(len(question["points"]) == 8 for question in important_standard))

    def test_evaluate_standard_answer(self) -> None:
        question = ALL_QUESTIONS[0]
        result = evaluate_answer(
            question,
            "Machine learning model is program that learns patterns from data to make predictions. "
            "It identifies patterns from historical data predicts future values or classifications "
            "improves performance with more data reduces manual effort and time. Prediction.",
        )
        self.assertGreaterEqual(result["score"], 80)

    def test_evaluate_difference_answer(self) -> None:
        question = next(item for item in ALL_QUESTIONS if item["id"] == 26)
        result = evaluate_answer(question, "Output smooth but blurry and sharp realistic. Training stable and difficult.")
        self.assertGreater(len(result["missed_differences"]), 0)

    def test_bda_question_has_detailed_definition(self) -> None:
        question = next(item for item in ALL_QUESTIONS if item["id"] == 205)
        self.assertIn("distributed storage", question["definition"].lower())
        self.assertEqual(len(question["examples"]), 5)

    def test_missing_unit_returns_404(self) -> None:
        response = self.client.get("/subject/aam/unit/99")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
