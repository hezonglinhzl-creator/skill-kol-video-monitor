import tempfile
import unittest
from pathlib import Path

import main


class MonitorRulesTest(unittest.TestCase):
    def test_failed_view_parse_keeps_previous_views_and_first_seen(self):
        with tempfile.TemporaryDirectory() as tmp:
            original_db = main.DB_PATH
            main.DB_PATH = Path(tmp) / "monitor.sqlite3"
            try:
                conn = main.db()
                try:
                    main.init_db(conn)
                    main.upsert_content(
                        conn,
                        main.ContentRecord(
                            username="creator",
                            profile_url="https://www.instagram.com/creator/",
                            post_url="https://www.instagram.com/reel/ABC123/",
                            shortcode="ABC123",
                            followers=1000,
                            views=500,
                            likes=20,
                            comments=2,
                            view_status="OK",
                        ),
                        checked=True,
                    )
                    first = conn.execute(
                        "SELECT first_seen_at, last_checked_at, views FROM instagram_contents WHERE shortcode = 'ABC123'"
                    ).fetchone()
                    main.upsert_content(
                        conn,
                        main.ContentRecord(
                            username="creator",
                            profile_url="https://www.instagram.com/creator/",
                            post_url="https://www.instagram.com/reel/ABC123/",
                            shortcode="ABC123",
                            followers=1100,
                            views=None,
                            likes=25,
                            comments=3,
                            view_status="PARSE_FAILED",
                        ),
                        checked=True,
                    )
                    second = conn.execute(
                        "SELECT first_seen_at, last_checked_at, views, likes, comments, view_status FROM instagram_contents WHERE shortcode = 'ABC123'"
                    ).fetchone()
                finally:
                    conn.close()
                self.assertEqual(second["first_seen_at"], first["first_seen_at"])
                self.assertEqual(second["views"], 500)
                self.assertEqual(second["likes"], 25)
                self.assertEqual(second["comments"], 3)
                self.assertEqual(second["view_status"], "PARSE_FAILED")
                self.assertGreaterEqual(second["last_checked_at"], first["last_checked_at"])
            finally:
                main.DB_PATH = original_db


if __name__ == "__main__":
    unittest.main()
