# PhonePe Transaction Insights

Warehouse and dashboard for PhonePe Pulse. Aggregated, map, and top files are loaded into nine Postgres databases, one container per table.

## First run

Install Python 3.11+ and Docker, start Docker, then from this folder:

```bash
bash run.sh
```

The dashboard opens at http://localhost:8501. The script creates `.venv`, installs packages, starts the databases, and loads the data. Run it again any time.

`bash scripts/teardown.sh` stops the containers. `bash scripts/setup.sh --reset` reloads the data without opening the app. `scripts/download_data.sh` clones [PhonePe Pulse](https://github.com/PhonePe/pulse) when `data/pulse` is missing.

Tests:

```bash
python -m pytest
```

Ports are 5601–5609. See `.env.example`.

The written snapshot is `reports/findings.md`. The handover note is `kt.md`.
