# Useful Xperia applications across the Mero stack

Research snapshot: 2026-10-26. These are proposals, not installed applications. The U20a runs Android 1.6 on an ARMv6-class CPU, has about 166 MiB of kernel-visible RAM, a 240 × 320 screen, and a physical keyboard. USB ADB works; Wi-Fi (`tiwlan0`) was down during this inspection. The phone should render short results while desktop/Pi services do the expensive work.

## Strong candidates

| Idea | Phone view/action | Existing host source | First-slice difficulty |
| --- | --- | --- | --- |
| **Pocket GitHub monitor** | Recent commits, open/recently updated issues and PRs, a small attention list | Authenticated `gh` on the desktop; selected repo allowlist | Low to medium |
| **Agent pager** | Working, blocked, and idle agents; short blocker labels | `mero-pi` Herdr state reports; selected Mero operator observations | Medium |
| **Stack health card** | LLMero service up/down, queued work, backup/check status | Host-side process and service probes | Low once the display bridge exists |
| **Pocket capture** | Type a note or task with the keyboard, sync later | Host inbox/second-brain importer | Medium; needs a return channel and duplicate handling |
| **PR triage remote** | Read a PR summary, queue “open on desktop” or a draft note | GitHub CLI and desktop bridge | Medium; any write needs explicit confirmation |

The first recommendation is **Pocket GitHub monitor**. It answers a real question in a glance: “What changed in my projects, and what needs my attention?” It also establishes the display, data contract, and transport needed by the other ideas. A push is a branch update; polling recent commits can show new commits, while a later webhook can record exact push events. The UI should label these accurately.

## Why the phone needs a bridge

- The existing Mero Protocol Hub uses an authenticated WebSocket on `127.0.0.1`. Its server currently keeps one client session and closes the old session when a new one connects. The Xperia must not connect directly or carry that bearer token.
- `mero-pi` already reports agent `working`, `blocked`, and `idle` states to a local Unix socket when Herdr runs. A desktop/Pi adapter could summarize those states without exposing the socket to the handset.
- `LLMero` defaults to a loopback `llama-server`. The phone should see a health summary or a curated answer, not the model server or its full API.
- The host's `gh` CLI is installed and authenticated. Read-only issue and PR queries worked for `zacmero/mero-xperia`. The phone needs no GitHub token.

## First vertical slice: USB activity card

1. A host collector reads an explicit list of repositories with `gh`. It records latest default-branch commits, open/recently updated issues, and PRs. It keeps only short titles, numbers, states, timestamps, and repository names. No issue bodies, comments, credentials, or private file paths are sent.
2. The collector produces a bounded versioned snapshot: at most five repositories, five attention items, and short text fields. It includes `generatedAt` and `expiresAt` so the phone can mark stale data.
3. Over the already working USB link, the host sends the compact snapshot to a small Android 1.6 app with `adb shell am broadcast`. This phone's `am` supports string extras. Hex encoding the UTF-8 payload keeps dynamic GitHub titles out of remote shell syntax.
4. The app renders a large-text list suited to 240 × 320 pixels and the physical arrow keys. It caches the last good snapshot and shows its age when unplugged. A tap or key opens details; no GitHub write action exists in this slice.

Example screen layout:

```text
MERO / ACTIVITY       02:45
2 repos changed       1 alert

> mero-xperia
  new commit · backup notes

  mero-pi
  PR #42 · review needed

  AGENTS  2 working · 1 blocked

[Up/Down] select  [Enter] open
```

The example values are illustrative, not current GitHub or agent state.

**Acceptance check:** the host can generate a snapshot for one allowlisted repo; the phone displays it; a subsequent update replaces it; disconnecting USB leaves a readable cached snapshot with a stale indicator. No system partition changes or phone-side account login are needed.

## Later transport and controls

Wi-Fi can make the monitor untethered after we verify this phone's connection to the trusted LAN. A small gateway should expose only the curated snapshot, use explicit pairing/access controls, and keep GitHub/agent credentials on the host. Android 1.6's old networking stack is a reason to avoid direct modern cloud APIs from the phone. Bluetooth file transfer worked for a PNG, but it has not been established as a reliable live app transport.

Agent replies, issue creation, PR comments, and approvals can be added after a return channel exists. Keep those operations in a host queue with a visible confirmation step. The first app is a monitor.
