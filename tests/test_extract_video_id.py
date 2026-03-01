import unittest

from app.youtube_comments import InvalidVideoError, extract_video_id


class ExtractVideoIdTests(unittest.TestCase):
    def test_extract_from_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_from_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_extract_from_shorts_url(self):
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        self.assertEqual(extract_video_id(url), "dQw4w9WgXcQ")

    def test_raises_for_invalid_url(self):
        with self.assertRaises(InvalidVideoError):
            extract_video_id("https://example.com/video")


if __name__ == "__main__":
    unittest.main()
