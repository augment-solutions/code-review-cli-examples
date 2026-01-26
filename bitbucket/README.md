# Augment Code Review for Bitbucket

This guide walks you through how to set up the **Auggie CLI** with Bitbucket for automatically generating code review comments after a pull request.

![Bitbucket Code Review Screenshot](./screenshot.png)

---

## Prerequisites

### 1. Enable Pipelines & Configure Runners

Before running any pipelines, you must ensure your Bitbucket workspace or repository is configured to use runners.

* **Cloud Runners:** If you are using Bitbucket Cloud, simply enabling Pipelines in **Repository settings** \> **Pipelines** \> **Settings** will automatically allow you to use Atlassian’s hosted cloud runners.  
* [**Self-Hosted Runners**](https://support.atlassian.com/bitbucket-cloud/docs/adding-a-new-runner-in-bitbucket/)**:** If your organization requires a self-hosted runner (e.g., for security compliance or VPC access), ensure the runner is "Online" in your **Workspace** or **Repository settings** \> **Pipelines** \> **Runners** and tag it correctly in your pipeline configuration (e.g. add `runs-on: [self.hosted, linux]` to the step).

### 2. Retrieve your Auggie Token

[Install Auggie locally](https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli) first, if needed. And run the following commands on your *local* machine:

```shell
# Log in if you haven't already
auggie login

# Print your session token
auggie tokens print
```

*Copy the output token string for step 4\.*

### 3. Create an Access Token in Bitbucket

You can define Access tokens on [Repository](https://support.atlassian.com/bitbucket-cloud/docs/create-a-repository-access-token/), [Project](https://support.atlassian.com/bitbucket-cloud/docs/create-a-project-access-token/), or [Workspace](https://support.atlassian.com/bitbucket-cloud/docs/create-a-workspace-access-token/) level in Bitbucket. Once you have created one, make sure to copy the token, as it will be used in the next step as a variable.

The Access token can either be unscoped or scoped. If using the latter, specify the following scopes:

* Read:  
    * `read:pullrequest:bitbucket`  
    * `read:repository:bitbucket`  
* Write:  
    * `write:pullrequest:bitbucket`

Alternatively, you can also define an [API token](https://support.atlassian.com/bitbucket-cloud/docs/api-tokens/), but generally Access Tokens are preferred as these are not user-based.

### 4. Add Auggie token & Bitbucket Access token to Bitbucket [Workspace-](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/#Workspace-variables) or [Repository variables](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/#Repository-variables)

You can use either workspace- or repository variables. Choose one.

* Option A. To use Repository variables:  
    * Go to your Bitbucket repository.  
    * Navigate to **Repository settings** \> **Pipelines** \> **Repository variables**.  
* Option B. To use Workspace variables:  
    * Go to your Bitbucket workspace  
    * Navigate to **Workspace settings \> Workspace variables**.  
* Add a new variable:  
    * **Name:** `AUGMENT_SESSION_AUTH`  
    * **Value:** *(Paste your token from step 2 here)*  
    * **Secured:** Checked (Recommended to hide the secret in logs)  
* Add another variable:  
    * **Name:** `BB_TOKEN`  
    * **Value:** *(Paste your token from step 3 here)*  
    * **Secured:** Checked (Recommended to hide the secret in logs)   
* Optional: if you’re using API tokens instead of Access tokens, add the variable:  
    * **Name:** `BB_USER_EMAIL`  
    * **Value:** Your Bitbucket email address

---

## Pipeline Configuration

Create or update the [`bitbucket-pipelines.yml`](https://support.atlassian.com/bitbucket-cloud/docs/configure-your-runner-in-bitbucket-pipelines-yml/) file in the root of your repository with the content below.

This configuration uses the official `node:22-alpine` Docker image and installs Augment as the pipeline runs. Feel free to use any other image as long as it’s able to (install and) run Auggie.

This pipeline runs on all pull requests, but [starting conditions](https://support.atlassian.com/bitbucket-cloud/docs/pipeline-start-conditions/#Pull-Requests) can be adjusted as needed.

There are two examples provided, one using Access Tokens and one using API Tokens:
- `bitbucket-pipelines-access-token.yml`
- `bitbucket-pipelines-api-token.yml`

---

## Appendix

### A. Adding Rules & Guidelines

Configure custom [rules & guidelines](https://docs.augmentcode.com/codereview/review-guidelines) to help Augment Code Review focus on specific areas and domain knowledge. Additionally, certain files are automatically skipped (e.g. .lock & .log files) during reviews but you can configure additional file exclusions.

The easiest way to persist rules for your pipeline is to commit them to your repository.

1. **Create an Augment Directory:** Create a folder named `.augment in the root of your repository.  
2. **Add Rules & Guidelines File:** Create `code_review_guidelines.yaml` file inside this folder. Auggie automatically detects and applies all rules found here. 

For a complete working example, see the [Code Review Best Practices repository]((https://github.com/augmentcode/code-review-best-practices/blob/main/code_review_guidelines.example.yaml).

### B. Adding Tools / MCP

Auggie supports the [**Model Context Protocol**](https://docs.augmentcode.com/cli/integrations) **(MCP)**, which allows it to connect to external tools (like database connectors, browser automation, or third-party APIs) during execution.

Since Docker runners are ephemeral (fresh environment every time), you must configure these integrations within the pipeline script before running your main Auggie command.

**Setup for Pipelines:** Add the `auggie mcp add` command to your pipeline script steps. This installs the integration for that active session.

**`bitbucket-pipelines.yml` with MCP Example:**

```
...
      - step:
        name: Run Auggie for Code Review with MCP
        script:
	     - |
		 ...
		 # run below steps after Auggie is installed and before auggie is run to generate the code review
            # Example: Add a 'Sequential Thinking' tool via MCP (requires npx)
            # This registers the tool so the agent can use it during the next command
            - auggie mcp add sequential-thinking --command npx --args "-y @modelcontextprotocol/server-sequential-thinking"

            # Example: Add a Database tool (requires env vars for connection)
            # - auggie mcp add postgres --command npx --args "-y @modelcontextprotocol/server-postgres" --env POSTGRES_URL=$DB_CONNECTION_STRING

            # Verify MCP setup (Optional)
            - auggie mcp list
```

**Note on Native Integrations (GitHub, Linear, etc.):** If you have connected native integrations (like GitHub or Linear) via the Augment VS Code or JetBrains extension, those connections are tied to your **Augment Session Token**. As long as `AUGMENT_SESSION_AUTH` is correctly set in your Bitbucket Repository Variables, the CLI in the pipeline will automatically inherit permissions to read/write to those services without extra configuration.
