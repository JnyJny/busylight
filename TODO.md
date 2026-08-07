# TODO

## `busylight` lint backlog (ruff)

`packages/busylight` was recently switched from a narrow ruff `select`
(`E`, `F`, `I`, `W`) to the same `["I", "ALL"]` baseline `busylight-core`
already used, via the new shared [ruff.toml](ruff.toml). That surfaced
523 pre-existing findings that were never being checked before. They're
selected (visible in `ruff check`, will show red in CI) but intentionally
not fixed yet — tracked here instead of silently ignored.

Reproduce: `cd packages/busylight && ruff check src tests`

By rule, most to least:

| Rule | Count | What |
|---|---|---|
| `ANN201` | 115 | Missing return type annotation, public function — **~105 of these are `test_*` functions missing `-> None`**; worth reconsidering as a `tests/*` per-file-ignore rather than fixing by hand, since annotating every test's trivial `None` return is low-value |
| `FAST002` | 62 | FastAPI dependency not using `Annotated[]` style |
| `PLC0415` | 43 | `import` not at module top-level |
| `TID252` | 33 | Relative imports (should be absolute) |
| `FAST001` | 30 | FastAPI route with redundant `response_model` |
| `D102` | 27 | Missing docstring, public method |
| `D413` | 20 | Missing blank line after docstring's last section |
| `D103` | 17 | Missing docstring, public function |
| `B904` | 16 | `raise` inside `except` without `from` |
| `D101` | 12 | Missing docstring, public class |
| `PT006` | 11 | Wrong type for `pytest.mark.parametrize`'s first arg |
| `PLR0917` | 19 | Too many positional arguments |
| `D107` | 10 | Missing docstring, `__init__` |
| `ARG001` | 9 | Unused function argument |
| `D202` | 8 | Blank line after function docstring |
| `SIM117` | 6 | Nested `with` should be a single statement |
| `D419` | 5 | Empty docstring |
| `B008` | 5 | `typer.Option(...)` call in argument default (framework pattern — likely another `extend-immutable-calls` candidate, not a real bug) |
| everything else | ~60 | Singles/low counts — `TRY003`, `RUF013`, `RSE102`, `D205`, `TC005`, `EM102`, `D404`, `ANN202`, `SIM105`, `S104`, `RUF006`, `PLW0603`, and more. Full list via the reproduce command above. |

`busylight-core` has one pre-existing, unrelated finding of its own:
`PLR0917` (too many positional arguments) in
`src/busylight_core/vendors/kuando/implementation/commands.py`.
