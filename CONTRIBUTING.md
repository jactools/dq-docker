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

Production builds and embedding Data Docs

- The repository supports a production workflow that embeds a generated
  Great Expectations `data_docs` site into a dedicated `nginx` image so
  you can deploy a self-contained static site.

- Basic steps (local / CI):

  1. Generate Data Docs into `uncommitted/data_docs/local_site` for each
     site you want to publish (for example `ds_sample_data` ->
     `uncommitted/data_docs/local_site/ds_sample_data`). Customize the
     generation command to your project (see `.github/workflows/build-with-data-docs.example.yml`).

  2. Build production images:

     ```bash
     ./buildit.sh --prod
     ```

     `buildit.sh --prod` will build the package image via
     `docker-compose.prod.yml` and will attempt to build the `nginx`
     image from `docker/nginx/Dockerfile.prod` if the generated site
     exists at `uncommitted/data_docs/local_site`.

  3. Run production compose (ensure `DQ_DATA_SOURCE` is set):

     ```bash
     export DQ_DATA_SOURCE=ds_sample_data
     ./runit.sh --prod --serve-docs
     # or
     DQ_DATA_SOURCE=ds_sample_data docker compose -f docker-compose.prod.yml up -d
     ```

- CI: see `.github/workflows/build-with-data-docs.example.yml` for an
  example job that (1) generates Data Docs, (2) builds the package image,
  and (3) builds an `nginx` image that embeds the generated site. That
  workflow is intentionally annotated — adapt it to your build and
  registry credentials before enabling in your pipeline.

- Recommendation: in CI copy or generate `data_docs` into the repo
  workspace before building the `nginx` image. Embedding Data Docs in the
  image yields a single artifact you can push to registries and deploy
  without mount-time dependencies.