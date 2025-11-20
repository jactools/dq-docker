
# Assuming you have the .env file and Docker setup ready
# Example using the Great Expectations CLI inside the container:
# docker run -it --rm \
#   --env-file .env \
#   great-expectations-adls-spn \
#   checkpoint run adls_checkpoint

# Run the package as a module inside the container. This uses the
# namespaced module `dq_docker.run_adls_checkpoint` now that the
# runtime was moved into the `dq_docker` package.
docker run -it --rm \
  --env-file .env \
  --volume "$(pwd)/great_expectations/uncommitted/data_docs":/usr/src/app/gx/uncommitted/data_docs \
  great-expectations-adls-spn \
  python -m dq_docker.run_adls_checkpoint
