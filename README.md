# Bulk File Renamer

A Python CLI tool for bulk renaming files with customizable prefixes, suffixes, numbering, and file-extension filters.

## Features

- Rename files in a directory in one operation
- Add prefixes and suffixes
- Sequential numbering with configurable starting numbers and padding
- Filter files by extension
- Preview changes with a dry-run mode
- Prevent accidental filename collisions
- Optional recursive directory processing
- Cross-platform path handling
- Automated tests with pytest
- GitHub Actions CI

## Usage

Run the CLI with:

```bash
bulk-renamer ./photos --prefix vacation --number
```

Preview changes without modifying files:

```bash
bulk-renamer ./photos --prefix vacation --number --dry-run
```

Run `bulk-renamer --help` for all options.

## Development

Install the project in editable mode:

```bash
pip install -e ".[dev]"
```

Run tests:

```pytest
```

Run linting:

```bash
ruff check .
```

## License

MIT
