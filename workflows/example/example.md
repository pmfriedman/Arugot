# Example Workflow

## Purpose
Demonstrates the basic workflow contract by incrementing a counter.

## How It Works
- Reads `count` from persisted state
- Increments it by 1
- Returns updated state for persistence

## Inbox Integration
None - this is a minimal example showing state persistence.

## Usage
```sh
uv run python main.py run example
```

Run multiple times to see the counter increment with each run.
