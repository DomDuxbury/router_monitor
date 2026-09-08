from types import SimpleNamespace

import texter.texter as texter_script


def test_texter_main_prints_each_kafka_message(capsys, monkeypatch):
    class FakeKafkaConsumer:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __iter__(self):
            return iter([SimpleNamespace(value=b"hello from kafka")])

    monkeypatch.setattr(texter_script, "KafkaConsumer", FakeKafkaConsumer)

    texter_script.main()

    captured = capsys.readouterr()
    assert "hello from kafka" in captured.out
