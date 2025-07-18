from fedmcp.artifact import sign_artifact, verify_artifact
import json, pathlib

priv = pathlib.Path("tests/priv.pem").read_text()
pub = pathlib.Path("tests/pub.pem").read_text()
art = json.loads(pathlib.Path("tests/example.json").read_text())

def test_roundtrip():
    jws = sign_artifact(art, priv, "kid-1")
    verified = verify_artifact(jws, pub, "workspace-1")
    assert verified["id"] == art["id"]