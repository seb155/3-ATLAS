# Daemon Redesign Plan

## Vision Statement

**Daemon** is not just an API—it's a **live window into a person**. Like a friend's status update, but structured and queryable. The core philosophy: *technology's primary role is to enable human connection*.

What a friend or follower wants to know:
- Where are you? (Location)
- What are you about? (Mission/Purpose)
- What are you into right now? (Current focus)
- What are you reading/thinking about? (Intellectual state)
- What do you recommend? (Curated lists)
- How can I connect with you programmatically? (API)

## Current Problems

1. **No "live" sections** - Missing currently reading, recent ideas, what I'm working on
2. **Poor hierarchy** - All panels treated equally, no visual importance
3. **Too technical** - API access prominent, feels like docs not a personal page
4. **Static feel** - Doesn't feel like a living, breathing personal status

## Proposed Section Architecture

### Tier 1: Identity (Always Visible, Top)
```
┌─────────────────────────────────────────────────────────────┐
│  DAEMON                                                [LIVE] │
│  Personal MCP API for Daniel Miessler                        │
│  "My vision of the future where technology's primary role    │
│   is to enable human connection"                             │
└─────────────────────────────────────────────────────────────┘
```

### Tier 2: Primary Status (Full Width, Prominent)
```
┌──────────────────────────────────────────────────────────────┐
│ 📍 LOCATION                                                   │
│ San Francisco Bay Area                                        │
│ (Home base)                                                   │
└──────────────────────────────────────────────────────────────┘
```

### Tier 3: Core Purpose (2 columns, High Importance)
```
┌────────────────────────────┬─────────────────────────────────┐
│ 🎯 MISSION                 │ 🧭 TELOS FRAMEWORK              │
│ Human flourishing through  │ P1: People lack meaning         │
│ AI augmentation...         │ M1: Increase eudaimonia         │
│                            │ G1: Reach 1M people...          │
└────────────────────────────┴─────────────────────────────────┘
```

### Tier 4: Live Updates (3 columns, "What's happening now")
**NEW SECTIONS:**
```
┌──────────────────┬──────────────────┬──────────────────────────┐
│ 📖 READING       │ 💡 RECENT IDEAS  │ 🔨 WORKING ON            │
│ "The Beginning   │ • AI agents will │ • Kai personal AI        │
│  of Infinity"    │   replace apps   │ • Fabric 2.0             │
│ by David Deutsch │ • Daemon concept │ • AUGMENTED course       │
└──────────────────┴──────────────────┴──────────────────────────┘
```

### Tier 5: Curated Lists (3 columns, Recommendations)
```
┌──────────────────┬──────────────────┬──────────────────────────┐
│ 📚 BOOKS         │ 🎬 MOVIES        │ 🔮 PREDICTIONS           │
│ • Antifragile    │ • Interstellar   │ • 95% - AI transforms    │
│ • Thinking Fast  │ • Arrival        │   white collar work      │
│ • The Beginning  │ • The Matrix     │ • 85% - Agents replace   │
│   of Infinity    │                  │   most SaaS by 2027      │
└──────────────────┴──────────────────┴──────────────────────────┘
```

### Tier 6: Context (3 columns, Deeper Info)
```
┌──────────────────┬──────────────────┬──────────────────────────┐
│ ⚙️ PREFERENCES   │ 🏠 DAILY ROUTINE │ 🚀 PROJECTS              │
│ • TypeScript     │ • 8AM wake       │ • Fabric (AI framework)  │
│ • Minimalism     │ • 9AM deep work  │ • Unsupervised Learning  │
│ • Long-form      │ • Afternoon walk │ • Daemon (this API)      │
└──────────────────┴──────────────────┴──────────────────────────┘
```

### Tier 7: Technical (Centered, Subdued)
```
                    ┌────────────────────────────┐
                    │ 🔌 API ACCESS              │
                    │ mcp.daemon.danielmiessler  │
                    │ [View API Docs]            │
                    └────────────────────────────┘
```

## New Daemon Sections to Add

### 1. CURRENTLY_READING
```markdown
[CURRENTLY_READING]

"The Beginning of Infinity" by David Deutsch
Started: November 2025
```
**Update triggers:** "I'm reading...", "Started reading...", "Finished..."

### 2. RECENT_IDEAS
```markdown
[RECENT_IDEAS]

- AI agents will replace most SaaS applications within 3 years
- The daemon concept is the foundation of a new human-tech interface
- Personal AI infrastructure is the new personal computer
```
**Update triggers:** "New idea:", "I'm thinking about...", "Add to recent ideas..."

### 3. WORKING_ON
```markdown
[WORKING_ON]

Primary focus: Kai personal AI infrastructure
Secondary: AUGMENTED course development
Exploring: Voice-first interfaces
```
**Update triggers:** "Working on...", "Focusing on...", "Current project is..."

## Frontend Implementation

### 1. Hero Section (Compact)
- Title: DAEMON with LIVE badge
- Subtitle: "Personal MCP API for [Daniel Miessler](https://danielmiessler.com)"
- Description: "My vision of the future where technology's primary role is to enable human connection"
- Small pills: MCP | Real-time | Public

### 2. Location Card (Full Width)
- Prominent, single card spanning full width
- Large text, minimal decoration
- Timestamp of last update

### 3. Core Purpose Row (2 columns)
- Mission: Full mission statement
- TELOS: Abbreviated view with link to full page

### 4. Live Updates Row (3 columns)
- Currently Reading: Book title, author, progress
- Recent Ideas: Latest 3 ideas as bullet points
- Working On: Current focus areas

### 5. Recommendations Row (3 columns)
- Books: Top 4-5 recommendations
- Movies: Top 4-5 recommendations
- Predictions: Top 3 with confidence levels

### 6. Context Row (3 columns)
- Preferences: Key preferences
- Routine: Abbreviated schedule
- Projects: Active technical projects

### 7. API Footer (Centered, Subdued)
- Smaller card, centered
- Endpoint URL
- Link to API docs
- "Connect your AI"

## Daemon Skill Updates

### New Update Patterns

```
"I'm reading [book]" → Update CURRENTLY_READING
"New idea: [idea]" → Append to RECENT_IDEAS (keep last 5)
"Focusing on [project]" → Update WORKING_ON primary
"Finished [book]" → Move to FAVORITE_BOOKS, clear CURRENTLY_READING
```

### Automatic Freshness

Consider adding `last_updated` timestamps to each section so visitors can see how fresh the data is.

## Fixes Required

1. **API Docs button broken** - Check href="/api" routing
2. **Update subtitle** - New vision statement
3. **Link Daniel Miessler** - Add hyperlink to danielmiessler.com

## Implementation Steps

### Phase 1: Frontend Redesign
1. Fix API docs button (routing issue)
2. Update Hero with new subtitle and link
3. Restructure DaemonDashboard with new hierarchy:
   - Location (full width)
   - Mission + TELOS (2 col)
   - Reading + Ideas + Working On (3 col)
   - Books + Movies + Predictions (3 col)
   - Preferences + Routine + Projects (3 col)
   - API Access (centered footer)

### Phase 2: Backend Updates
4. Add new sections to daemon.md:
   - [CURRENTLY_READING]
   - [RECENT_IDEAS]
   - [WORKING_ON]
5. Update daemon skill with new parsing patterns
6. Run update-daemon to publish

### Phase 3: Skill Enhancement
7. Update Daemon skill with new section patterns
8. Add "freshness" concept (last_updated per section)
9. Test natural language updates for new sections

## Design Principles

1. **Human first, API second** - This is about Daniel, not about the tech
2. **Live feeling** - Should feel like checking a friend's status
3. **Clear hierarchy** - Most important stuff visible first
4. **Scannable** - Quick glance gives full picture
5. **Beautiful** - Should look as good as any personal site

## Questions to Resolve

1. Should "About" be a separate panel or just in the subtitle?
2. How many recent ideas to show? (Suggest: 3-5)
3. Should we show "last updated" timestamps on each section?
4. Do we want an "Availability" status? (e.g., "Open to conversations")
