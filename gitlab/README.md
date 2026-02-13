# Augment Code Review for GitLab

This guide walks you through how to set up the **Auggie CLI** with GitLab for automatically generating code review comments after a merge request.

![GitLab Code Review Screenshot](./screenshot.png)

---

## Prerequisites

### 1. Retrieve your Auggie Token

[Install Auggie locally](https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli) first, if needed. And run the following commands on your *local* machine:

```shell
# Log in if you haven't already
auggie login

# Print your session token
auggie tokens print
```

*Copy the output token string for step 3.*

### 2. Create a GitLab Project Access Token

You can create an Access Token at the Project level in GitLab:

1. Go to your GitLab project → **Settings** → **Access Tokens**
2. Click **Add new token**
3. Configure the token:
   - **Token name:** `augment-code-review` (this name appears as the commenter)
   - **Expiration date:** Set as needed (or leave blank for no expiration)
   - **Role:** `Developer` or higher
   - **Scopes:** Select `api`
4. Click **Create project access token**
5. **Copy the token value** - you'll need it in the next step

### 3. Add Auggie token & GitLab Access token to GitLab CI/CD Variables

1. Go to your GitLab project → **Settings** → **CI/CD**
2. Expand **Variables**
3. Add a new variable:
   - **Key:** `AUGMENT_SESSION_AUTH`
   - **Value:** *(Paste your token from step 1 here)*
   - **Type:** Variable
   - **Protected:** Checked (if only running on protected branches)
   - **Masked:** Checked (Recommended to hide the secret in logs)
4. Add another variable:
   - **Key:** `GITLAB_PERSONAL_ACCESS_TOKEN`
   - **Value:** *(Paste your token from step 2 here)*
   - **Type:** Variable
   - **Protected:** Checked (if only running on protected branches)
   - **Masked:** Checked (Recommended to hide the secret in logs)

> **Important:** If testing on non-protected branches, uncheck "Protected" for both variables.

---

## Pipeline Configuration

Create or update the `.gitlab-ci.yml` file in the root of your repository with the content from the example file.

This configuration uses the official `node:22` Docker image and installs Augment as the pipeline runs. Feel free to use any other image as long as it's able to (install and) run Auggie.

This pipeline runs on all merge requests via the rule `if: '$CI_PIPELINE_SOURCE == "merge_request_event"'`, but [rules](https://docs.gitlab.com/ee/ci/yaml/#rules) can be adjusted as needed.

---

## Appendix

### A. Adding Rules & Guidelines

Configure custom [rules & guidelines](https://docs.augmentcode.com/codereview/review-guidelines) to help Augment Code Review focus on specific areas and domain knowledge. Additionally, certain files are automatically skipped (e.g. .lock & .log files) during reviews but you can configure additional file exclusions.

The easiest way to persist rules for your pipeline is to commit them to your repository.

1. **Create an Augment Directory:** Create a folder named `.augment` in the root of your repository.
2. **Add Rules & Guidelines File:** Create `code_review_guidelines.yaml` file inside this folder. Auggie automatically detects and applies all rules found here.

For a complete working example, see the [Code Review Best Practices repository](https://github.com/augmentcode/code-review-best-practices/blob/main/code_review_guidelines.example.yaml).

### B. Adding Tools / MCP

Auggie supports the [**Model Context Protocol**](https://docs.augmentcode.com/cli/integrations) **(MCP)**, which allows it to connect to external tools (like database connectors, browser automation, or third-party APIs) during execution.

Since Docker runners are ephemeral (fresh environment every time), you must configure these integrations within the pipeline script before running your main Auggie command.

**Setup for Pipelines:** Add the `auggie mcp add` command to your pipeline script steps. This installs the integration for that active session.

**`.gitlab-ci.yml` with MCP Example:**

```yaml
...
augment-pr-review:
  stage: review
  image: node:22
  before_script:
    - npm install -g @augmentcode/auggie
    - auggie --version
  script:
    - |
      # Add GitLab MCP server (already included in example)
      auggie mcp add gitlab \
        --command npx \
        --args "-y @zereight/mcp-gitlab" \
        --env GITLAB_PERSONAL_ACCESS_TOKEN="${GITLAB_PERSONAL_ACCESS_TOKEN}" \
        --env GITLAB_API_URL="${CI_API_V4_URL}"

      # Example: Add a 'Sequential Thinking' tool via MCP (requires npx)
      # This registers the tool so the agent can use it during the next command
      # auggie mcp add sequential-thinking --command npx --args "-y @modelcontextprotocol/server-sequential-thinking"

      # Example: Add a Database tool (requires env vars for connection)
      # auggie mcp add postgres --command npx --args "-y @modelcontextprotocol/server-postgres" --env POSTGRES_URL=$DB_CONNECTION_STRING

      # Verify MCP setup (Optional)
      - auggie mcp list

      # Run the code review
      - auggie --print --instruction-file review-prompt.md
```

**Note on Native Integrations (GitHub, Linear, etc.):** If you have connected native integrations (like GitHub or Linear) via the Augment VS Code or JetBrains extension, those connections are tied to your **Augment Session Token**. As long as `AUGMENT_SESSION_AUTH` is correctly set in your GitLab CI/CD Variables, the CLI in the pipeline will automatically inherit permissions to read/write to those services without extra configuration.

