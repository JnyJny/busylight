"""HTTP API server for BusyLight."""

from os import environ

import typer
from loguru import logger

try:
    import uvicorn
except ImportError as error:
    raise ImportError(
        "The package `uvicorn` is missing, unable to serve the busylight API. "
        "Install with webapi extras: pip install busylight-for-humans[webapi]"
    ) from None

from busylight.api.logging_config import get_uvicorn_log_config

busyserve_cli = typer.Typer()


@busyserve_cli.command(name="serve")
def serve_http_api(
    debug: bool = typer.Option(False, "--debug", "-D"),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host name to bind the server to.",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Network port number to listen on.",
    ),
) -> None:
    """Serve HTTP API to access available lights."""

    environ["BUSYLIGHT_DEBUG"] = str(debug)

    try:
        log_config = get_uvicorn_log_config(debug=debug)

        uvicorn.run(
            "busylight.api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_config=log_config,
        )
    except ModuleNotFoundError as error:
        logger.error(f"Failed to start webapi: {error}")
        typer.secho(
            "Failed to start the webapi.",
            fg="red",
        )
        raise typer.Exit(code=1) from None
