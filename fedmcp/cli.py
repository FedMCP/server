import json, typer
from pathlib import Path
from .artifact import sign_artifact

app = typer.Typer(no_args_is_help=True, help="FedMCP reference CLI")

@app.command()
def sign(
    artifact: Path = typer.Argument(..., help="Artifact JSON file"),
    key: Path = typer.Argument(..., help="PEM private key"),
    kid: str = typer.Option("workspace-root", help="JWS key ID"),
):
    art = json.loads(artifact.read_text())
    pem = key.read_text()
    token = sign_artifact(art, pem, kid)
    typer.echo(token)

def main():
    app()

if __name__ == "__main__":
    main()