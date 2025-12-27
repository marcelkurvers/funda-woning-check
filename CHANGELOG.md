# Changelog

All notable changes to AI Woning Rapport will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [9.5.1] - 2025-12-27

### Fixed
- **CRITICAL**: Fixed missing `run_id` parameter in `execute_report_pipeline()` function (backend/pipeline/bridge.py:27)
  - This bug caused TypeError on every pipeline execution
  - All runs since Dec 26 were failing due to this issue
- Fixed incomplete test `test_duplicate_m2_display_fix` with proper assertions
- Fixed false positive test `test_upload_oversized_image_rejected` that passed even on failure
- Replaced source-code inspection tests with proper behavioral tests in `test_enforcement_laws.py`
- Reduced excessive mocking in `test_async_pipeline.py` to test real pipeline behavior

### Changed
- Updated API documentation with 10+ previously undocumented endpoints:
  - `/api/ai/runtime-status` - Unified AI provider status
  - `/api/governance/status` - Governance and policy enforcement
  - `/api/runs/active` - Get most recent active run
  - `/api/preferences` GET/POST - User preferences management
  - Complete `/api/config` endpoint variants
- Updated `/api/runs/{run_id}/report` response structure documentation to match actual implementation
- API documentation now includes `runId`, `address`, `kpis`, and `core_summary` fields

### Documentation
- Comprehensive API specification update (docs/API.md v5.1)
- Added detailed response examples for all major endpoints
- Fixed documentation/implementation mismatches identified during code review

### Testing
- Improved test quality by eliminating false positives
- Replaced implementation testing with behavioral testing
- Tests now verify actual runtime behavior instead of source code structure

## [9.5.0] - 2025-12-23

### Added
- KPI Uniqueness Contract: Every chapter has prefixed KPI IDs (ch0_, ch1_, ..., ch12_)
- Complete Chapter Maximalization: All 12 chapters (3-12) fully implemented
- 4-Plane Cognitive Architecture enforcement across all chapters

### Changed
- Enhanced fail-closed validation throughout pipeline
- Improved AI provider hierarchy and fallback mechanisms
