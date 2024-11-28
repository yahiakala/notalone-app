# Skeleton Loading States

The Not Alone app uses skeleton loading states to provide a better user experience while data is being fetched or processed. This is implemented through a CSS role called `skeleton` that can be applied to various Anvil components.

## Implementation

The skeleton loading effect is defined in `theme/assets/theme.css` and consists of:

```css
.anvil-role-skeleton {
  animation: skeleton-loading 1s linear infinite alternate;
  height: 30px;
  border-radius: 12px;
}

@keyframes skeleton-loading {
  0% {
    background-color: hsl(200, 20%, 80%);
  }
  100% {
    background-color: hsl(200, 20%, 95%);
  }
}
```

This creates a pulsing animation that alternates between two shades of gray, providing a visual indication that content is loading.

## Loading Sequence

The proper timing of skeleton states is crucial for a smooth user experience. The sequence works as follows:

1. Form YAML defines initial component states with skeleton roles
2. Form is displayed to user showing skeleton loading states
3. `form_show` event triggers after the form is visible
4. Data is loaded and skeleton states are removed

### Example from MemberDetail

```yaml
# form_template.yaml
components:
  - name: tb_firstname
    type: TextBox
    properties:
      role: [outlined, skeleton]  # Initial skeleton state

  - name: tb_lastname
    type: TextBox
    properties:
      role: [outlined, skeleton]  # Initial skeleton state
```

```python
# __init__.py
def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    with anvil.server.no_loading_indicator:
        self.load_data()

def load_data(self):
    # Fetch data from server
    self.member = anvil.server.call('get_member_data', Global.tenant_id, self.email)

    # Populate fields and remove skeleton states
    self.tb_firstname.text = self.member['first_name']
    self.tb_lastname.text = self.member['last_name']
    self.tb_firstname.role = 'outlined'  # Remove skeleton role
    self.tb_lastname.role = 'outlined'  # Remove skeleton role
```

This sequence ensures that:
1. Users see the skeleton loading state immediately when the form appears
2. The form layout is preserved while data loads
3. Content appears smoothly once data is ready

## Usage Throughout the Application

The skeleton role is used in several key areas of the application:

### Member Components
- In member rows (`Members/MemberRow`): Applied to name, sign-up date, and last login fields to show loading states before member data is loaded
- In member details (`MemberDetail`): Used on various input fields and labels while member information is being fetched

### Role Management
- In role details (`RoleDetail`): Applied to email fields and other input components during loading
- In role rows (`Roles/RoleRow`): Used on labels showing last update information

### Reports
- In report components (`Reports/ReportRow`): Applied to labels to show loading states while report data is being generated
- In the router (`Router`): Used on report name labels during navigation

### Setup Forms
- In setup configuration (`Setup`): Applied to various input fields while loading configuration data, including:
  - Discourse API settings
  - PayPal integration settings
  - Webhook configurations
  - Group name fields
  - URL inputs for waivers and documentation

### File Management
- In file rows (`RoleDetail/FileRow`): Applied to file information displays while loading

## Integration with no_loading_indicator

The skeleton loading implementation is integrated with Anvil's `no_loading_indicator` context manager to prevent the default loading spinner from appearing during data fetching.

### Best Practices

1. Define skeleton states in YAML for immediate visual feedback:
```yaml
properties:
  role: [outlined, skeleton]
```

2. Load data in the form_show event to ensure skeletons are visible:
```python
def form_show(self, **event_args):
    with anvil.server.no_loading_indicator:
        self.load_data()
```

3. Remove skeleton roles after populating data:
```python
def load_data(self):
    data = anvil.server.call('get_data')
    self.text_box.text = data['value']
    self.text_box.role = 'outlined'  # Remove skeleton role
```

4. For components that combine roles, preserve other roles when removing skeleton:
```python
# Initial state in YAML
properties:
  role: [outlined, skeleton]

# After loading
self.text_box.role = 'outlined'
```

This pattern ensures a smooth, professional loading experience where:
- Users see immediate feedback through skeleton states
- The page layout is stable during loading
- No disruptive loading spinners appear
- Content transitions smoothly once loaded
