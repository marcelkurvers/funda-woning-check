# AI Capability Status Layer - Implementation Complete

## Overview

This implementation introduces a **global AI Capability Status model** that explicitly distinguishes between:

1. **IMPLEMENTATION_INVALID**: Code/architecture error - the system is broken
2. **OPERATIONALLY_LIMITED**: External resource constraint - the system works but a capability is temporarily unavailable

## Non-Negotiable Principle

> A missing external capability (e.g., AI credits, quota, provider outage) must **NEVER** invalidate a correct implementation.

## Components Implemented

### 1. Backend: Enhanced AICapabilityManager

**File**: `backend/ai/capability_manager.py`

- **CapabilityState**: AVAILABLE, LIMITED, QUOTA_EXCEEDED, OFFLINE, NOT_CONFIGURED, UNKNOWN
- **StatusCategory**: IMPLEMENTATION_VALID, IMPLEMENTATION_INVALID, OPERATIONALLY_LIMITED
- **CapabilityStatus**: Individual capability status with user-facing messages
- **GlobalCapabilityStatus**: Aggregated status for UI display
- **to_api_response()**: API-friendly format for frontend consumption

Key behaviors:
- QUOTA_EXCEEDED → StatusCategory.OPERATIONALLY_LIMITED (NOT an implementation error)
- OFFLINE → StatusCategory.OPERATIONALLY_LIMITED
- NOT_CONFIGURED → StatusCategory.IMPLEMENTATION_INVALID
- Auto-generates user-facing messages that reassure users when quota-limited

### 2. Backend: New API Endpoint

**File**: `backend/api/ai_status.py`

- Added `GET /api/ai/capabilities` endpoint
- Returns global capability status with explicit flags:
  - `is_implementation_valid`: True means system is correctly configured
  - `is_operational_limit`: True means external constraint (not a bug)

### 3. Frontend: GlobalCapabilityBanner Component

**File**: `frontend/src/components/common/GlobalCapabilityBanner.tsx`

- Shows a banner when there are operational limits
- Displays **"✓ System Correctly Configured"** badge when quota-limited
- Expandable detailed view showing per-capability status
- Distinguishes between:
  - Operational limits (amber styling, reassuring message)
  - Configuration issues (red styling, action prompt)

### 4. Frontend: Enhanced PlaneA2Content

**File**: `frontend/src/components/FourPlaneChapter.tsx`

- Updated to detect quota limits vs configuration issues
- Shows intelligent messaging:
  - **Quota limit**: "Temporarily Unavailable" with "✓ System Correctly Configured" badge
  - Explicitly states: "This is NOT an implementation error"
  - Shows visual concepts even when image generation is unavailable
  - **Config issue**: Prompts user to configure API key

### 5. Backend: Enhanced Gemini Image Provider

**File**: `backend/ai/providers/gemini_image_provider.py`

- Reports capability status with explicit StatusCategory
- Includes resume_hint for quota limits ("Quota typically resets within 24 hours")

## Test Coverage

**File**: `backend/tests/test_capability_manager.py`

19 comprehensive tests covering:
- Singleton pattern
- State transitions
- Category auto-detection
- Global status aggregation
- API response format
- User message generation
- **Critical distinction tests**: Verify quota limits never invalidate implementation

## Success Criteria ✓

| Criterion | Status |
|-----------|--------|
| Plane A2 renders with clear explanation instead of image | ✅ |
| Global status indicator confirms limited AI capability | ✅ |
| User sees: "This works — it is just temporarily constrained" | ✅ |
| Quota limit does NOT downgrade implementation status | ✅ |
| Information NOT hidden in logs only | ✅ |
| No content regeneration required to show capability state | ✅ |

## API Response Example

```json
{
  "overall": {
    "state": "quota_exceeded",
    "category": "operationally_limited",
    "summary": "Operational limits on: Image Generation",
    "user_message": "⚠️ Some features temporarily limited (external constraint) — System is correctly configured",
    "is_operational_limit": true,
    "is_implementation_valid": true
  },
  "capabilities": {
    "image_generation": {
      "state": "quota_exceeded",
      "category": "operationally_limited",
      "user_message": "Image Generation is temporarily unavailable due to quota limits. The system is correctly configured and will resume automatically.",
      "is_operational_limit": true,
      "is_implementation_error": false,
      "resume_hint": "Quota typically resets within 24 hours."
    }
  }
}
```

## UI Behavior

### When Quota-Limited:
1. **Header**: GlobalCapabilityBanner shows amber notification with "✓ System Correctly Configured" badge
2. **Plane A2**: Shows "Temporarily Unavailable" with explanation
3. **Visual Concepts**: Still rendered (they don't require image generation)
4. **User Understanding**: Clear that this is temporary and NOT a bug

### When Misconfigured:
1. **Header**: GlobalCapabilityBanner shows red notification with "Configure" button
2. **Plane A2**: Prompts user to set GEMINI_API_KEY
3. **User Action**: Directed to settings page

---

*Implementation completed: 2025-12-25*
