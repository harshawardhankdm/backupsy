# backupsy

A small, dependable CLI that backs up folders to S3-compatible storage — AWS S3, Backblaze B2, or MinIO — with automatic rotation of old backups and optional Slack/Discord alerts.

No servers to run, no daemons, no dashboard. Point it at a folder, point it at a bucket, put it on a cron job or a scheduled GitHub Action, and forget about it.

## Features

- 📦 Archives one or more folders into a timestamped `tar.gz`
- ☁️ Uploads to any S3-compatible endpoint (AWS S3, Backblaze B2, MinIO, etc.)
- 🔄 Rotation: keep the last N backups, and/or delete anything older than N days
- 🧪 Dry-run mode — see exactly what would happen before it touches anything
- 🔔 Optional webhook notification on success/failure (Slack or Discord format)
- ⚙️ Single YAML config file; secrets stay in environment variables, never in the file

## Install

```bash
pip install backupsy
```

Or from source:

```bash
git clone https://github.com/YOUR_USERNAME/backupsy.git
cd backupsy
pip install -e .
```

## Quickstart

1. Generate a starter config:

   ```bash
   backupsy init
   ```

2. Edit `config.yaml` — set your source folder(s) and your S3 bucket details.

3. Set your credentials as environment variables (names are configurable, these are the defaults):

   ```bash
   export BACKUPSY_S3_ACCESS_KEY=your-access-key
   export BACKUPSY_S3_SECRET_KEY=your-secret-key
   ```

4. Try a dry run first:

   ```bash
   backupsy run --config config.yaml --dry-run
   ```

5. Run it for real:

   ```bash
   backupsy run --config config.yaml
   ```

## Configuration reference

See [`config.example.yaml`](./config.example.yaml) for a fully commented example. Key sections:

| Section       | Purpose                                                              |
|---------------|-----------------------------------------------------------------------|
| `source`      | Folders to back up, and glob patterns to exclude                     |
| `archive`     | Naming for the generated archive                                     |
| `destination` | Bucket, prefix, endpoint (set `endpoint_url` for B2/MinIO), region    |
| `rotation`    | `keep_last` and/or `keep_days` — how many old backups to retain      |
| `notify`      | Webhook URL (env var name) for Slack/Discord alerts                  |
| `logging`     | Log level and optional log file                                      |

### Using Backblaze B2 or MinIO instead of AWS S3

Just set `endpoint_url` in your config, e.g.:

```yaml
destination:
  type: s3
  bucket: my-bucket
  endpoint_url: https://s3.us-west-000.backblazeb2.com   # Backblaze B2 example
  region: us-west-000
```

## Running on a schedule

**Cron (Linux/macOS):**

```cron
0 3 * * * BACKUPSY_S3_ACCESS_KEY=xxx BACKUPSY_S3_SECRET_KEY=yyy /usr/local/bin/backupsy run --config /home/you/config.yaml >> /home/you/backupsy.log 2>&1
```

**GitHub Actions:** copy [`.github/workflows/scheduled-backup.yml.example`](./.github/workflows/scheduled-backup.yml.example) into your own repo as `.github/workflows/backup.yml`, add your `config.yaml`, and set the referenced secrets in your repo settings.

## Roadmap

- [ ] Local disk / external drive backend
- [ ] Remote server via SSH/rsync backend
- [ ] Encryption at rest before upload
- [ ] Database dump support (Postgres/MySQL) as a source type

Contributions adding any of the above are very welcome — see below.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

The rotation logic and config loading are pure functions with no I/O, so they're fully covered by unit tests without needing real S3 credentials. `moto` is included as a dev dependency for anyone who wants to add tests that mock actual S3 calls.

## Contributing

Issues and PRs are welcome. If you're adding a new storage backend, implement the `StorageBackend` interface in `backupsy/storage/base.py` and wire it into `build_storage_backend()` in `backupsy/storage/__init__.py` — the CLI, rotation, and notification logic won't need to change.

## License

MIT — see [LICENSE](./LICENSE).
