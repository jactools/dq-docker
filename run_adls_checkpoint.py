import os
import great_expectations as gx
from great_expectations.checkpoint import UpdateDataDocsAction

from dq_docker.config.adls_config import (
    PROJECT_ROOT,
    DATA_DOCS_SITE_NAME,
    DATA_DOCS_CONFIG,
    SOURCE_FOLDER,
    DATA_SOURCE_NAME,
    ASSET_NAME,
    BATCH_DEFINITION_NAME,
    BATCH_DEFINITION_PATH,
    EXPECTATION_SUITE_NAME,
    DEFINITION_NAME,
    RESULT_FORMAT,
    DATA_DOCS_SITE_NAMES,
)

print(f"Attempting to initialize/load project in: {PROJECT_ROOT}")

# Initialize or load a FileDataContext rooted at PROJECT_ROOT
context = gx.get_context(mode="file", project_root_dir=PROJECT_ROOT)

# Ensure Data Docs site exists
if DATA_DOCS_SITE_NAME not in context.get_site_names():
    context.add_data_docs_site(site_name=DATA_DOCS_SITE_NAME, site_config=DATA_DOCS_CONFIG)
    print(f"✅ Data Docs site '{DATA_DOCS_SITE_NAME}' added to the context.")
else:
    print(f"✅ Data Docs site '{DATA_DOCS_SITE_NAME}' already exists in the context.")

print("✅ Great Expectations Data Context is ready.")

# Create the Data Source and CSV asset (uses pandas filesystem datasource)
data_source = context.data_sources.add_pandas_filesystem(name=DATA_SOURCE_NAME, base_directory=SOURCE_FOLDER)
file_customers = data_source.add_csv_asset(name=ASSET_NAME)

print("Files:", os.listdir(SOURCE_FOLDER))

batch_definition = file_customers.add_batch_definition_path(name=BATCH_DEFINITION_NAME, path=BATCH_DEFINITION_PATH)

# Fetch a batch to inspect
batch = batch_definition.get_batch()
print(batch.head())

# Create or reuse an Expectation Suite
try:
    suite = gx.ExpectationSuite(name=EXPECTATION_SUITE_NAME)
    print(f"✅ Expectation Suite '{EXPECTATION_SUITE_NAME}' created.")
except Exception as e:
    print(f"⚠️ Could not create Expectation Suite: {e}")

# Add Expectations to the Suite
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="total_spend", min_value=100, max_value=999999))
suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchRegex(column="email", regex=r"[^@]+@[^@]+\.[^@]+"))
context.suites.add(suite)

batch.expectation_suite = suite

print(f"✅ Expectations added to the suite '{EXPECTATION_SUITE_NAME}'.")

# Build ValidationDefinition and add to the context
validation_definition = gx.ValidationDefinition(name=DEFINITION_NAME, data=batch_definition, suite=suite)
validation_definition = context.validation_definitions.add(validation_definition)
print(f"✅ Validation Definition '{DEFINITION_NAME}' created.")

validation_results = validation_definition.run()
if validation_results.get("success"):
    print("✅ Validation succeeded!")
else:
    print("❌ Validation failed!")

# Prepare actions and checkpoint
action_list = [UpdateDataDocsAction(name="update_data_docs", site_names=DATA_DOCS_SITE_NAMES)]

checkpoint = gx.Checkpoint(name=DEFINITION_NAME, validation_definitions=[validation_definition], actions=action_list, result_format=RESULT_FORMAT)

context.checkpoints.add_or_update(checkpoint=checkpoint)
results = checkpoint.run()
if "success" not in results:
    print("❌ Checkpoint run did not return success status.")
else:
    print(f"✅ Checkpoint run success status: {results['success']}")

print(context.list_data_docs_sites())
print(f"✅ Data Docs are available at: {context.get_docs_sites_urls()}")

