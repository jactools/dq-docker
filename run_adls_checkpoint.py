import great_expectations as gx
import os
import pandas as pd
from great_expectations.checkpoint import (
     UpdateDataDocsAction,
)

# Define the root directory (optional, defaults to current working directory if not specified)
project_root = os.getcwd() 

print(f"Attempting to initialize/load project in: {project_root}")

# Use get_context() with mode="file" to ensure a FileDataContext is created or loaded
# This handles the creation logic internally if no context is found.
context = gx.get_context(mode="file", project_root_dir=project_root)

# Define a Data Docs site configuration
data_docs_site_name = "local_site"
data_docs_config = {
    "class_name": "SiteBuilder",
    "site_name": data_docs_site_name,
    "site_index_builder": {
        "class_name": "DefaultSiteIndexBuilder",
    },
    "store_backend": {
        "class_name": "FilesystemStoreBackend",
        "base_directory": os.path.join(project_root, "great_expectations", "uncommitted", "data_docs", data_docs_site_name),
    },
}

# Add the Data Docs site to the context
if data_docs_site_name not in context.get_site_names():
    context.add_data_docs_site(site_name=data_docs_site_name, site_config=data_docs_config)
    print(f"✅ Data Docs site '{data_docs_site_name}' added to the context.")
else:
    print(f"✅ Data Docs site '{data_docs_site_name}' already exists in the context.")

print("✅ Great Expectations Data Context is ready.")

# Define the Data Source and Data Asset
source_folder = "great_expectations/sample_data/customers"
data_source_name = "ds_sample_data"

# Create the Data Source
data_source = context.data_sources.add_pandas_filesystem(
    name=data_source_name, base_directory=source_folder
)

# Define the Data Asset
asset_name = "sample_customers"
file_customers = data_source.add_csv_asset(name=asset_name)

batch_definition_name = "customers_2019.csv"
batch_definition_path = "customers_2019.csv"
print("Files:", os.listdir(source_folder))

batch_definition = file_customers.add_batch_definition_path(
    name=batch_definition_name, path=batch_definition_path
)
# Fetch a batch to validate
batch = batch_definition.get_batch() 
# Display the first few rows of the batch
print(batch.head()) 

# Create an Expectation Suite
expectation_suite_name = "adls_data_quality_suite"
try:
    suite = gx.ExpectationSuite(name=expectation_suite_name)
    print(f"✅ Expectation Suite '{expectation_suite_name}' created.")
except Exception as e:
       print(f"⚠️ Could not create Expectation Suite: {e}") 

# Add Expectations to the Suite
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="total_spend", min_value=100, max_value=999999))
suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchRegex(column="email", regex=r"[^@]+@[^@]+\.[^@]+"))
context.suites.add(suite)

# Attach the Expectation Suite to the Batch
batch.expectation_suite = suite
# Save the Expectation Suite to the Batch
# batch.save_expectation_suite(discard_failed_expectations=False)

print(f"✅ Expectations added to the suite '{expectation_suite_name}'.")

definition_name = "adls_checkpoint"
validation_definition = gx.ValidationDefinition(
    name=definition_name,
    data=batch_definition,
    suite=suite,
)
validation_definition = context.validation_definitions.add(validation_definition)
print(f"✅ Validation Definition '{definition_name}' created.")

validation_results = validation_definition.run()
if validation_results["success"]:
    print("✅ Validation succeeded!")
else:
    print("❌ Validation failed!")

# print("Validation Results:", validation_results)

action_list = [
    UpdateDataDocsAction(name="update_data_docs", site_names=[data_docs_site_name]),
]

checkpoint = gx.Checkpoint(
    name=definition_name,
    validation_definitions=[validation_definition],
    actions=action_list,
    result_format={"result_format": "SUMMARY"}
    )

context.checkpoints.add_or_update(checkpoint=checkpoint)
# Run the Checkpoint with the Batch Request and Expectation Suite
results = checkpoint.run()
if "success" not in results:
    print("❌ Checkpoint run did not return success status.")
else:
     print(f"✅ Checkpoint run success status: {results['success']}")

print(context.list_data_docs_sites())
print(f"✅ Data Docs are available at: {context.get_docs_sites_urls()}")

