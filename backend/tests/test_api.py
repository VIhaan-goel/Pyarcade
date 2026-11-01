"""Run from the backend folder:   python -m unittest discover -s tests -t .

Uses a fake game process, so pygame is not needed to test the API."""
import os
import time
import unittest

os.environ["RUNNER_PATH"] = os.path.join(os.path.dirname(__file__), "fake_runner.py")
os.environ["MAX_SESSIONS"] = "2"

from app import create_app  # noqa: E402
from services.session_manager import manager  # noqa: E402


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def tearDown(self):
        for sid in list(manager._sessions):
            manager.stop(sid)

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_games_list_and_detail(self):
        games = self.client.get("/api/games").get_json()
        self.assertEqual(len(games), 6)
        self.assertNotIn("file", games[0])
        self.assertEqual(self.client.get("/api/games/snake").status_code, 200)
        self.assertEqual(self.client.get("/api/games/nope").status_code, 404)

    def test_unknown_game_rejected(self):
        r = self.client.post("/api/sessions", json={"game_id": "../../etc/passwd"})
        self.assertEqual(r.status_code, 400)

    def test_session_lifecycle_and_input(self):
        r = self.client.post("/api/sessions", json={"game_id": "snake"})
        self.assertEqual(r.status_code, 201)
        sid = r.get_json()["session_id"]

        self.assertTrue(self.client.get(f"/api/sessions/{sid}").get_json()["running"])

        bad = self.client.post(f"/api/sessions/{sid}/input", json={"events": [{"type": "evil"}]})
        self.assertEqual(bad.status_code, 400)

        ok = self.client.post(f"/api/sessions/{sid}/input",
                              json={"events": [{"type": "keydown", "code": "ArrowLeft"}]})
        self.assertEqual(ok.status_code, 202)

        # The stream must contain frames and our echoed input
        stream = self.client.get(f"/api/sessions/{sid}/stream")
        self.assertIn("multipart/x-mixed-replace", stream.content_type)
        seen = b""
        deadline = time.time() + 5
        for chunk in stream.response:
            seen += chunk
            if b"ECHO:" in seen or time.time() > deadline:
                break
        stream.response.close()
        self.assertIn(b"image/jpeg", seen)
        self.assertIn(b"ArrowLeft", seen)

        self.assertEqual(self.client.delete(f"/api/sessions/{sid}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/sessions/{sid}").status_code, 404)

    def test_capacity_limit(self):
        for _ in range(2):
            self.assertEqual(self.client.post("/api/sessions", json={"game_id": "dino"}).status_code, 201)
        self.assertEqual(self.client.post("/api/sessions", json={"game_id": "dino"}).status_code, 503)

    def test_root_and_unknown_route(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/api/unknown").status_code, 404)


if __name__ == "__main__":
    unittest.main()
