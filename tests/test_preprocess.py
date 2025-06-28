import json
import io
import builtins

from scripts import preprocess


def test_preprocess_creates_index(tmp_path, monkeypatch):
    # Sample poem consisting of two lines
    sample_data = [
        {"paragraphs": ["春眠不觉晓", "处处闻啼鸟"]}
    ]
    json_str = json.dumps(sample_data, ensure_ascii=False)

    # Mock glob.glob to return a single fake JSON file path
    def fake_glob(pattern, recursive=True):
        return ["dummy.json"]

    monkeypatch.setattr(preprocess.glob, "glob", fake_glob)

    # Monkeypatch open so that reading the fake JSON file returns our sample
    real_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if path == "dummy.json":
            return io.StringIO(json_str)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    preprocess.main.callback(data_dir=str(tmp_path / "data"), index_dir=str(tmp_path))

    index_file = tmp_path / "char_index.json"
    with open(index_file, "r", encoding="utf-8") as fh:
        index = json.load(fh)

    assert index["春"][0]["tone"] == 1
    assert index["处"][0]["pos"] == 1
    assert index["处"][1]["pos"] == 2
    assert index["鸟"][0]["tone"] == 3
