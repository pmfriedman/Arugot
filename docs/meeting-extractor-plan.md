# Meeting Extractor Implementation Plan

## Overview
The Meeting Extractor is a schedule-driven, idempotent control-plane workflow that ensures every ingested meeting transcript has exactly one corresponding machine-owned working document. It operates as a filesystem reconciler, not an analyzer.

**Key Principle:** Extractor state is implicit via file existence—no global registry or database required.

## Goal
Ensure that every meeting transcript in `_ingest/fireflies/` has a corresponding machine-owned record in `_working/auto/meetings/`.

## Responsibilities
- ✅ Detect new meeting transcripts in `_ingest/fireflies/`
- ✅ Create machine-owned meeting records in `_working/auto/meetings/`
- ✅ Maintain extractor state implicitly via file existence
- ✅ Be safe to run repeatedly on a schedule (idempotent)

## Non-Responsibilities
- ❌ No LLM usage
- ❌ No summarization or synthesis
- ❌ No reading or writing curated notes
- ❌ No workflow state transitions beyond creation
- ❌ No dependence on human notes

## Inputs & Outputs

### Inputs
- Files in `_ingest/fireflies/` representing meeting transcripts from Fireflies.ai
- Each transcript must have (or allow derivation of) a stable meeting ID

### Outputs
For each transcript missing a meeting record, create:
```
_working/auto/meetings/<meeting-id>.md
```

**Frontmatter (machine-owned):**
```yaml
---
workflow: meeting
state: unprocessed
created_by: meeting-extractor
created_at: <ISO timestamp>
---
```

**Body (canonical structure):**
```markdown
# Meeting

Source:
- Transcript: [[_ingest/fireflies/<filename>.md]]

This file is machine-owned.
```

## Algorithm (Idempotent Reconciliation)

On each scheduled run:
1. Enumerate candidate meeting transcripts in `_ingest/fireflies/`
2. For each transcript:
   - Derive a deterministic `meeting_id`
   - Check for existing file in `_working/auto/meetings/` corresponding to that meeting
   - If meeting file exists → do nothing
   - If missing → create it with `state: unprocessed`

## Invariants
- Exactly one meeting record per transcript
- Extractor may create, but never modify or delete meeting records
- Safe to re-run at any time
- Deleting a meeting record causes it to be recreated on the next run

## Building Blocks

### Block 1: Workflow Module Structure
**Goal:** Set up the basic workflow structure following the project's conventions

**Implementation Steps:**
- [x] 1. Create `workflows/meeting_extractor/` directory
- [x] 2. Create `workflows/meeting_extractor/__init__.py`
- [x] 3. Create `workflows/meeting_extractor/workflow.py` with stub `run(context, state)` function
- [x] 4. Add module-level docstring explaining purpose
- [x] 5. Verify workflow is discoverable via `uv run python main.py list`

---

### Block 2: Ingest File Scanner
**Goal:** Enumerate meeting transcripts in `_ingest/fireflies/`

**Implementation Steps:**
- [x] 1. Create `workflows/meeting_extractor/scanner.py`
- [x] 2. Implement `list_ingest_files(ingest_dir: Path) -> list[Path]`
   - Scan for `.md` files in the directory
   - All markdown files in `_ingest/fireflies/` are considered meeting transcripts
- [x] 3. Add logging for discovery results
- [x] 4. Add unit tests (can be deferred to later block if preferred)

---

### Block 3: Meeting ID Derivation
**Goal:** Generate stable, deterministic meeting IDs from ingest files

**Implementation Steps:**
- [x] 1. Create `workflows/meeting_extractor/meeting_id.py`
- [x] 2. Implement `derive_meeting_id(ingest_file: Path) -> str`
   - **v1 Strategy:** Use filename stem (without extension)
   - Sanitize for filesystem safety (lowercase, replace spaces with hyphens)
- [x] 3. Document assumptions about filename stability
- [x] 4. Add validation: raise error if ID would be invalid filename
- [x] 5. Add unit tests with various filename examples

---

### Block 4: Meeting Record File Writer
**Goal:** Create well-formed meeting record files in `_working/auto/meetings/`

**Implementation Steps:**
- [x] 1. Create `workflows/meeting_extractor/writer.py`
- [x] 2. Implement `MeetingRecord` dataclass:
   ```python
   @dataclass
   class MeetingRecord:
       meeting_id: str
       created_at: str  # ISO timestamp
       created_by: str = "meeting-extractor"
       workflow: str = "meeting"
       state: str = "unprocessed"
       ingest_source: str  # relative path to ingest file
   ```
- [x] 3. Implement `generate_meeting_record(ingest_file: Path, meeting_id: str) -> MeetingRecord`
   - Create record with meeting_id and ingest source path
- [x] 5. Implement `write_meeting_file(record: MeetingRecord, output_dir: Path) -> Path`
   - Generate frontmatter YAML
   - Generate body with markdown link to ingest source
   - Write to `_working/auto/meetings/<meeting-id>.md`
   - Create directories if needed
- [x] 6. Add dry-run support (logging only, no file write)
- [x] 7. Add logging for file creation

**Note:** Use `[[_ingest/...]]` wiki-style links for Obsidian compatibility.

---

### Block 5: Reconciliation Logic
**Goal:** Implement the core idempotent reconciliation algorithm

**Implementation Steps:**
- [x] 1. Create `workflows/meeting_extractor/reconciler.py`
- [x] 2. Implement `meeting_record_exists(meeting_id: str, working_dir: Path) -> bool`
   - Check if `_working/auto/meetings/<meeting-id>.md` exists
- [x] 3. Implement `reconcile_meetings(ingest_dir: Path, working_dir: Path, dry_run: bool = False) -> dict`
   - Get all ingest transcripts
   - For each transcript:
     - Derive meeting_id
     - Check if record exists
     - If not, create it
   - Return summary stats: `{"scanned": N, "existing": M, "created": K}`
- [x] 4. Add logging for:
   - Number of transcripts scanned
   - Number already existing (skipped)
   - Number created
- [x] 5. Add error handling: log errors but continue processing other files
- [x] 6. Add unit tests (can use temporary directories)

---

### Block 6: Workflow Integration
**Goal:** Wire up the workflow to the runner framework

**Implementation Steps:**
- [x] 1. Update `workflows/meeting_extractor/workflow.py`
- [x] 2. Implement `run(context: RunContext, state: dict) -> dict`:
   ```python
   def run(context: RunContext, state: dict) -> dict:
       # Get directories from settings
       ingest_dir = Path(settings.obsidian_vault_dir) / "_ingest/fireflies"
       working_dir = Path(settings.obsidian_vault_dir) / "_working/auto/meetings"
       
       # Run reconciliation
       summary = reconcile_meetings(ingest_dir, working_dir, context.dry_run)
       
       # Log summary
       logger.info(f"Meeting extraction complete: {summary}")
       
       # Return empty state (implicit state via filesystem)
       return {}
   ```
- [x] 3. Add proper imports
- [x] 4. Add error handling and logging
- [x] 5. Ensure dry-run flag is respected

---

### Block 7: Settings & Configuration
**Goal:** Add any workflow-specific settings if needed

**Implementation Steps:**
- [x] 1. Review if any settings are needed beyond existing `obsidian_vault_dir`
- [x] 2. If needed, add to `settings.py` (e.g., `meeting_ingest_pattern`, `meeting_working_dir`)
- [x] 3. Document defaults

**Current Assessment:** Likely no additional settings needed for v1. Can use hardcoded paths relative to `obsidian_vault_dir`.

---

### Block 8: Testing & Validation
**Goal:** Ensure the workflow is robust and idempotent

**Implementation Steps:**
- [ ] 1. Create test fixtures: sample ingest files
- [ ] 2. Manual test: run workflow with `--dry-run`
- [ ] 3. Manual test: run workflow, verify meeting files created
- [ ] 4. Manual test: run workflow again, verify idempotence (no duplicates)
- [ ] 5. Manual test: delete a meeting record, re-run, verify recreation
- [ ] 6. Edge case: test with invalid ingest files (missing frontmatter, etc.)
- [ ] 7. Edge case: test with existing meeting file (should skip)
- [ ] 8. Document test results

---

### Block 9: Scheduler Integration (Future)
**Goal:** Register meeting_extractor with the scheduler

**Implementation Steps:**
- [ ] 1. Decide on schedule (e.g., hourly, twice daily)
- [ ] 2. Update `scheduler/scheduler.py` to register `meeting_extractor` workflow
- [ ] 3. Test scheduled execution
- [ ] 4. Document schedule in README or this plan

**Note:** This block can be deferred until workflow is fully tested manually.

---

## Dependencies & Assumptions

### External Dependencies
- `pathlib.Path` for filesystem operations (stdlib)

### Assumptions
1. **Ingest filenames are stable and unique** — the filename stem serves as the meeting ID
2. **All markdown files in `_ingest/fireflies/` are meeting transcripts** — no filtering needed
3. **Obsidian vault structure:**
   - `_ingest/fireflies/` contains meeting transcripts from Fireflies.ai workflow (never modified after creation)
   - `_working/auto/meetings/` is the target directory for meeting records
4. **No concurrent writers** — only the meeting extractor creates meeting records
5. **Filesystem is source of truth** — no external database or registry

---

## Migration & Rollout

### v1 Rollout (Initial Implementation)
- Manual execution only: `uv run python main.py run meeting_extractor`
- Full scan of `_ingest/fireflies/` every run
- Filename-based meeting IDs

### Future Enhancements (Post-v1)
- Incremental scanning (track last_run timestamp)
- Content-based meeting IDs (hash-based for robustness)
- Support for subfolder organization in `_working/auto/meetings/`
- Metadata enrichment (e.g., extract attendees, date from title)

---

## Success Criteria

### Functional Requirements
- ✅ Every meeting transcript in `_ingest/fireflies/` has a corresponding record in `_working/auto/meetings/`
- ✅ Running the workflow multiple times does not create duplicates
- ✅ Deleting a meeting record and re-running recreates it
- ✅ Workflow completes successfully with informative logging

### Non-Functional Requirements
- ✅ Workflow runs in < 5 seconds for typical vault size (~100 ingest files)
- ✅ Error handling: individual file errors don't crash the workflow
- ✅ Code follows project conventions (type hints, logging, structure)

---

## Open Questions for Discussion

1. **Error Handling:** If an ingest file is malformed (e.g., cannot be read), should we skip it and log a warning, or fail the entire workflow run?
   - **Recommendation:** Skip and log warning to allow processing to continue for other files

---

## Next Steps

1. **Review & Discuss:** Address open questions and ambiguities above
2. **Approve Building Blocks:** Confirm the implementation sequence
3. **Start Block 1:** Set up workflow module structure
4. **Iterate:** Implement one block at a time, test, and move forward

