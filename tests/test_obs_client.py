import builtins

import pytest

from obs_autoclip.obs_client import ObsDependencyError, ObsWebSocketClient


def test_missing_obsws_dependency_has_actionable_message(monkeypatch) -> None:
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "obsws_python":
            raise ModuleNotFoundError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    client = ObsWebSocketClient("localhost", 4455, None)

    with pytest.raises(ObsDependencyError, match="python -m pip install -e"):
        client.connect()
