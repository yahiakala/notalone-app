# General Instructions

This document outlines general development guidelines for the Not Alone application.

## Linting

### Policy on Linting Errors

Flake8 linting errors should be **ignored** in this project. Common linting errors you may see include:

1. Line length warnings (e.g., "line too long (149 > 79 characters)")
2. Unused import warnings
3. Blank line warnings
4. Whitespace warnings

These warnings should not be addressed because:
- The project prioritizes code readability over strict PEP 8 compliance
- Some imports may be used indirectly or needed for type hints
- Line length restrictions can make code less readable when broken up
- Maintaining consistent style across the codebase is more important than fixing linting warnings

### Example

This code with linting errors:
```python
from .helpers import print_timestamp, verify_tenant, validate_user, get_usertenant, get_users_with_permission, populate_roles, usertenant_row_to_dict

def some_long_function_name_with_many_parameters(param1, param2, param3, param4, param5, param6):
    """This is a very long docstring that explains what this function does in great detail."""
    pass
```

Should be left as-is, even though it triggers linting errors about line length and imports.

## Dropdown Components

When working with Anvil's dropdown components, follow these guidelines:

### Data Format

Dropdown items must be provided as a list of tuples, where each tuple contains:
1. Display value (what the user sees)
2. Stored value (what's used programmatically)

```python
# Correct - list of tuples
dropdown_items = [
    ("John Smith", "user123"),
    ("Jane Doe", "user456")
]

# Incorrect - list of dictionaries
dropdown_items = [
    {"name": "John Smith", "id": "user123"},
    {"name": "Jane Doe", "id": "user456"}
]
```

### Example Implementation

```python
# In form code
def load_users(self):
    """Load users for dropdown selection"""
    users = self.get_users()

    # Format users for dropdown
    user_items = [(u["name"], u["id"]) for u in users]

    # Assign to dropdown
    self.dd_users.items = user_items

    # Get selected value later
    selected_id = self.dd_users.selected_value  # Returns the stored value
```

### Best Practices

1. Always use tuples for dropdown items:
   - First element: Display text
   - Second element: Value to store

2. When converting from other formats:
```python
# Converting from dict format
users = [{"name": "User", "id": "123"}]
dropdown_items = [(u["name"], u["id"]) for u in users]
```

3. Handling selected values:
```python
# Getting selected value
selected_id = dropdown.selected_value  # Returns second element of tuple

# Setting selected value
dropdown.selected_value = "user123"  # Use stored value, not display text
```

4. Empty state handling:
```python
# Provide empty list if no items
dropdown.items = [] if not users else [(u["name"], u["id"]) for u in users]
```

## HTTP Requests with anvil.http

When making HTTP requests using anvil.http, follow these guidelines:

1. Use json=True for JSON requests:
```python
# Correct - use json=True for both request body and response parsing
response = anvil.http.request(
    url="https://api.example.com/data",
    method="POST",
    headers={"Content-Type": "application/json"},
    json=True,  # Request body will be JSON-encoded
    data=data,  # body goes through the data arg
    timeout=30
)

# Incorrect - don't use json_response=True
response = anvil.http.request(
    url="https://api.example.com/data",
    json_response=True  # Wrong parameter name
)
```

2. Error Handling:
```python
# Correct - let anvil.http handle errors
def make_request():
    return anvil.http.request(
        url="https://api.example.com/data",
        method="GET",
        json=True
    )

# Incorrect - don't wrap in try-except
def make_request():
    try:
        return anvil.http.request(...)
    except anvil.http.HttpError as e:  # Unnecessary error handling
        raise Exception(str(e))
```

3. Optional Parameters:
   - Use timeout for time-sensitive requests
   - Set appropriate headers for API calls
   - Use json=True when working with JSON APIs

This ensures consistent and reliable HTTP request handling across the application.

## Button Click Event Handlers

When implementing button click event handlers that make server calls, follow this pattern:

1. Disable the button immediately to prevent double-clicks
2. Update button text to indicate processing state
3. Use no_loading_indicator to prevent the default loading spinner
4. Restore button state after the operation completes
5. Do not add alerts or other user feedback unless explicitly requested

Example:
```python
def btn_save_click(self, **event_args):
    """Save data to server"""
    # Disable button and show processing state
    self.btn_save.enabled = False
    self.btn_save.text = "Saving..."

    # Make server call without loading indicator
    with anvil.server.no_loading_indicator:
        updated_data = anvil.server.call(
            'save_data',
            self.text_box.text
        )

        # Update any client state if needed
        Global.some_data = updated_data

    # Restore button state
    self.btn_save.text = "Save"
    self.btn_save.enabled = True
```

This pattern ensures:
- No accidental double-submissions
- Clear visual feedback during processing
- No disruptive loading spinners
- Proper button state restoration
- No unnecessary alerts or popups

### User Feedback

User feedback through alerts should only be added when explicitly requested. When requested, use Anvil's built-in alert function:
```python
# Correct - use Anvil's alert function when requested
alert("Operation completed successfully")

# Incorrect - Notification is not a valid Anvil function
Notification("Operation completed successfully").show()
```

## Testing the Application

The application can be tested using the development deployment. The deployment information is stored in `docs/.deployment.txt` and includes a URL, an email, and a password.

To test the application:

1. Visit the deployment URL in your browser
2. Sign in using the provided email and password
3. Test functionality in the development environment
4. Remember that this is a development deployment, so use it only for testing purposes

### Best Practices for Testing

1. Always test changes in the development deployment before deploying to production
2. Use the provided test account credentials
3. Test all affected functionality after making changes
4. Clear browser cache if you encounter unexpected behavior
5. Report any issues found during testing

## Import Guidelines

### Avoid Top-Level Imports for Public Packages

Public Python packages should be imported within functions or methods where they are used, rather than at the module level. This practice:
- Reduces memory usage by only importing when needed
- Improves startup time by deferring imports until they're required
- Makes dependencies clearer and more localized

```python
# Incorrect - top-level import
import datetime

def process_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')

# Correct - import within function
def process_date(date_string):
    import datetime as dt
    return dt.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
```

### Exceptions

The following imports are allowed at the top level:
- Internal project imports (e.g., `from .helpers import validate_user`)
- Anvil framework imports (e.g., `import anvil.server`, `import anvil.users`)
- Type hints in stub files

This guideline helps maintain efficient resource usage and clear dependency management throughout the application.

## Best Practices

While linting errors should be ignored, developers should still follow these best practices:

1. Write clear, descriptive variable and function names
2. Include docstrings for functions and modules
3. Maintain consistent indentation
4. Use meaningful whitespace to improve readability
5. Follow the established patterns in the codebase

The focus should be on writing maintainable, secure code that follows the project's architectural patterns rather than strict adherence to linting rules.
