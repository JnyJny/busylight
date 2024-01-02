"""Busylight for Humans™

"""

try:
    from .cli import cli
except ModuleNotFoundError:
    print("Please install the CLI extras, busylight-for-humans[cli]")
    exit(1)


if __name__ == "__main__":
    exit(cli())
