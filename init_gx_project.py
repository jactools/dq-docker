import great_expectations as gx
import os

# Define the root directory (optional, defaults to current working directory if not specified)
project_root = os.getcwd() 

print(f"Attempting to initialize/load project in: {project_root}")

# Use get_context() with mode="file" to ensure a FileDataContext is created or loaded
# This handles the creation logic internally if no context is found.
context = gx.get_context(mode="file", project_root_dir=project_root)

print("✅ Great Expectations Data Context is ready.")
# The 'great_expectations' directory should now exist in your project_root
print(context)
