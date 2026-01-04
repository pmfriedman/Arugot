# Extract Meetings

⚠️ **STATUS: DEPRECATED - On Pause**

This workflow is partially implemented but put on pause. It represents premature automation and is left here as reference code. The workflow is not registered and cannot be called.

---

Processes meeting transcripts from `_ingest/` and creates structured notes in `_scratch/auto/`.

## Why Deprecated

**Premature automation** - According to the new Inbox philosophy:

This workflow represents premature automation. According to the new philosophy:
- Meeting notes should be processed manually first
- Automation should only be added when pain points become clear
- Processing could be manual, Copilot-assisted in VS Code, or eventually automated

**Recommendation:** Keep dormant or delete. Start by manually processing meeting notes from Inbox notifications instead.

## Original Usage

```sh
uv run python main.py run extract_meetings
```
