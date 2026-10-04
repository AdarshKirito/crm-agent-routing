import json

import numpy as np


def test_router_reads_every_example_file_in_order(tmp_path, monkeypatch):
    from app import router as R

    first, second = tmp_path / "pro.jsonl", tmp_path / "new_org.jsonl"
    first.write_text(json.dumps({"org": "b2b", "task": "handle_time", "idx": 1, "text": "x"}) + "\n", encoding="utf-8")
    second.write_text(json.dumps({"org": "original", "task": "case_routing", "idx": 2, "text": "y"}) + "\n",
                      encoding="utf-8")

    class FakeEmbedder:
        def passage_embed(self, texts):
            return [np.arange(1, 5, dtype=np.float32) * (i + 1) for i, _ in enumerate(texts)]

    router = R.TaskRouter([first, second], cache_dir=tmp_path / "cache")
    monkeypatch.setattr(router, "_embedder", lambda: FakeEmbedder())
    router._load()
    assert router._labels == ["handle_time", "case_routing"]
    assert router._matrix.shape == (2, 4)


def test_example_paths_are_relative_to_the_data_dir_unless_absolute(tmp_path):
    from app import router as R

    assert R.example_paths("router_examples.jsonl") == [R.DATA_DIR / "router_examples.jsonl"]
    assert R.example_paths(" router_examples.jsonl, router_examples_original.jsonl ")[1] == \
        R.DATA_DIR / "router_examples_original.jsonl"
    absolute = tmp_path / "x.jsonl"
    assert R.example_paths(str(absolute)) == [absolute]
