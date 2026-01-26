---
name: "Bitbucket Code Review"
description: "Perform a thorough code review on a PR"
argument-hint: "[PR number] - Review a pull request (e.g., 123)"
model: "code-review"
---

Analyze pull request: #{pr_number} for this repository.

## Step 1: Gather PR Information

Parse the PR number from the argument. If it is missing or ambiguous, ask for clarification.

Using the Bitbucket MCP server tools, fetch:

1. **PR metadata:** Use the `getPullRequest` tool with parameters:
   - `workspace`: _WORKSPACE_
   - `repo_slug`: _REPO_
   - `pull_request_id`: _PR_ID_
2. **PR diff:** Use the `getPullRequestDiff` tool with the same parameters as in step 1 to get the full diff.
   - **Large diffs:** If the diff is truncated, use `getPullRequestDiffStat` to get statistics and run `git diff` locally on the PR branch for complete file contents.
3. **PR comments (inline and general):** Use the `getPullRequestComments` tool with:
   - `workspace`: _WORKSPACE_, `repo_slug`: _REPO_, `pull_request_id`: _PR_ID_
   - **Pagination:** Use `pagelen` (default 10, max 100) and `page` parameters, or set `all: true` to fetch all comments.
4. **PR activity:** Use the `getPullRequestActivity` tool to get the full activity log including approvals, comments, and status changes.

### PR Information Summary Format

After gathering the data, organize it as follows:

**PR Metadata:**
- **Title:** [PR title]
- **Author:** [PR author]
- **Branch:** [source branch] → [destination branch]
- **State:** [OPEN/MERGED/DECLINED/SUPERSEDED]
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
`([Guideline](https://bitbucket.org/{workspace}/{repo_slug}/src/{source_branch}/.augment/code_review_guidelines.yaml): <guideline_id>)`

## Step 3: Review Existing Comments

Using the existing comments and reviews fetched in Step 1:
- Note any issues already addressed by human reviewers
- Avoid posting suggestions that contradict human reviewer feedback
- Avoid duplicating existing comments or inline review notes

## Step 4: Analyze the Changes

Generate a concise summary of this pull request that describes what changes were made and why.

Focus on:
- What changes were made
- Why the changes were made (if evident from the code/commit messages)
- Any important technical details or considerations

## Step 5: Format the Review Summary

Structure your PR summary comment using this exact format with the HTML marker comment:

```markdown
<!-- augment-pr-summary -->

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

After completing your analysis, post your review with comments to Bitbucket using the MCP tools.

### Step 6a: Check for Existing Summary Comment

First, check if a PR summary comment already exists:

1. **List existing PR comments:** Use the `getPullRequestComments` tool:
   - `workspace`: _WORKSPACE_
   - `repo_slug`: _REPO_
   - `pull_request_id`: _PR_ID_
   - `all`: true (to fetch all comments)

2. **Search for the marker:** Look for a comment containing `<!-- augment-pr-summary -->` in its content.

3. **If found:** Note the comment `id` to update it in Step 6b.

### Step 6b: Post or Update the Summary Comment

**If an existing summary comment was found (has the marker):**
Use the `updatePullRequestComment` tool:
- `workspace`: _WORKSPACE_
- `repo_slug`: _REPO_
- `pull_request_id`: _PR_ID_
- `comment_id`: The ID of the existing comment
- `content`: The updated summary in markdown format:

```markdown
<!-- augment-pr-summary -->

## 🤖 Augment PR Summary

**Summary:** [Your summary here]

**Changes:**
- [Change 1]
- [Change 2]

---
*🤖 Was this summary useful? React with 👍 or 👎*
```

**If no existing summary comment exists:**
Use the `addPullRequestComment` tool:
- `workspace`: _WORKSPACE_
- `repo_slug`: _REPO_
- `pull_request_id`: _PR_ID_
- `content`: The summary in markdown format (same as above)

### Step 6c: Post Inline Review Comments

For each inline comment, use the `addPullRequestComment` tool with the `inline` parameter:

**General comment (not on a specific line):**
- `workspace`: _WORKSPACE_
- `repo_slug`: _REPO_
- `pull_request_id`: _PR_ID_
- `content`: Your comment in markdown format

**Inline comment on a specific line:**
- `workspace`: _WORKSPACE_
- `repo_slug`: _REPO_
- `pull_request_id`: _PR_ID_
- `content`: Your inline comment in markdown format
- `inline`: An object specifying the location:
  ```json
  {
    "path": "path/to/file.ts",
    "to": 123
  }
  ```

### Inline Comment Field Reference

- `path`: File path relative to repository root
- `to`: Line number in the NEW version of the file (for added/modified lines)
- `from`: Line number in the OLD version of the file (for deleted lines)
- `content`: The comment text in markdown format

**Examples:**
- Comment on new/added line: Use `to` parameter only
- Comment on deleted line: Use `from` parameter only
- Comment on modified line: Use both `from` and `to` parameters

### Common Errors to Avoid

- **Do NOT** use `web-fetch` to interact with Bitbucket API directly - always use the MCP tools
- **Do NOT** use `deletePullRequestComment` unless explicitly requested by the user
- **Always** use the `<!-- augment-pr-summary -->` marker at the start of the summary comment content
- **Always** provide the correct `workspace` and `repo_slug` parameters to all tools
- **For inline comments**, ensure the `path` matches the file path exactly as shown in the diff