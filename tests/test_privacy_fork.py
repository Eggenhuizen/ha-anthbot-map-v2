"""Behavioral checks for the privacy fork's disabled announcement network path."""
import ast
import asyncio
import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PrivacyForkTests(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_never_acquires_a_network_session(self):
        source = (ROOT / "custom_components/anthbot_map/announcements.py").read_text()
        tree = ast.parse(source)
        method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                      for node in cls.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_refresh")
        def forbidden(*args, **kwargs):
            self.fail("Offline news must not create a network session")
        stamp = datetime.datetime(2026, 11, 1, tzinfo=datetime.timezone.utc)
        namespace = {"async_get_clientsession": forbidden, "_utcnow": lambda: stamp}
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(ROOT), "exec"), namespace)
        store = SimpleNamespace(lock=asyncio.Lock(), items=[{"title": "cached upstream message"}], fetched_at=None)
        await namespace["async_refresh"](store, "nl")
        self.assertEqual(store.items, [])
        self.assertEqual(store.fetched_at, stamp)

if __name__ == "__main__":
    unittest.main()
