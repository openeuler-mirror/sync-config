# sync-config

This is a repository for sync configuration — mirroring repos from Gitcode to GitHub.

## Mirror Sync Status

<!-- SYNC_STATUS_START -->
**Last updated:** 2026-07-15T02:31:12Z
**Flow:** `gitcode/openeuler` → `github/openeuler-mirror`
**Status:** ✅ All repos synced successfully

| Total | ✅ Synced | ❌ Failed | ⏭️ Skipped |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 0 | 0 |

📊 [查看详细同步状态（含失败原因诊断）](https://huanglei0308.github.io/community-mirror/community.html?org=openEuler)

---

<details>
<summary><b>✅ Synced Repos (1)</b></summary>

- `stratovirt`

</details>


<!-- SYNC_STATUS_END -->

## How It Works

This repository uses scripts from [community-mirror](https://github.com/huanglei0308/community-mirror) (mainly `mirror_repos.py`) to mirror repositories from `gitcode/openeuler` to `github/openeuler-mirror`. The scripts are checked out at runtime — no local copy needed.

### Workflows

| Workflow | Schedule | Description |
|----------|----------|-------------|
| `repo-mirror.yml` | Daily at 01:00 UTC | Splits all repos into batches of 80, mirrors in parallel (matrix strategy), merges results, updates this README |
| `large-repo-mirror.yml` | Daily at 01:00 UTC | Mirrors 5 large repos (kernel, qemu, etc.) with 1h timeout per repo |
| `high.yml` | Every 2 hours | Mirrors high-priority repo (stratovirt) with quick turnaround |

Each workflow uses `mirror_repos.py` to sync code, `diagnose_failures.py` to classify failures, and `merge_results.py` to merge with gh-pages so no workflow overwrites another's results.

### Status Tracking

Sync status is automatically updated in this README after each `repo-mirror` run. Failures are** categorised** (e.g. "File Too Large", "Push Protection Blocked") for easy triage. Results are also published to the [Community Mirror Hub](https://huanglei0308.github.io/community-mirror/).
