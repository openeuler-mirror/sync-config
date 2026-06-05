# sync-config

This is a repository for sync configuration — mirroring repos from Gitcode to GitHub.

## Mirror Sync Status

<!-- SYNC_STATUS_START -->
**Last updated:** 2026-06-05T06:07:03Z
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

### Status Tracking

Sync status is automatically checked after each mirror run and displayed above. Results are also published to the [Community Mirror Hub](https://huanglei0308.github.io/community-mirror/).
