import pytest
from auteur.llm import LLMClient, LLMRequest, LLMResponse
from auteur.llm.fake import FakeClient


def test_fake_client_returns_scripted_responses_in_order():
    scripted = [
        LLMResponse(text="first", input_tokens=10, output_tokens=2),
        LLMResponse(text="second", input_tokens=12, output_tokens=3),
    ]
    client: LLMClient = FakeClient(scripted)

    r1 = client.complete(LLMRequest(system="s", user="u1"))
    r2 = client.complete(LLMRequest(system="s", user="u2"))

    assert r1.text == "first"
    assert r2.text == "second"


def test_fake_client_raises_when_exhausted():
    client = FakeClient([LLMResponse(text="only", input_tokens=1, output_tokens=1)])
    client.complete(LLMRequest(system="s", user="u"))

    with pytest.raises(RuntimeError, match="FakeClient exhausted"):
        client.complete(LLMRequest(system="s", user="u"))


def test_fake_client_records_calls():
    client = FakeClient([LLMResponse(text="x", input_tokens=1, output_tokens=1)])
    client.complete(LLMRequest(system="sys", user="usr", temperature=0.1))

    assert len(client.calls) == 1
    assert client.calls[0].system == "sys"
    assert client.calls[0].user == "usr"
    assert client.calls[0].temperature == 0.1
