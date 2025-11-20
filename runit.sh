# Assuming you have the .env file and Docker setup ready
# docker run -it --rm \
#   --env-file .env \
#   great-expectations-adls-spn \
#   checkpoint run adls_checkpoint

docker run -it --rm \
  --env-file .env \
  --volume "$(pwd)/great_expectations/uncommitted/data_docs":/usr/src/app/gx/uncommitted/data_docs \
  great-expectations-adls-spn \
  python run_adls_checkpoint.py
