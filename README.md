# sync-config

This is a repository for sync configuration — mirroring repos from Gitcode to GitHub.

## Mirror Sync Status

<!-- SYNC_STATUS_START -->
**Last updated:** 2026-06-05T05:21:52Z
**Flow:** `gitcode/openeuler` → `github/openeuler-mirror`
**Status:** ✅ All repos synced successfully

| Total | ✅ Synced | ❌ Failed | ⏭️ Skipped |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 0 | 0 |

<details>
<summary><b>✅ Synced Repos (1)</b></summary>

- `stratovirt`

</details>


<!-- SYNC_STATUS_END -->

## How It Works

This repository uses [Yikun/hub-mirror-action](https://github.com/Yikun/hub-mirror-action) to mirror repositories from `gitcode/openeuler` to `github/openeuler-mirror`.

### Workflows

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `repo-mirror.yml` | Daily at 01:00 UTC | Mirrors all repos except large ones (kernel, qemu, etc.) |
| `large-repo-mirror.yml` | Daily at 01:00 UTC | Mirrors large repos with extended timeout |
| `high.yml` | Every 2 hours | Mirrors high-priority repos (stratovirt) |
| `status-deploy.yml` | Daily at 01:30 UTC | Generates and deploys the status dashboard |

### Status Tracking

After each mirror run, a status checker script independently queries both the source (Gitcode) and destination (GitHub) APIs to verify which repositories have been successfully mirrored. Results are published to the [status dashboard](https://openeuler-mirror.github.io/sync-config/) via GitHub Pages.

> **Note:** To enable the status dashboard, go to repo **Settings → Pages** and set the source to the `gh-pages` branch.
