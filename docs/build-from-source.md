# Running from Source

Run the `remarkable-mcp` server from a local clone instead of the published package. Useful for development, testing changes, or running a fork.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A reMarkable tablet or cloud account

## 1. Clone and install

```bash
git clone https://github.com/SamMorrowDrums/remarkable-mcp.git
cd remarkable-mcp
uv sync --all-extras
```

## 2. Configure environment

Create a `.env` file in the project root with your credentials:

```bash
# Required for cloud mode
REMARKABLE_TOKEN=your-cloud-token

# Optional: handwriting OCR
GOOGLE_VISION_API_KEY=your-api-key
REMARKABLE_OCR_BACKEND=google
```

To get a cloud token, run:

```bash
uv run remarkable-mcp --register YOUR_ONE_TIME_CODE
```

Get a one-time code from [my.remarkable.com/device/desktop/connect](https://my.remarkable.com/device/desktop/connect).

## 3. Verify the build

```bash
uv run pytest test_server.py -v
```

All tests should pass. To also run live integration tests against the real cloud API (requires `.env` credentials):

```bash
set -a && source .env && set +a
uv run pytest test_server.py -v -m remarkable_live
```

## 4. Configure your MCP client

Point your MCP client configuration to the local clone using `uv --directory` to ensure the correct virtualenv is used.

### Cloud mode (default)

```json
{
  "servers": {
    "remarkable": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/remarkable-mcp", "run", "remarkable-mcp"],
      "env": {
        "REMARKABLE_TOKEN": "your-cloud-token",
        "GOOGLE_VISION_API_KEY": "your-api-key"
      }
    }
  }
}
```

### USB Web mode

```json
{
  "servers": {
    "remarkable": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/remarkable-mcp", "run", "remarkable-mcp", "--usb"],
      "env": {
        "GOOGLE_VISION_API_KEY": "your-api-key"
      }
    }
  }
}
```

### SSH mode

```json
{
  "servers": {
    "remarkable": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/remarkable-mcp", "run", "remarkable-mcp", "--ssh"],
      "env": {
        "GOOGLE_VISION_API_KEY": "your-api-key"
      }
    }
  }
}
```

Replace `/absolute/path/to/remarkable-mcp` with the actual path to your clone.

## How it works

The `uv --directory` flag tells `uv` to use the project at that path, including its virtualenv and dependencies. The `run remarkable-mcp` part executes the CLI entry point defined in `pyproject.toml` (`remarkable_mcp.cli:main`).

This is equivalent to running `uvx remarkable-mcp` with the published package, but uses your local source instead.

## Cloud mode performance

In cloud mode, the server uses a shared in-memory cache for document metadata. A background loader populates the cache at startup using parallel HTTP requests (10 concurrent workers). Tools read from this cache instead of making individual API calls, so responses are fast after the initial load.

The cache refreshes every 5 minutes. If a refresh fails, the server returns the last known good data — so tools stay responsive even during transient network issues. See the [README](../README.md#cloud-mode-architecture) for more detail.

## Troubleshooting

**`uv` not found**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

**Token expired**: Cloud tokens expire periodically. Re-register with `uv run remarkable-mcp --register NEW_CODE`.

**USB Web not connecting**: Make sure your tablet is connected via USB, unlocked, and has the web interface enabled in **Settings → Storage**.

**Tests fail**: Run `uv sync --all-extras` to ensure all dependencies are installed. Check Python version is 3.10+.

For more on development and contributing, see the [Development Guide](development.md).
