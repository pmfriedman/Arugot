# Extract GitHub PR

⚠️ **STATUS: SUPERSEDED - No Longer Needed**

This workflow has been superseded by improvements to the `github_pr` (formerly `ingest_github_pr`) workflow. The functionality of creating stubs and tracking action signal changes is now handled directly in the ingest workflow using state tracking, eliminating the need for an intermediate stub layer.

---

Processes GitHub PR data from `_ingest/` and creates structured notes in `_scratch/auto/`.

## Why Superseded

The original architecture had two workflows:
1. **Ingest** - Fetch PRs, write to `_ingest/github_pr/`
2. **Extract** - Read from `_ingest/`, create "stubs" in `_scratch/auto/github/` with state tracking

**New approach:** The `github_pr` workflow now:
- Fetches PRs and writes to `github/prs/`
- Tracks action signal state (action_type, last_actor, last_event_at) per PR
- Creates Inbox notifications only when action signals change
- No intermediate stub files needed
- State persisted as `{"prs": {"owner/repo/number": {...}}}`

This aligns with the Inbox pattern's philosophy of simplicity and letting patterns emerge organically. The state tracking eliminates notification spam while keeping a single workflow responsible for both fetching and notification.

This workflow represents premature automation. According to the new philosophy:
- PR data should be processed manually first
- Automation should only be added when pain points become clear
- Processing could be manual, Copilot-assisted in VS Code, or eventually automated

**Recommendation:** Keep dormant or delete. Start by manually processing PR data from Inbox notifications instead.

## Original Usage

```sh
uv run python main.py run extract_github_pr
```
