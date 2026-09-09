# J.A.R.V.I.S.

A local, clap-activated personal assistant for Windows, written in Python.
No cloud dependency for the core system — claps in, actions out, entirely
on-device.

## What it does

The system listens continuously through the microphone and recognizes claps
by their acoustic shape (a sharp attack, a short duration window, a fast
decay) rather than a fixed volume threshold — this is what lets it tell a
clap apart from a door slam or a raised voice. A configurable number of
claps in a short window triggers a named protocol: open an application on a
specific monitor, play an audio cue, ask a local LLM a question and show the
answer as a native notification.

It also runs a persistent state machine (`DORMINDO` → `EXECUTANDO` →
`DORMINDO`), so the microphone is intentionally deaf to its own protocol's
sound effects while one is running, and automatically recovers if the audio
device drops out mid-session (a Bluetooth headset disconnecting, for
example) instead of crashing.

## Highlights

- **Signal processing without a framework.** The clap detector is a small,
  from-scratch peak detector over raw microphone amplitude — attack
  threshold, duration window, decay threshold — tuned against synthetic
  test signals (`tests/test_clap_detector.py`) that model a good clap, a
  weak clap, continuous speech, and a door slam, so sensitivity tuning
  never regresses silently.
- **State machine over a live audio stream.** A `threading`-safe loop reads
  the mic via `sounddevice`, gates clap detection by system state, and
  recovers from stream failures (explicit exceptions *and* streams that go
  silently dead) with a watchdog and backoff retry.
- **Windows automation via `pywin32`/`pygetwindow`.** Multi-monitor window
  placement, active-monitor detection by cursor position, and a
  retry-with-backoff wrapper around `SetWindowPos` calls, because Windows
  occasionally (and transiently) refuses to move a window that's still
  settling after launch.
- **A real command surface, not just claps.** The same protocols are
  reachable from a CLI (`executar_protocolo.py`), a system tray icon
  (pause/resume/quit via `pystray`), global hotkeys (`keyboard`), and a
  filesystem-watched "trigger folder" that turns any synced cloud-storage
  folder into a remote trigger from a phone — no companion app, no new
  account.
- **A safe-mode that's actually load-bearing.** Every action-performing
  class has a drop-in "announce, don't execute" counterpart
  (`AcoesSimuladas`), switchable per-run (`--dry-run`) or via config
  (`modo_seguro`), so new protocols and refactors can be exercised end to
  end without opening a single window or making a sound.
- **A local-LLM bridge that fails usefully.** Before ever shelling out to
  the local assistant CLI, the bridge checks that the command is on `PATH`
  and that the inference server is actually listening — and if it isn't,
  it tries to start it itself before giving up with a specific, actionable
  message instead of a generic "no response."

## Architecture

```
jarvis.py                  Persistent loop: mic -> ClapDetector -> state machine -> protocol
executar_protocolo.py      Run any protocol on demand, no claps required
core/clap_detector.py      Peak detector: attack, duration window, decay
core/maquina_estados.py    DORMINDO / ESCUTANDO / EXECUTANDO state machine
core/protocols.py          Protocol definitions; dispatch by name or by clap count
core/actions.py            App launching, window placement, audio playback
core/acoes_simuladas.py    Drop-in "announce, don't execute" counterpart to actions.py
core/window_control.py     Multi-monitor placement, active-monitor detection, retry logic
core/bandeja.py            System tray icon: pause/resume/quit, native notifications
core/atalho_teclado.py     Global keyboard shortcuts, config-driven
core/gatilho_celular.py    Filesystem-watched folder as a remote trigger
core/jarvis_bridge.py      Bridge to a local LLM assistant CLI, with health checks
core/lockscreen.py         Refuses to trigger while the workstation is locked
core/logger.py             Rotating log with an optional elapsed-time verbose mode
tests/test_clap_detector.py Synthetic-signal regression tests for the detector
```

## Requirements

- Windows 10/11
- Python 3.11+
- A working microphone
- `pip install -r requirements.txt`

## Running it

```
python jarvis.py                 # start the persistent listener
python jarvis.py --dry-run       # same, but announces instead of acting
python jarvis.py --verbose       # same, with elapsed-time logging

python executar_protocolo.py --listar
python executar_protocolo.py <protocolo> --simular
```

Protocols, clap-count mapping, monitor assignment, and detector sensitivity
are all defined in `config.json` — nothing about a specific protocol's
behavior is hardcoded against a particular application beyond what's in
that file.

## Testing

```
python tests/test_clap_detector.py
```

No microphone or external service required — the suite feeds synthetic
volume/time sequences directly into the detector and asserts on the
resulting clap count.

---

Built as one part of a larger personal-automation project alongside a local
LLM assistant and a personal knowledge base, neither of which is included
here.
