# Sprint 1 Demo Script - PyForge

## Overview
End-to-end demonstration of all Sprint 1 features for PyForge Tier 0 implementation.

**Estimated Time**: 15 minutes  
**Test User**: `testuser@pyforge.dev` (created during onboarding)  
**Test Environment**: `http://localhost:3000` (development mode)

---

## Step-by-Step Walkthrough

### Step 1: Onboarding
1. Navigate to `http://localhost:3000/register`
2. Fill form:
   - Email: `testuser@pyforge.dev`
   - Username: `testuser`
   - Password: `testpass123`
3. Click "Create Account"
4. **Verification**: User is redirected to `/dashboard` automatically
   - Streak display shows `0` (fresh account)
   - XP shows `0`
   - ELO badge shows `1000` (default starting ELO)
   - Tier display shows `Tier 0`

### Step 2: Daily Mission
1. On dashboard, locate "Today's Mission Card" in the main column
2. Click the card to expand
3. Mission ticket displays:
   - Title: "Fix the Bug - Day 1"
   - Mode: `fix_bug`
   - Ticket text: "Kode sudah ada, ada 1–2 bug logika atau edge case. User mencari dan memperbaikinya."
   - Starter code appears in Monaco Editor:
     ```python
     def find_bug():
         pass
     ```
4. Monaco Editor features:
   - Python syntax highlighting
   - Autocomplete basic functions
   - Minimap enabled
   - Auto-save enabled (every 5s)

### Step 3: Run Tests
1. In the expanded Mission Card, click the **“Run Tests”** button
2. Spinner appears: "Initializing Pyodide..."
3. After ~3 seconds, test results display:
   - **Status**: `PASSED` (if code correct) or `FAILED`
   - **Grade**: `S`, `A`, `B`, `C`, or `F`
   - **Output**: `stdout` and `stderr` sections
   - **Execution time**: `2.1s` (example)
4. If grade is not `S`:
   - Error details show what failed
   - "AI Hint" button becomes available
   - "AI Review" button appears if grade ≥ C

### Step 4: AI Hint
1. Click the **“AI Hint”** button (visible after test submission if grade ≠ S)
2. Modal opens with:
   - Header: "Socratic Hint"
   - Content: Conceptual hint without code answers
     - Example: "Pertanyaan kembali: Apa yang kamu ingin fungsi ini lakukan? Coba pikirkan langkah-langkahnya sebelum menuliskan kode."
   - ELI5 toggle: Visible for Tier 0 users only
     - When toggled: "Jawabannya seperti cerita singkat: fungsi ini untuk mencari sesuatu yang hilang."
3. **Verification**: No code snippets in hint text

### Step 5: AI Review
1. After test submission, if grade is `C` or lower, "AI Review" button appears
2. Click "AI Review" to open review panel
3. Review content:
   - Constructive feedback mentioning specific lines
   - Pythonic suggestions (e.g., "Gunakan list comprehension untuk mengganti loop")
   - Potential bug warnings (e.g., "Hati-hati dengan kasus edge case kosong")
   - Encouraging closing remark
4. **“Apply Suggestions” button**:
   - When clicked, Monaco Editor content is replaced with improved code
   - User can accept or dismiss the changes

### Step 6: Dashboard Progress
1. Observe the dashboard updates automatically after mission completion:
   - **Streak**: Increments by 1 (or resets logic applied)
   - **XP**: Increments by reward amount (150 for passing Tier 0 mission)
   - **ELO**: Increases by ~12 points (formula: base + difficulty match)
   - **Skill Radar**: All 5 dimensions (logic, clean_code, debugging, testing, performance) show slight increase
   - **Tier badge**: Remains `Tier 0` (unless ELO ≥ 1100, then auto-shows "Ready for Tier 1!" banner)

### Step 7: Mission History
1. Click the "Mission History" tab/sidebar link
2. List displays all completed missions:
   - Each row shows: Date, Mission Title, Grade (S/A/B/C/F), XP earned, ELO change
   - Filter options: by mode (fix_bug/build_feature), by grade
3. **CSV Export** button:
   - Click to download `.csv` file with all mission data
   - Format: `mission_id,date,grade,xp,elo_change,mode,tier`

### Step 7: Completion
1. All above steps verified functional
2. User can repeat the daily mission cycle
3. All data persists to backend API and localStorage
4. Ready to continue with Sprint 2 features

---
*Demo Script Version: 1.0 | Generated: 2026-11-23*  
*Sprint 1 Complete - All Features Verified*