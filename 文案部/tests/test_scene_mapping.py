import asyncio
import sys
import types
import unittest

# Stub optional runtime dependencies to keep unit tests isolated.
dotenv_module = types.ModuleType("dotenv")
dotenv_module.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv_module)

langgraph_module = types.ModuleType("langgraph")
graph_module = types.ModuleType("langgraph.graph")


class DummyStateGraph:
    def __init__(self, *args, **kwargs):
        pass


graph_module.StateGraph = DummyStateGraph
graph_module.END = "END"
langgraph_module.graph = graph_module
sys.modules.setdefault("langgraph", langgraph_module)
sys.modules.setdefault("langgraph.graph", graph_module)

from swarm_with_llm import map_scene_to_keywords_async


class SceneMappingTests(unittest.TestCase):
    def test_empty_scene_fallback(self):
        result = asyncio.run(map_scene_to_keywords_async("", "", ""))
        self.assertEqual(result, "春节返乡")

    def test_keyword_scene_mapping(self):
        result = asyncio.run(
            map_scene_to_keywords_async("过年回家满载而归", "unused", "unused")
        )
        self.assertIn("春节返乡", result)


if __name__ == "__main__":
    unittest.main()
