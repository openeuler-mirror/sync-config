# sync-config

This is a repository for sync configuration — mirroring repos from Gitcode to GitHub.

## Mirror Sync Status

<!-- SYNC_STATUS_START -->
> ⚠️ No sync status data available yet. Data will appear after the next scheduled mirror run.
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
