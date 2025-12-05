---
name: response-protocol-rules
description: Unified response protocol for all human-facing agents - Recap + numbered choices format
type: rule
---

# Response Protocol

## Overview

This protocol standardizes how ALL agents interacting with humans format their responses. Every agent MUST follow this format to ensure consistent, clear communication.

---

## Standard Response Format

Every response to a human MUST end with:

```markdown
[Agent's main response content...]

---

## Recap

- [2-4 bullet points summarizing what was done/discussed]
- Use status icons: done, pending, blocked

---

## What do you want to do?

1. **[Primary action]** - Short description
2. **[Alternative]** - Short description
3. **[Other option]** - Short description
4. **[Optional 4th option]** - Short description
5. **Something else** - Describe what you want

> Tip: Type a number (1-5) or write your request.
```

---

## Status Icons

| Icon | Meaning |
|------|---------|
| `[done]` | Completed |
| `[pending]` | In progress / Next step |
| `[blocked]` | Blocked / Needs attention |
| `[skipped]` | Skipped / Not applicable |

---

## AskUserQuestion Tool

### When to Use

| Situation | Use AskUserQuestion? |
|-----------|---------------------|
| Clarify requirements BEFORE starting work | YES |
| Choose between architectures/approaches | YES |
| Gather multiple preferences (checkboxes) | YES (multiSelect: true) |
| End-of-response "What do you want to do?" | NO (use text format) |
| Quick yes/no questions | NO (use text) |

### Format

```json
{
  "questions": [
    {
      "question": "Which tech stack do you prefer?",
      "header": "Tech Stack",
      "multiSelect": false,
      "options": [
        {"label": "React + TypeScript", "description": "Modern frontend with typing"},
        {"label": "Vue 3", "description": "Progressive framework"},
        {"label": "Vanilla JS", "description": "No framework"}
      ]
    }
  ]
}
```

### Rules

- **Max 4 questions** per call
- **2-4 options** per question
- **Header**: max 12 characters
- **Label**: 1-5 words
- **multiSelect: true** for checkbox selection (multiple answers)
- User can ALWAYS write "Other" for custom response

---

## Recap Format by Agent Type

### ATLAS (Orchestrator)

```markdown
## Recap

- [Action routed to which agent]
- [Main result]
- [Suggested next step]

## What do you want to do?

1. **Continue** - Launch the next step
2. **Modify** - Change the approach
3. **Details** - See more information
4. **Different agent** - Route to a specialist
5. **Something else** - Describe what you want
```

### Workshop Facilitator

```markdown
## Recap - Phase [X]

- [What was explored]
- [Key insights]
- [Decisions made]

| Phase | Status |
|-------|--------|
| 1. Discovery | [done] |
| 2. Problem | [pending] |
| 3. Ideation | [pending] |

## What do you want to do?

1. **Continue** - Next question/step
2. **Go deeper** - Explore this point
3. **Next phase** - Move to phase [X+1]
4. **Go back** - Return to previous
5. **Something else** - Describe what you want
```

### Builders (Backend/Frontend/DevOps/Docs)

```markdown
## Recap

- [done] [File created/modified]
- [done] [Feature implemented]
- [pending] [What remains to do]

## What do you want to do?

1. **Test** - Run the tests
2. **Continue** - Next feature
3. **Modify** - Change the implementation
4. **See code** - Show the files
5. **Something else** - Describe what you want
```

### Planners (Debugger/Planner/UX-Designer)

```markdown
## Recap

- [Analysis completed]
- [Root cause / Plan / Design identified]
- [Recommendation]

## What do you want to do?

1. **Implement** - Apply the solution/plan
2. **Investigate more** - Dig deeper
3. **Different approach** - Try another method
4. **Export** - Save analysis/plan
5. **Something else** - Describe what you want
```

---

## Examples

### Good Response

```markdown
I created the UserProfile component with:
- Local state for user data
- Email and name field validation
- Integration with /users API

---

## Recap

- [done] `UserProfile.tsx` component created
- [done] Email + name validation added
- [pending] Unit tests to write

---

## What do you want to do?

1. **Add tests** - Jest + React Testing Library
2. **Connect to API** - Integrate with backend
3. **Improve styling** - Add CSS/Tailwind
4. **See the code** - Show complete component
5. **Something else** - Describe what you want

> Tip: Type a number (1-5) or write your request.
```

### Bad Response (Missing Protocol)

```markdown
I created the UserProfile component. Let me know if you need anything else.
```

---

## Implementation Checklist

When adding Response Protocol to an agent:

1. Add reference to this file in agent definition
2. Include Response Protocol section with:
   - Recap format specific to agent type
   - Numbered choices relevant to agent's domain
3. Ensure AskUserQuestion is used appropriately

### Section to Add in Each Agent

```markdown
## Response Protocol

ALWAYS end responses with:

1. **Recap section** - 2-4 bullet points summarizing actions/findings
2. **Numbered choices** - 3-5 options with descriptions
3. **Input hint** - "Type a number (1-5) or write your request"

Use AskUserQuestion tool for:
- Multi-step clarifications before starting work
- Choosing between architectural approaches
- Gathering multiple preferences (multiSelect)

See: `.claude/agents/rules/response-protocol.md`
```

---

## Language

- Default language: Follow user's language
- If user writes in French, respond in French
- If user writes in English, respond in English
- Recap and choices should match user's language
