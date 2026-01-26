---
name: "Azure DevOps Code Review"
description: "Perform a thorough code review on a PR"
argument-hint: "[PR number] - Review a pull request (e.g., 123)"
model: "code-review"
---

Analyze pull request: #{pr_number} for this repository.

## Step 1: Gather PR Information

Parse the PR number from the argument. If it is missing or ambiguous, ask for clarification.

Using the Azure DevOps API tool, fetch:

1. **PR metadata:** Use `repo_get_pull_request_by_id` with `repositoryId: ((REPO))` and `pullRequestId: ((PR_ID))`
2. **PR diff:** ((DIFF))
3. **Review threads:** Use `repo_list_pull_request_threads` with `repositoryId: ((REPO))` and `pullRequestId: ((PR_ID))`
4. **Thread comments:** For each thread, use `repo_list_pull_request_thread_comments` with `repositoryId: ((REPO))`, `pullRequestId: ((PR_ID))`, and `threadId` from step 3

### PR Information Summary Format

After gathering the data, organize it as follows:

**PR Metadata:**
- **Title:** [PR title]
- **Author:** [PR author]
- **Branch:** [head ref] → [base ref]
- **State:** [open/closed/merged]
- **Head SHA:** [commit SHA for review submissions]

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
`([Guideline](https://dev.azure.com/{organization}/{project}/_git/{repository}?path=/.augment/code_review_guidelines.yaml&version=GB{sourceBranch}): <guideline_id>)`

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

```
<!-- augment-pr-summary -->
<details>
<summary><b>🤖 Augment PR Summary</b></summary>

<br>

<b>Summary:</b> [One sentence describing the PR]

<b>Changes:</b>
<ul>
<li>[Key change 1]</li>
<li>[Key change 2]</li>
</ul>
</details>
```

If a section has no findings, omit it entirely.

## Guidelines

- Be specific: Include file paths, line numbers, and code snippets
- Be constructive: Explain *why* something is problematic and suggest fixes
- Be thorough but focused: Don't nitpick style if there are real bugs
- Consider context: Understand the intent before criticizing the approach
- Skip low-severity issues unless they indicate a pattern

## Step 6: Post Your Review

After completing your analysis, post your review with inline comments to Azure DevOps.

### Step 6a: Check for Existing Summary Comment

First, check if a PR summary comment already exists:

1. **List existing PR threads:**
   Use `repo_list_pull_request_threads` with `repositoryId: ((REPO))` and `pullRequestId: ((PR_ID))`

2. **Search for the marker:** Look for a thread containing `<!-- augment-pr-summary -->` in its first comment body.

3. **If found:** Note the thread `id` to update it in Step 6b.

### Step 6b: Post or Update the Summary Comment

**If an existing summary comment was found (has the marker):**
   Use `repo_update_pull_request_thread` with:
   - `repositoryId`: ((REPO))
   - `pullRequestId`: ((PR_ID))
   - `threadId`: The thread ID from Step 6a
   - `content`: The updated summary (see format below)

**If no existing summary comment exists:**
   Use `repo_create_pull_request_thread` with:
   - `repositoryId`: ((REPO))
   - `pullRequestId`: ((PR_ID))
   - `content`: The summary comment body (see format below)
   - `status`: "Active"

and note the thread `id` from the response.

**Summary comment format:**
```
<!-- augment-pr-summary -->
<details>
<summary><b>🤖 Augment PR Summary</b></summary>

<br>

<b>Summary:</b> [Your summary here]

<b>Changes:</b>
<ul>
<li>[Change 1]</li>
<li>[Change 2]</li>
</ul>

<sub>🤖 Was this summary useful? React with 👍 or 👎</sub>
</details>
```

### Step 6c: Post Inline Review Comments

**Create inline review comments as threads:**

For each inline comment, use `repo_reply_to_comment` with:
- `repositoryId`: ((REPO))
- `pullRequestId`: ((PR_ID))
- `threadId`: The thread ID from Step 6a or 6b
- `content`: Your inline comment text
- `filePath`: Path to the file (e.g., "path/to/file.ts")
- `rightFileStartLine`: Line number where the comment should appear
- `rightFileStartOffset`: Character offset (typically 1)
- `rightFileEndLine`: Same as startLine for single-line comments
- `rightFileEndOffset`: Character offset for end of range
- `status`: "Active"

**Example:**
```
repo_create_pull_request_thread(
  repositoryId: "repo-id",
  pullRequestId: 123,
  content: "Your inline comment here",
  filePath: "path/to/file.ts",
  rightFileStartLine: 45,
  rightFileStartOffset: 1,
  rightFileEndLine: 45,
  rightFileEndOffset: 1,
  status: "Active"
)
```

### Comment Field Reference

- `filePath`: File path relative to repository root
- `rightFileStartLine`: Line number in the new version of the file where the comment should appear
- `rightFileStartOffset`: Character offset within the line (use 1 for start of line)
- `rightFileEndLine`: End line number (same as startLine for single-line comments)
- `rightFileEndOffset`: Character offset for end of range
- `content`: The comment text
- `status`: Use "Active" for new comments

### Common Errors to Avoid

- **Do NOT** create duplicate threads for the same file/line combination
- **Do NOT** omit required position parameters (`rightFileStartLine`, etc.) when commenting on specific lines
- **Do NOT** use `leftFile*` parameters unless commenting on deleted lines
- **Always** check for existing threads before creating new ones to avoid duplicates
- **Always** use the `<!-- augment-pr-summary -->` marker at the start of the summary comment body
- **Always** set `status` to "Active" for new review comments