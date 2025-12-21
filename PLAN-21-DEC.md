# Execution Plan - 21 December 2025

**Plan ID**: funda-app-phase2-recovery
**Created**: 2025-12-21
**Status**: IN PROGRESS
**Current Phase**: Phase 1

---

## Execution Overview

### Problem Statement
- Photos not appearing in frontend header
- Parsed property info not appearing in frontend header
- Root cause unknown - requires investigation

### Approach
Crash-safe, phased execution with external artifact tracking:
1. **Phase 1**: Investigate data flow (read-only, parallel agents)
2. **Phase 2**: Analyze findings and propose fixes
3. **Phase 3**: Implement fixes (conditional on Phase 2 approval)
4. **Phase 4**: Document test procedures

---

## Phase 1: Data Flow Verification

### Phase Objective
Trace data flow from user input → database → report generation → frontend to identify missing links.

### Agents (4 total, executing in parallel)

#### Agent 1.1: Media URL Flow Verification
**Task**: Trace `media_urls` parameter through the system
**Inputs**:
- `backend/main.py`
- `backend/database.py` (if exists)
- `backend/models.py` (if exists)

**Investigation Steps**:
1. Find POST /runs endpoint - verify it accepts `media_urls` parameter
2. Find database insertion code - verify `media_urls` is saved
3. Find GET /runs/{id}/report endpoint - verify `media_urls` is retrieved from DB
4. Find chapter context construction - verify `media_urls` is passed to `intelligence.py`
5. Trace to `intelligence.py:55` where `ctx.get('media_urls')` is called

**Expected Output**: `.claude/execution/artifacts/phase_1_media_flow.md`
**Output Format**:
```markdown
## Data Flow Trace
1. POST /runs (main.py:LINE_X) - receives media_urls: YES/NO
2. Database save (main.py:LINE_Y) - stores media_urls: YES/NO
3. GET /runs/{id}/report (main.py:LINE_Z) - retrieves media_urls: YES/NO
4. Context construction (main.py:LINE_W) - passes to intelligence.py: YES/NO

## Missing Links
[List any breaks in the chain]

## Verdict
FLOW_COMPLETE | FLOW_BROKEN
```

**Success Criteria**:
- File exists with all sections
- Contains file:line references for each step
- Contains explicit verdict

---

#### Agent 1.2: Parser Integration Verification
**Task**: Trace parser output (asking_price_eur, living_area_m2, etc.) through system
**Inputs**:
- `backend/main.py`
- `backend/parser.py`
- `backend/intelligence.py`

**Investigation Steps**:
1. Find where parser is invoked during run processing
2. Identify parser output fields (asking_price_eur, living_area_m2, build_year, energy_label, etc.)
3. Find where parser output is stored (database columns, in-memory, or discarded)
4. Find GET /runs/{id}/report endpoint - verify parser data is included
5. Find chapter context construction - verify parser data is passed to `intelligence.py`
6. Trace to `intelligence.py:41-56` where context fields are mapped

**Expected Output**: `.claude/execution/artifacts/phase_1_parser_flow.md`
**Output Format**:
```markdown
## Parser Invocation Point
File: main.py:LINE_X
Called during: run processing | report generation | NOT_CALLED

## Parser Output Fields
- asking_price_eur
- living_area_m2
- plot_area_m2
- build_year
- energy_label
- [others identified]

## Output Storage Method
DIRECT_TO_DB | IN_MEMORY | NOT_STORED

## Context Integration
File: main.py:LINE_Y
Parser data passed to intelligence.py: YES/NO

## Verdict
INTEGRATED | NOT_INTEGRATED
```

**Success Criteria**:
- File exists with all sections
- Identifies storage method
- Contains explicit verdict

---

#### Agent 1.3: Database Schema Verification
**Task**: Document database schema and verify required columns exist
**Inputs**:
- `backend/main.py` (look for CREATE TABLE statements)
- `backend/models.py` (if exists)
- `backend/database.py` (if exists)

**Investigation Steps**:
1. Locate database schema definition (SQLite CREATE TABLE or ORM model)
2. Document complete `runs` table schema
3. Check for `media_urls` column (TEXT or JSON type expected)
4. Check for parser output columns:
   - `asking_price_eur` or `asking_price`
   - `living_area_m2` or `living_area`
   - `plot_area_m2` or `plot_area`
   - `build_year`
   - `energy_label`
5. Identify any missing columns

**Expected Output**: `.claude/execution/artifacts/phase_1_schema.md`
**Output Format**:
```markdown
## Runs Table Schema
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | INTEGER | NOT NULL | Primary key |
| funda_url | TEXT | NOT NULL | Property URL |
| ... | ... | ... | ... |

## Column Check: Media URLs
- media_urls: PRESENT (type: TEXT/JSON) | MISSING

## Column Check: Parser Fields
- asking_price_eur: PRESENT (type: X) | MISSING
- living_area_m2: PRESENT (type: X) | MISSING
- plot_area_m2: PRESENT (type: X) | MISSING
- build_year: PRESENT (type: X) | MISSING
- energy_label: PRESENT (type: X) | MISSING

## Verdict
SCHEMA_COMPLETE | SCHEMA_MISSING_COLUMNS

## Missing Columns (if any)
[List columns that need to be added]
```

**Success Criteria**:
- File exists with complete schema table
- Explicit check for media_urls column
- Explicit check for parser field columns
- Contains verdict

---

#### Agent 1.4: Import Dependency Scan
**Task**: Verify no broken imports after `ollama_client.py` deletion
**Inputs**:
- All `backend/**/*.py` files

**Investigation Steps**:
1. Use Grep to scan for: `import ollama_client`
2. Use Grep to scan for: `from ollama_client import`
3. Document any files still referencing the deleted module
4. Verify `backend/intelligence.py` does NOT import ollama_client (already confirmed, but re-verify)

**Expected Output**: `.claude/execution/artifacts/phase_1_import_scan.md`
**Output Format**:
```markdown
## Scan Command
grep -r "import ollama_client|from ollama_client" backend/

## Scan Results
[Grep output]

## Affected Files
NONE |
- backend/file1.py:line_X
- backend/file2.py:line_Y

## Verdict
IMPORTS_CLEAN | IMPORTS_BROKEN

## Action Required
NONE | Fix imports in listed files
```

**Success Criteria**:
- File exists with grep results
- Explicitly lists affected files or states NONE
- Contains verdict

---

### Parallel Execution Safety

**Why parallel execution is safe**:
1. ✅ **No write conflicts**: Each agent writes to a different file
   - 1.1 → `phase_1_media_flow.md`
   - 1.2 → `phase_1_parser_flow.md`
   - 1.3 → `phase_1_schema.md`
   - 1.4 → `phase_1_import_scan.md`

2. ✅ **Read-only operations**: All agents only read existing files, no modifications

3. ✅ **Independent tasks**: No agent depends on another agent's output

4. ✅ **Failure isolation**: If one agent crashes, others continue and provide valuable data

5. ✅ **Token budget**: 4 agents × 15k = 60k total < 150k available

**Launch method**: Single message with 4 Task tool invocations

---

### Phase 1 Completion Criteria

**Phase 1 is COMPLETE when**:
1. At least 3 out of 4 agents finish with SUCCESS
2. At least 3 out of 4 artifact files exist and are valid
3. All existing artifact files contain required sections and verdicts
4. Token budget remaining > 50k (enough for subsequent phases)
5. No unexpected file modifications detected

**Phase 1 Status Options**:
- **COMPLETED**: All criteria met, proceed to Phase 2
- **PARTIAL**: 3/4 criteria met, proceed to Phase 2 with partial data
- **FAILED**: Fewer than 3 agents succeeded, abort execution

**Artifacts to be created**:
- `.claude/execution/artifacts/phase_1_media_flow.md`
- `.claude/execution/artifacts/phase_1_parser_flow.md`
- `.claude/execution/artifacts/phase_1_schema.md`
- `.claude/execution/artifacts/phase_1_import_scan.md`
- `.claude/execution/agent_logs/phase_1_agent_1.1_{session_id}.jsonl`
- `.claude/execution/agent_logs/phase_1_agent_1.2_{session_id}.jsonl`
- `.claude/execution/agent_logs/phase_1_agent_1.3_{session_id}.jsonl`
- `.claude/execution/agent_logs/phase_1_agent_1.4_{session_id}.jsonl`
- `.claude/execution/artifacts/phase_1.manifest.json` (after validation)

---

## Phase 2: Root Cause Analysis (NOT YET STARTED)

**Depends on**: Phase 1 completion

**Agent 2.1**: Synthesize Phase 1 findings
**Inputs**: All Phase 1 artifacts
**Outputs**:
- `.claude/execution/artifacts/phase_2_root_cause.md`
- `.claude/execution/artifacts/phase_2_fix_plan.md`

**Task**: Consolidate findings, identify exact missing code/configuration, propose minimal fixes

**Execution**: Sequential (single agent, depends on all Phase 1 outputs)

---

## Phase 3: Implementation (CONDITIONAL, NOT YET STARTED)

**Depends on**: Phase 2 completion + User approval + Safety assessment = SAFE_TO_APPLY

**Agents**: TBD based on Phase 2 fix plan

**Execution**: Sequential (likely, to avoid write conflicts in `backend/main.py`)

**Conditional**: ONLY executed if Phase 2 determines fixes are safe and user approves

---

## Phase 4: Test Documentation (NOT YET STARTED)

**Depends on**: Phase 3 completion OR Phase 2 completion (if Phase 3 skipped)

**Agent 4.1**: Document manual test procedures
**Output**: `.claude/execution/artifacts/phase_4_test_plan.md`

**Execution**: Sequential (single agent)

---

## Execution Timeline

**Phase 1**: ~3-5 minutes, 60k tokens (IN PROGRESS)
**Phase 2**: ~2 minutes, 20k tokens (PENDING)
**Phase 3**: ~4 minutes, 40k tokens (CONDITIONAL)
**Phase 4**: ~1 minute, 10k tokens (PENDING)

**Total**: ~15 minutes, 130k tokens (excluding user approval wait time)

---

## Token Budget Tracking

**Initial Budget**: 200k tokens
**Used for Planning**: ~50k tokens
**Available for Execution**: ~150k tokens

**Phase Budgets**:
- Phase 1: 60k tokens (40% of available)
- Phase 2: 20k tokens (13% of available)
- Phase 3: 40k tokens (27% of available)
- Phase 4: 10k tokens (7% of available)
- Reserve: 20k tokens (13% safety buffer)

**Safety Thresholds**:
- SAFE: < 120k used (80k+ remaining)
- CAUTION: 120-150k used (50-80k remaining)
- CRITICAL: 150-170k used (30-50k remaining)
- EMERGENCY: > 170k used (< 30k remaining)

---

## Risk Mitigation

### Risk: Agent Crashes Mid-Execution
**Mitigation**: Parallel execution + failure isolation
**Impact**: Partial data still valuable, can proceed with 3/4 agents

### Risk: Token Limit Hit During Phase
**Mitigation**: Per-agent 15k limit, phase 60k limit, stop before critical threshold
**Impact**: Write CRASH logs, document partial findings, allow recovery

### Risk: Data Flow Not Found
**Mitigation**: Agents instructed to write "NOT_FOUND" explicitly
**Impact**: Phase 2 can document "unfixable due to missing code"

### Risk: Multiple Files Need Same Modification
**Mitigation**: Force sequential execution in Phase 3
**Impact**: Slower but safer, no write conflicts

---

## Pre-Execution Checklist

**Environment**:
- ✅ Working directory: `/Users/marcelkurvers/Development/funda-app`
- ✅ `backend/main.py` exists (verified in IMPROVEMENTS_21-DEC.md)
- ✅ `backend/parser.py` exists (verified in IMPROVEMENTS_21-DEC.md)
- ✅ `backend/intelligence.py` exists (verified in IMPROVEMENTS_21-DEC.md)
- ✅ Token budget: 150k available

**Safety**:
- ✅ Parallel execution safety confirmed (no write conflicts)
- ✅ All Phase 1 agents are read-only
- ✅ Failure isolation confirmed
- ✅ Maximum scope per agent defined (15k tokens, 5-6 files max)

**Directories to Create**:
- `.claude/execution/artifacts/` (for investigation reports)
- `.claude/execution/agent_logs/` (for lifecycle logs)

---

## Execution Log

### 2025-12-21 - Phase 1 Launch

**Time**: [TIMESTAMP WILL BE ADDED]
**Action**: Launching Phase 1 - 4 parallel investigation agents
**Agents**:
- Agent 1.1: Media URL Flow Verification
- Agent 1.2: Parser Integration Verification
- Agent 1.3: Database Schema Verification
- Agent 1.4: Import Dependency Scan

**Expected Outcome**: 4 investigation reports documenting current data flow state

**Next Steps After Phase 1**:
1. Validate all artifacts exist and contain verdicts
2. Generate `phase_1.manifest.json`
3. Report findings to user
4. If COMPLETED: Proceed to Phase 2
5. If PARTIAL: Discuss with user whether to retry failed agents or proceed
6. If FAILED: Abort and require manual intervention

---

**END OF PLAN**

*This plan will be updated as execution progresses.*
