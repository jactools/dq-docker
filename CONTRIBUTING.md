# Contributing

Quick notes for developers working on this repository.

Running tests locally

- The runtime requires a data source mapping to be selected via the
  `DQ_DATA_SOURCE` environment variable. There are per-source YAML files
  under `dq_docker/config/data_sources/` (for example
  `ds_sample_data.yml`).

- Install dev dependencies (recommended inside a venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

- Run the full test suite (sets the required environment variable):

```bash
export DQ_DATA_SOURCE=ds_sample_data
PYTHONPATH=. pytest
```

Why `DQ_DATA_SOURCE` is required

- The package intentionally fails fast when a data source is not
  configured to avoid silent default behavior. Set `DQ_DATA_SOURCE` to
  one of the filenames (without extension) in
  `dq_docker/config/data_sources/`.

If you add new data sources

- Add a new YAML file to `dq_docker/config/data_sources/` named
  `ds_your_source.yml` containing the required mapping keys:
  `source_folder`, `asset_name`, `batch_definition_name`,
  `batch_definition_path`, `expectation_suite_name`, `definition_name`.

- Add any necessary CI updates if the new data source requires extra
  provisioning.

Questions or issues

- Open an issue or start a discussion in the repository for larger
  design decisions (for example, if you'd prefer an alternate config
  format or lazy-loading behavior).