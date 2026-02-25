import asyncio
import json
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

import swarm_with_llm as module


class _Counter:
    def __init__(self):
        self.in_flight = 0
        self.max_in_flight = 0


class _FakeResponse:
    def __init__(self, counter, payload):
        self._counter = counter
        self._payload = payload

    async def __aenter__(self):
        self._counter.in_flight += 1
        if self._counter.in_flight > self._counter.max_in_flight:
            self._counter.max_in_flight = self._counter.in_flight
        await asyncio.sleep(0.01)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._counter.in_flight -= 1

    def raise_for_status(self):
        return None

    async def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, counter, payload):
        self._counter = counter
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    def post(self, *args, **kwargs):
        return _FakeResponse(self._counter, self._payload)


class SemaphoreTests(unittest.TestCase):
    def test_call_api_is_bounded_by_semaphore(self):
        counter = _Counter()
        payload = {"choices": [{"message": {"content": "ok"}}]}
        original_client_session = module.aiohttp.ClientSession

        async def _run():
            module._api_semaphore = asyncio.Semaphore(2)
            module.aiohttp.ClientSession = lambda: _FakeSession(counter, payload)
            tasks = [
                module.call_deepseek_api_async("p", "k", "u")
                for _ in range(8)
            ]
            await asyncio.gather(*tasks)

        try:
            asyncio.run(_run())
        finally:
            module.aiohttp.ClientSession = original_client_session
        self.assertLessEqual(counter.max_in_flight, 2)

    def test_reviewer_api_is_bounded_by_semaphore(self):
        counter = _Counter()
        review_obj = {"passed": True, "score": 7, "issues": [], "suggestions": []}
        payload = {"choices": [{"message": {"content": json.dumps(review_obj)}}]}
        original_client_session = module.aiohttp.ClientSession

        async def _run():
            module._api_semaphore = asyncio.Semaphore(2)
            module.aiohttp.ClientSession = lambda: _FakeSession(counter, payload)
            tasks = [
                module.evaluate_content_ai_flavor_async(
                    "文案", {"persona": "宝妈", "selling_point": "空间"}, "k", "u"
                )
                for _ in range(8)
            ]
            await asyncio.gather(*tasks)

        try:
            asyncio.run(_run())
        finally:
            module.aiohttp.ClientSession = original_client_session
        self.assertLessEqual(counter.max_in_flight, 2)


if __name__ == "__main__":
    unittest.main()
