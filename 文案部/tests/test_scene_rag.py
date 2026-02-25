import unittest

from scene_rag import SceneRetriever


class SceneRagTests(unittest.TestCase):
    def test_retrieve_known_scene(self):
        retriever = SceneRetriever(
            scene_library_path="02-参考学习/03-Writer材料/内容变量库/场景切入库.md",
            top_k=3,
            min_score=0.15,
            default_scene="春节返乡",
        )
        result = retriever.retrieve("过年回家满载而归")
        self.assertIn("scene_type", result)
        self.assertIn("keywords", result)
        self.assertIn("evidence", result)
        self.assertIn("score", result)
        self.assertIn("fallback_used", result)
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["scene_type"], "春节返乡")

    def test_missing_library_fallback(self):
        retriever = SceneRetriever(
            scene_library_path="/tmp/not-exist-scene-lib.md",
            top_k=3,
            min_score=0.15,
            default_scene="春节返乡",
        )
        result = retriever.retrieve("过年回家")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["scene_type"], "春节返乡")

    def test_low_score_fallback(self):
        retriever = SceneRetriever(
            scene_library_path="02-参考学习/03-Writer材料/内容变量库/场景切入库.md",
            top_k=3,
            min_score=0.4,
            default_scene="春节返乡",
        )
        result = retriever.retrieve("火星基地能源补给站")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["scene_type"], "春节返乡")


if __name__ == "__main__":
    unittest.main()
