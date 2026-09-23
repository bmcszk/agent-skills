---
name: mcpc
description: 'Use mcpc CLI to interact with MCP servers — call tools, read resources, manage sessions. Load this when you need to access any MCP server via the command line. Configured servers: context7, pixellab, MiniMax, zai-search, zai-reader, zread, zai-vision, gemini-cli, playwright, searxng. Keywords: mcpc, mcp client, model context protocol, mcp server, call tool, read resource, mcp session.'
metadata:
  audience: developers
  workflow: infrastructure
  category: mcp-client
  technologies: mcp, mcpc, cli
---

# mcpc: MCP command-line client

Use `mcpc` to interact with MCP (Model Context Protocol) servers from the command line. Generate shell commands instead of using function calling — more efficient, composable with pipes, and works across all agent types.

## Configured servers

MCP servers are defined in `~/.mcpc/mcp.json`. Connect via `file:entry` syntax:

```bash
mcpc connect ~/.mcpc/mcp.json:<entry> @<name>
```

**Available servers:** context7, pixellab, MiniMax, gemini-cli, playwright, searxng, plus Z.ai coding-plan servers (added 2026-09-16, key = ZAI_AUTH_TOKEN from ~/.config/environment.d/secrets.conf):

| Session | Entry | Tools | Notes |
|---|---|---|---|
| `@zai-search` | `zai-web-search` | `web_search_prime` | remote, live-verified |
| `@zai-reader` | `zai-web-reader` | `webReader` | remote, live-verified |
| `@zread` | `zread` | `search_doc`, `read_file`, `get_repo_structure` | remote; repo_name = owner/repo |
| `@zai-vision` | `zai-vision` | `analyze_image`, `ui_to_artifact`, OCR, … | stdio npx @z_ai/mcp-server; **local file paths only** — URL fetch fails (400 图片输入格式/解析错误); Node ≥22 |
| `@minimax` | `MiniMax` | `web_search`, `understand_image` | uvx minimax-coding-plan-mcp, key = MINIMAX_CODING_KEY; local paths verified; search verified |

Not configured (pay-per-use platform API, NOT covered by coding plans): official generative MiniMax-MCP (uvx minimax-mcp: TTS/video/image/music). Only add on explicit user request.

**PATH pitfall:** `mcpc` binary lives in `~/.bun/bin` — absent from default non-login PATH. First line of any script: `export PATH="$HOME/.bun/bin:$PATH"` (else `command not found`, exit 127).

**Verified quirks (2026-09-16):** Z.ai/zread remote tools take `owner/repo` as `repo_name`; vision tools reject remote image URLs (HTTP 400 图片输入格式/解析错误) — download or generate a local file first (local paths verified OK on both @zai-vision and @minimax).

## Quick reference

```bash
# List sessions and auth profiles
mcpc

# Show server info, capabilities, tools
mcpc @<session>

# Tools
mcpc @<session> tools-list
mcpc @<session> tools-list --full
mcpc @<session> tools-get <tool-name>
mcpc @<session> tools-call <tool-name> key:=value key2:="string value"

# Resources
mcpc @<session> resources-list
mcpc @<session> resources-read <uri>

# Prompts
mcpc @<session> prompts-list
mcpc @<session> prompts-get <prompt-name> arg1:=value1

# Async tasks
mcpc @<session> tools-call <tool> args --task
mcpc @<session> tools-call <tool> args --detach
mcpc @<session> tasks-list
mcpc @<session> tasks-result <taskId>

# Sessions
mcpc connect <server> @<name>
mcpc @<name> restart
mcpc @<name> close

# Search tools across sessions
mcpc grep <pattern>
mcpc @<name> grep <pattern>

# Authentication
mcpc login <server>
mcpc logout <server>
```

## Connecting to servers

```bash
# From config file (preferred for local setup)
mcpc connect ~/.mcpc/mcp.json:playwright @pw

# Direct URL (remote servers)
mcpc connect mcp.apify.com @apify

# With bearer token
mcpc connect mcp.example.com @api --header "Authorization: Bearer $TOKEN"

# With OAuth profile
mcpc login mcp.example.com --profile work
mcpc connect mcp.example.com @api-work --profile work
```

## Passing arguments

Arguments use `key:=value` syntax. Values are auto-parsed as JSON when valid:

```bash
# String values
mcpc @s tools-call search query:="hello world"

# Numbers, booleans (auto-parsed as JSON)
mcpc @s tools-call search limit:=10 enabled:=true

# Complex JSON values
mcpc @s tools-call search config:='{"nested":"value"}' items:='[1,2,3]'

# Force string type with inner JSON quotes
mcpc @s tools-call search id:='"123"'

# Inline JSON object (if first arg starts with { or [)
mcpc @s tools-call search '{"query":"hello","limit":10}'

# From stdin (auto-detected when piped)
echo '{"query":"hello"}' | mcpc @s tools-call search
```

**Pitfall:** No spaces around `:=`. Use quotes for values with spaces:
```bash
mcpc @s tools-call search "query:=hello world"
```

## JSON output for scripting

Use `--json` for machine-readable output. JSON follows the MCP specification:

```bash
# Get tools as JSON
mcpc --json @s tools-list

# Call tool and extract result with jq
mcpc --json @s tools-call search query:="test" | jq '.content[0].text'

# Chain tools across sessions
mcpc --json @s1 tools-call get-data | mcpc @s2 tools-call process

# Batch operations
for tool in $(mcpc --json @s tools-list | jq -r '.[].name'); do
  mcpc --json @s tools-get "$tool" > "schemas/$tool.json"
done
```

## Session management

Sessions are persistent named connections that maintain state. More efficient than reconnecting every command.

**Session states:**

| State | Meaning |
|-------|---------|
| live | Bridge running, server responding |
| connecting | Initial connection in progress |
| disconnected | Server unreachable, auto-recovers |
| crashed | Bridge crashed, auto-restarts |
| unauthorized | Auth failed, needs `login` then `restart` |
| expired | Server rejected session, needs `restart` |

**Lifecycle:**
```bash
mcpc connect ~/.mcpc/mcp.json:searxng @searxng    # Create
mcpc @searxng tools-call searxng_web_search query:="Go generics"  # Use
mcpc @searxng ping                                   # Health check
mcpc @searxng restart                                # Restart if stale
mcpc @searxng close                                  # Clean up
```

## Schema validation

Validate tool schemas against snapshots to detect breaking changes:

```bash
# Save expected schema
mcpc --json @s tools-get search > expected.json

# Validate before calling
mcpc @s tools-call search --schema expected.json query:="test"
```

## Proxy for sandboxed access

Expose MCP sessions without revealing credentials:

```bash
mcpc connect mcp.example.com @relay --proxy 8080 --profile ai-access
# Others connect to localhost:8080 with no access to original tokens
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Client error (invalid arguments) |
| 2 | Server error (tool execution failed) |
| 3 | Network error (connection/timeout) |
| 4 | Authentication error |

## Debugging

```bash
mcpc --verbose @s tools-call my-tool           # Protocol details to stderr
mcpc tail_log @s                                # View bridge logs
cat ~/.mcpc/logs/bridge-@<session>.log          # Read log file
```

## Related skills

Each MCP server has its own skill with tool-specific workflows:

- `context7` — Documentation lookup
- `pixellab` — Pixel art generation
- `minimax` — AI web search and image understanding
- `gemini` — Google Gemini AI assistant
- `playwright-mcp` — Browser automation
- `searxng` — Web search and URL reading
