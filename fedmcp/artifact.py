from jwcrypto import jwk, jws
import json, datetime
from typing import TypedDict, Any

class Artifact(TypedDict):
    id: str
    type: str
    version: int
    workspaceId: str
    createdAt: str
    jsonBody: Any

def sign_artifact(art: Artifact, pem_private: str, kid: str = "workspace-root") -> str:
    key = jwk.JWK.from_pem(pem_private.encode())
    key.update(kid=kid, alg="ES256")
    token = jws.JWS(json.dumps(art).encode())
    token.add_signature(key, protected={"alg": "ES256", "typ": "JWT", "kid": kid})
    return token.serialize(compact=True)

def verify_artifact(jws_compact: str, pem_public: str, expected_workspace: str) -> Artifact:
    key = jwk.JWK.from_pem(pem_public.encode())
    token = jws.JWS()
    token.deserialize(jws_compact)
    token.verify(key)
    art: Artifact = json.loads(token.payload)
    if art["workspaceId"] != expected_workspace:
        raise ValueError("workspaceId mismatch")
    return art