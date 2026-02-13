---
name: "GitLab Code Review"
description: "Perform a thorough code review on a MR"
argument-hint: "[MR IID] - Review a merge request (e.g., 123)"
model: "code-review"
---

Analyze merge request: _MR_IID_ for this repository.

## Step 1: Gather MR Information

Parse the MR IID from the argument. If it is missing or ambiguous, ask for clarification.

Using the GitLab MCP tools, fetch:

1. **MR metadata:** Use `get_merge_request` tool with parameters:
   - `project_id`: _PROJECT_ID_
   - `iid`: _MR_IID_
2. **MR files/diff:** Use `get_merge_request_diffs` tool with the same parameters as in step 1 to get the diff:
   - **Large diffs:** If the diff is truncated, run `git diff` locally on the MR branch to get the complete diff.
3. **Discussion threads (inline comments):** Use `mr_discussions` tool to list all discussion items for the merge request with the same parameters as in step 1:
   - **Pagination:** Handle pagination if responses contain many discussion threads.

### MR Information Summary Format

After gathering the data, organize it as follows:

**MR Metadata:**
- **Title:** [MR title]
- **Author:** [MR author]
- **Branch:** [source branch] → [target branch]
- **State:** [opened/closed/merged]
- **Head SHA:** [commit SHA for review submissions]

**Proposed Changes:**
- **Files changed:** [count]
- **Additions:** [+lines] | **Deletions:** [-lines]
- **Key Changes:** [Bullet list of the most significant changes, grouped by area/file if helpful]

**Notable Inline Discussion Comments:**
- Include only high-signal inline comments.
- For each, include: file path, line (if present), author, and a 1-sentence paraphrase.

## Step 2: Check for Custom Guidelines

Look for custom code review guidelines in the repository:
- Use `view` tool to check for `.augment/code_review_guidelines.yaml` in the repository
- If found, apply those guidelines (skip low-severity ones)

When referencing a custom guideline in your review comments, quote it using the format:
`([Guideline](_GITLAB_URL_/_PROJECT_PATH_/-/blob/_SOURCE_BRANCH_/.augment/code_review_guidelines.yaml): <guideline_id>)`

## Step 3: Review Existing Comments

Using the existing discussions fetched in Step 1:
- Note any issues already addressed by human reviewers
- Avoid posting suggestions that contradict human reviewer feedback
- Avoid duplicating existing comments or inline discussion notes

## Step 4: Analyze the Changes

Generate a concise summary of this merge request that describes what changes were made and why.

Focus on:
- What changes were made
- Why the changes were made (if evident from the code/commit messages)
- Any important technical details or considerations

## Step 5: Format the Review Summary

Structure your MR summary comment using this exact format with the marker comment:

```markdown
## 🤖 Augment PR Summary

**Summary:** [One sentence describing the PR]

**Changes:**
- [Key change 1]
- [Key change 2]
```

If a section has no findings, omit it entirely.

## Guidelines

- Be specific: Include file paths, line numbers, and code snippets
- Be constructive: Explain *why* something is problematic and suggest fixes
- Be thorough but focused: Don't nitpick style if there are real bugs
- Consider context: Understand the intent before criticizing the approach
- Skip low-severity issues unless they indicate a pattern

## Step 6: Post Your Review

After completing your analysis, post your review with inline comments to GitLab using the MCP tools.

### Step 6a: Check for Existing Summary Comment

First, check if an MR summary comment already exists:

1. **List existing MR discussions:** Use `mr_discussions` tool to get all discussion threads for the merge request:
   - `project_id`: _PROJECT_ID_
   - `iid`: _MR_IID_

2. **Search for the marker:** Look for a note containing `## 🤖 Augment PR Summary` in its body.

3. **If found:** Note the discussion/note IDs to update it in Step 6b.

### Step 6b: Post or Update the Summary Comment

**If an existing summary comment was found (has the marker):**
Use `update_merge_request_note` tool:
- `project_id`: _PROJECT_ID_
- `mr_iid`: _MR_IID_
- `note_id`: The ID of the existing note
- `body`: The updated summary in markdown format:

```markdown
## 🤖 Augment PR Summary

**Summary:** [Your summary here]

**Changes:**
- [Change 1]
- [Change 2]

---
*🤖 Was this summary useful? React with 👍 or 👎*
```

**If no existing summary comment exists:**
Use the `create_merge_request_note` tool:
- `project_id`: _PROJECT_ID_
- `mr_iid`: _MR_IID_    
- `content`: The summary in markdown format (same as above)

### Step 6c: Post Inline Review Comments

**Create threaded discussions on specific lines:**
   Use `create_merge_request_thread` tool to create inline comments on specific files and lines.

   Required parameters:
   - `project_id`: _PROJECT_ID_
   - `mr_iid`: _MR_IID_
   - `body`: The comment text
   - `position`: Object specifying the file and line location:
      - `base_sha`: The base commit SHA
      - `start_sha`: The start commit SHA
      - `head_sha`: The head commit SHA
      - `position_type`: Use `"text"` for code comments
      - `new_path`: File path for new/modified lines
      - `old_path`: File path for deleted lines
      - `new_line`: Line number in the new file (for additions)
      - `old_line`: Line number in the old file (for deletions)

### Comment Field Reference

- `new_path` / `old_path`: File path relative to repository root
- `new_line`: Line number for additions (new lines)
- `old_line`: Line number for deletions (removed lines)
- `body`: The comment text
- `position_type`: Use `"text"` for code line comments

### Common Errors to Avoid

- **Do NOT** use `web-fetch` to interact with GitLab API directly - always use the MCP tools
- **Do NOT** omit required SHA values (`base_sha`, `start_sha`, `head_sha`) when creating inline threads
- **Do NOT** specify both `new_line` and `old_line` for the same comment—use one based on whether commenting on added or removed code
- **Always** use the correct position type (`"text"` for code comments)