# AGENTS.md

## Project Overview

| Field | Value |
|---|---|
| **Name** | Stocks — Taiwan Stock Real-Time Monitor |
| **Organization** | StockMuffin |
| **Language** | Python 3.13 |
| **GUI Framework** | PySide6 (Qt for Python) |
| **Compiler/Packager** | Nuitka |
| **Package Manager** | uv (CI) / pip (local) |
| **Target Platforms** | Windows (.exe), macOS (.app) |
| **Entry Point** | `main.py` |

A lightweight desktop app for monitoring Taiwan Stock Exchange (TWSE) quotes in real time. Data is fetched from Yahoo Finance Taiwan's unofficial API and refreshed every 10 seconds during market hours.

---

## Repository Layout

```
stocks/
├── main.py                        # Entry point: creates QApplication, launches StockUI
├── requirements.txt               # Python dependencies
├── icon.ico                       # Windows app icon
├── icon.png                       # macOS app icon
├── .github/workflows/
│   └── python-app.yml             # CI/CD: build & release via GitHub Actions
└── src/
    ├── __init__.py
    ├── app_settings.py            # SettingsManager — persistent JSON config
    ├── data.py                    # StockFetcher, FetchStockData (QRunnable)
    ├── main_ui.py                 # StockUI — top-level QWidget
    ├── settings_dialog.py         # SettingsDialog — preferences modal
    ├── stock_table.py             # StockTable — table widget + window sizing
    ├── stock_table_model.py       # StockTableModel — QAbstractTableModel
    └── upper.py                   # AddStocks — input bar + buttons
```

---

## Module Reference

### `main.py`

No business logic. Selects the correct icon path per platform (`icon.ico` on Windows, `icon.png` elsewhere), instantiates `StockUI`, and starts the Qt event loop.

---

### `src/app_settings.py` — `SettingsManager`

Stores config as JSON at `QStandardPaths.AppConfigLocation/settings.json`.

**Schema:**

```json
{
    "stock_ids": ["^TWII", "2330"],
    "show_market_index": true,
    "enable_price_color": true
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `stock_ids` | `list[str]` | `[]` | Ordered list of tracked symbols |
| `show_market_index` | `bool` | `true` | Pin `^TWII` at index 0 of the list |
| `enable_price_color` | `bool` | `true` | Color the price column red/green |

**Behaviors:**
- When `show_market_index` is toggled, `^TWII` is inserted at or removed from `stock_ids[0]` automatically.
- On first run, if legacy `QSettings` data (`ID` key) exists, it is migrated to JSON and the old entry is left in place.
- When adding a new config key, **always** add its default to `default_settings` to preserve backward compatibility.

**Public API:**

```python
save_stock_id(stock_id: list)
load_stock_id() -> list
save_show_market_index(enabled: bool)
load_show_market_index() -> bool
save_enable_price_color(enabled: bool)
load_enable_price_color() -> bool
```

---

### `src/data.py` — `StockFetcher` + `FetchStockData` + `FetchBatchStockData`

**`StockFetcher`** is instantiated once at module level (`stock_fetcher`) and shared across all threads.

`fetch(stock_id)` dispatches to:

| Condition | Method | API endpoint |
|---|---|---|
| `stock_id` starts with `^` | `_fetch_index()` | `FinanceChartService.ApacLibraChartIndex` |
| Otherwise | `_fetch_stock()` | `StockServices.stockList` |

`fetch_batch(stock_ids)` batches regular stock queries into a single comma-separated `StockServices.stockList` request while querying any index symbols individually.

Both methods return 9-element list(s):

```python
[stock_id, name, price, change_pct, day_high, day_low, open_price, volume, turnover]
#    0       1      2       3           4         5         6          7       8
```

On any exception, a placeholder list is returned with `"-"` for all fields except `stock_id`. The app never crashes on network failure.

**Unit conversions:**
- Volume: raw value `// 1000` → unit is **lots (張)**
- Turnover: `turnover_calculator()` converts from million TWD to hundred million (億); uses 2 decimal places if `>= 100`, otherwise 3.

**`FetchStockData(QRunnable)`** wraps a single `stock_fetcher.fetch()` call. Results are emitted via `data_signal` (a Qt Signal) back to the main thread.
**`FetchBatchStockData(QRunnable)`** wraps `stock_fetcher.fetch_batch()` to fetch multiple symbols in a single batch request and emit results per symbol via `data_signal`.

---

### `src/main_ui.py` — `StockUI`

**Layout:**
```
StockUI (QVBoxLayout)
├── AddStocks    (upper panel)
└── StockTable   (lower panel)
```

**Signal wiring:**

| Source | Signal | Slot | Effect |
|---|---|---|---|
| `AddStocks` | `stock_added` | `StockTable.add_stock` | Append row + immediate fetch |
| `AddStocks` | `stock_removed` | `StockTable.remove_stock` | Remove row |
| `AddStocks` | `settings_changed` | `StockTable.reload_table` | Full table reload |
| `QTimer` (10 s) | `timeout` | `StockTable.decide_update` | Market-hours auto-refresh |

---

### `src/stock_table.py` — `StockTable`

**Table columns (index → header):**

| Index | Header | Notes |
|---|---|---|
| 0 | 股票代號 | Symbol |
| 1 | 股票名稱 | Name |
| 2 | 現價 | Price — colored if enabled |
| 3 | 漲跌幅 | Change % — used to derive color |
| 4 | 盤中最高 | Day high |
| 5 | 盤中最低 | Day low |
| 6 | 開盤價 | Open |
| 7 | 成交量 | Volume (lots) |
| 8 | 成交金額（億） | Turnover (hundred million TWD) |

**Initial window auto-sizing** runs in three deferred steps (each via `QTimer.singleShot(0, ...)`):
1. `_fit_initial_window_size()` — calls `resizeColumnsToContents()`
2. `_finish_initial_window_size_adjustment()` — computes delta and calls `window.resize()`
3. `_finalize_initial_window_size()` — applies final correction, re-enables scroll bars

This ensures Qt finishes laying out the table before any measurement is taken.

**Dynamic window sizing (post-initialization):**
- **Width auto-expansion (`_expand_window_width_if_needed`)**: Triggered in `handle_stock_data()`. If real-time value updates widen any column beyond the current viewport, the window width expands automatically (one-way expansion only; never shrinks) to prevent horizontal scrollbars. Debounced via `_width_expansion_pending` and `QTimer.singleShot(0, ...)`.
- **Height auto-adaptation (`_adjust_window_height`, `_schedule_height_adjustment`)**: Triggered on `add_stock()`, `remove_stock()`, and `reload_table()`. Recalculates total row height and expands or shrinks the window height accordingly (bounded by `window.minimumHeight()`) to prevent vertical scrollbars and eliminate empty gray space. Debounced via `_height_adjustment_pending` and `QTimer.singleShot(0, ...)`.

**`is_market_open()`** returns `True` on weekdays (Mon–Fri) between 09:00 and 13:40 local time. Public holidays are **not** accounted for.

---

### `src/stock_table_model.py` — `StockTableModel`

Extends `QAbstractTableModel`. Owns all data; no UI logic.

**Internal storage:**

```python
stock_order: list[str]        # display order
rows_by_id:  dict[str, list]  # stock_id → 9-element data list
```

**Color logic (`_price_color`):**
- Reads `stock_data[PERCENTAGE_COLUMN]` (index 3)
- Colors `PRICE_COLUMN` (index 2): `> 0` → `QColor("red")`, `< 0` → `QColor("green")`
- Returns `None` (no color) when disabled or when the value cannot be parsed

**`update_stock_data()`** emits `dataChanged` only for the updated row, avoiding full table repaints.

---

### `src/upper.py` — `AddStocks`

Input bar composed of a `QLineEdit` and three `QPushButton` widgets.

- Supports adding symbols by pressing **Enter** (`returnPressed`) or clicking the **添加股票** button.
- Validates symbol formats with a regex check before emitting `stock_added`.

**Symbol validation regex:**
```python
r'^\d{4,6}(?:[A-Za-z]+(?:\d+)?)?$'
```
Accepts 4–6 leading digits optionally followed by letters (and optional trailing digits). Examples: `2330`, `006208`, `00700B`. The `^TWII` index symbol bypasses this check entirely — it is managed by `SettingsManager`.

**Signals emitted:**

```python
stock_added   = Signal(str)   # valid new symbol confirmed
stock_removed = Signal(str)   # existing symbol removed
settings_changed = Signal()   # settings dialog accepted
```

---

### `src/settings_dialog.py` — `SettingsDialog`

Modal `QDialog` with two checkboxes:
1. **顯示大盤** — show/hide `^TWII` at row 0
2. **啟用漲跌幅顏色** — enable/disable price coloring

On **OK**: calls the relevant `SettingsManager.save_*` methods, emits `settings_changed`, then closes.
On **Cancel**: closes without saving.

---

## Data Flow

```
User types symbol → AddStocks.add_new_stocks()
  ├─ validate with regex
  ├─ persist via SettingsManager.save_stock_id()
  └─ emit stock_added
          │
          ▼
    StockTable.add_stock()
    ├─ StockTableModel.add_stock()   — insert placeholder row
    ├─ _schedule_height_adjustment() — auto-expand window height
    └─ QThreadPool.start(FetchStockData)
                    │  (worker thread)
                    ▼
           StockFetcher.fetch()  →  HTTP GET Yahoo Finance
                    │
                    ▼  (back on main thread via Signal)
           StockTable.handle_stock_data()
           ├─ StockTableModel.update_stock_data()
           │  └─ dataChanged → repaint affected row only
           └─ _expand_window_width_if_needed() — one-way width auto-expansion
```

**Periodic refresh:**
```
QTimer (10 s) → StockTable.decide_update()
  ├─ is_market_open()? No  → skip
  └─ Yes → QThreadPool.start(FetchBatchStockData) with all symbols (single batch request)
```

---

## CI/CD — `.github/workflows/python-app.yml`

Triggered manually via `workflow_dispatch` with a required `tag_name` input (e.g. `v1.2.0`).

Runs in parallel on two runners:

| Runner | Output artifact |
|---|---|
| `windows-latest` | `stocks_windows.zip` (contains `build/main.dist/`) |
| `macos-latest` | `stocks_macos.zip` (contains `build/main.app`) |

**Steps per runner:**
1. Checkout → setup uv + Python 3.13 → `uv pip install -r requirements.txt`
2. `uv run python -m nuitka` with `--standalone` + `--enable-plugin=pyside6`
   - Windows: `--windows-console-mode=disable`, `--windows-icon-from-ico=icon.ico`
   - macOS: `--macos-create-app-bundle`, `--macos-app-icon=icon.png`
   - Both: exclude all unused `PySide6.Qt*` submodules to minimize bundle size
3. Compress output → upload to GitHub Release via `softprops/action-gh-release@v2`

---

## Development Guidelines

### Thread Safety
- Never access Qt Widgets or the Model from inside `QRunnable.run()`.
- All cross-thread communication must go through Qt Signals.
- The global `stock_fetcher` shares one `requests.Session` across threads. Do not mutate its headers at runtime.

### MVC Boundaries
- `StockTableModel` — data only. No widget calls.
- `StockTable` — view/controller. Reads data exclusively through model's public methods.

### Config Changes
- Every new key in `settings.json` must have a default in `SettingsManager.default_settings`.
- `save_show_market_index()` has a side-effect on `stock_ids`; do not bypass it by writing `stock_ids` directly when changing market index visibility.

### Error Handling
- `StockFetcher` swallows all exceptions and returns a placeholder list. There is no logging framework — errors are printed to stdout only.

### File Editing
- Use the `replace` tool for all edits to existing files. Never overwrite a file wholesale.
- Do not implement anything before the user explicitly approves.

---

## Extension Patterns

### Add a new setting
1. Add the key + default to `SettingsManager.default_settings`
2. Implement `save_xxx()` / `load_xxx()`
3. Add a UI control in `SettingsDialog`
4. Call the new save method inside `accept_settings()`

### Add a new table column
1. Extend the return list in `StockFetcher._fetch_stock()` and `_fetch_index()`
2. Append the header string to `StockTable.headers`
3. Update any column-index constants in `StockTableModel` if needed

### Add a new data source
1. Add an `elif` branch in `StockFetcher.fetch()` based on symbol format
2. Implement `_fetch_xxx()` — must return a list of the same length as existing fetchers

---

## Dependencies

| Package | Purpose |
|---|---|
| `PySide6` | Qt bindings — Widgets, Signals/Slots, threading, settings paths |
| `requests` | HTTP client for Yahoo Finance API calls |
| `nuitka` | Compiles Python to native binary for distribution |
| `zstandard` | Compression backend used by Nuitka |
| `imageio` | Image I/O dependency (used during packaging) |
