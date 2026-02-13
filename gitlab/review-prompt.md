---
name: "GitLab Code Review"
description: "Perform a thorough code review on a MR"
argument-hint: "[MR number] - Review a merge request (e.g., 123)"
---

Analyze merge request for this repository.

## Step 1: Gather MR Information

Using the GitLab MCP server tools, fetch:

1. **MR metadata:** Use the `getMergeRequest` tool to get MR details.
2. **MR diff:** Use the `getMergeRequestChanges` tool to get the full diff.
   - **Large diffs:** If the diff is truncated, run `git diff` locally on the MR branch for complete file contents.
3. **MR comments (inline and general):** Use the `getMergeRequestNotes` tool.
4. **MR approvals:** Use the `getMergeRequestApprovals` tool to get approval status.

### MR Information Summary Format

After gathering the data, organize it as follows:

**MR Metadata:**
- **Title:** [MR title]
- **Author:** [MR author]
- **Branch:** [source branch] → [target branch]
- **State:** [opened/merged/closed]
- **Source Commit:** [commit hash from source branch]

**Proposed Changes:**
- **Files changed:** [count]
- **Additions:** [+lines] | **Deletions:** [-lines]
- **Key Changes:** [Bullet list of the most significant changes, grouped by area/file if helpful]

**Notable Inline Review Comments:**
- Include only high-signal inline comments.
- For each, include: file path, line (if present), author, and a 1-sentence paraphrase.

## Step 2: Check for Custom Guidelines

Look for custom code review guidelines in the repository:
- Use the `view` tool to check for `.augment/code_review_guidelines.yaml` in the repository
- If found, apply those guidelines (skip low-severity ones)

When referencing a custom guideline in your review comments, quote it using the format:
`([Guideline](.augment/code_review_guidelines.yaml): <guideline_id>)`

## Step 3: Review Existing Comments

Using the existing comments and reviews fetched in Step 1:
- Note any issues already addressed by human reviewers
- Avoid posting suggestions that contradict human reviewer feedback
- Avoid duplicating existing comments or inline review notes

## Step 4: Analyze the Changes

Generate a concise summary of this merge request that describes what changes were made and why.

Focus on:
- What changes were made
- Why the changes were made (if evident from the code/commit messages)
- Any important technical details or considerations

## Step 5: Analyze Test Coverage (Optional)

If the repository has test coverage reporting configured:
- Check for coverage reports in common locations (e.g., `coverage/`, `.coverage`, `coverage.xml`, etc.)
- If coverage data is available, review it against the changes

General coverage guidance (when applicable):
- New features should aim for reasonable test coverage
- Critical paths should have appropriate coverage
- Flag significant new code that lacks corresponding tests

**Note:** This step is optional and depends on the project's testing infrastructure. Skip if no coverage tooling is configured.

## Step 6: Format the Review Summary

Structure your MR summary comment using this exact format:

```markdown
## 🤖 Augment MR Summary

**Summary:** [One sentence describing the MR]

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

## Step 7: Post Your Review

After completing your analysis, post your review with comments to GitLab using the MCP tools.

### Step 7a: Check for Existing Summary Comment

First, check if a MR summary comment already exists:

1. **List existing MR notes:** Use the `getMergeRequestNotes` tool.
2. **Search for the marker:** Look for a note containing `## 🤖 Augment MR Summary` in its content.
3. **If found:** Note the note `id` to update it in Step 7b.

### Step 7b: Post or Update the Summary Comment

**If an existing summary comment was found (has the marker):**
Use the `updateMergeRequestNote` tool with the note ID and updated body.

**If no existing summary comment exists:**
Use the `createMergeRequestNote` tool with the summary in markdown format.

Include at the end:
```markdown
---
*🤖 Was this summary useful? React with 👍 or 👎*
```

### Step 7c: Post Inline Review Comments

For each inline comment, use the `createMergeRequestDiscussion` tool with:
- `body`: Your inline comment in markdown format
- `position`: An object specifying the location with `base_sha`, `start_sha`, `head_sha`, `position_type`, `old_path`, `new_path`, and line numbers.

### Inline Comment Field Reference

- `new_line`: Line number in the NEW version of the file (for added/modified lines)
- `old_line`: Line number in the OLD version of the file (for deleted lines)

**Examples:**
- Comment on new/added line: Use `new_line` parameter only
- Comment on deleted line: Use `old_line` parameter only
- Comment on modified line: Use both `old_line` and `new_line` parameters

### Common Errors to Avoid

- **Do NOT** use `web-fetch` to interact with GitLab API directly - always use the MCP tools
- **Do NOT** delete comments unless explicitly requested by the user
- **Always** provide the correct `project_id` parameter to all tools
- **For inline comments**, ensure the `path` matches the file path exactly as shown in the diff

