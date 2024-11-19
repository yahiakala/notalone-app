# CSS Roles Documentation

## Overview

The Not Alone app uses Material Design 3 styling through CSS roles defined in `theme/assets/theme.css`. These roles are the primary way to style components throughout the application, ensuring consistent design and behavior.

## Typography Roles

### Text Styles

```css
.anvil-role-display {
  font-size: 57px;
  line-height: 64px;
  font-weight: 400;
}

.anvil-role-headline {
  font-size: 32px;
  line-height: 40px;
  font-weight: 400;
}

.anvil-role-title {
  font-size: 22px;
  line-height: 28px;
  font-weight: 500;
}

.anvil-role-body {
  font-size: 14px;
  line-height: 20px;
  font-weight: 400;
}

.anvil-role-input-prompt {
  font-size: 16px;
  line-height: 1.5;
}
```

Use these roles to maintain consistent typography:
- `display`: Large, prominent text (e.g., landing page headlines)
- `headline`: Section headers and important text
- `title`: Subsection titles and card headers
- `body`: Default text style for content
- `input-prompt`: Text style for form labels and input fields

## Button Roles

### Standard Buttons

```css
.anvil-role-filled-button > .btn {
  background-color: %color:Primary%;
  color: %color:On Primary%;
}

.anvil-role-outlined-button > .btn {
  color: %color:Primary%;
  border: solid 1px %color:Outline%;
}

.anvil-role-elevated-button > .btn {
  color: %color:Primary%;
  background-color: %color:Surface%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 1px 3px 1px rgba(0, 0, 0, 0.15);
}

.anvil-role-tonal-button > .btn {
  color: %color:On Secondary Container%;
  background-color: %color:Secondary Container%;
}
```

Button variants for different contexts:
- `filled-button`: Primary actions with high emphasis
- `outlined-button`: Secondary actions
- `elevated-button`: Important actions that need visual hierarchy
- `tonal-button`: Alternative emphasis buttons

### Custom Button Roles

```css
.anvil-role-soft-button > .btn {
    border-radius: 10px;
}

.anvil-role-google-sign > button {
    /* Styling for Google sign-in button */
}
```

Special button styles for specific use cases:
- `soft-button`: Buttons with softer corners
- `google-sign`: Custom styling for Google authentication

## Card Roles

```css
.anvil-role-outlined-card {
  border-radius: 12px;
  background-color: %color:Surface%;
  border: solid 1px %color:Outline%;
  padding: 15px;
}

.anvil-role-elevated-card {
  border-radius: 12px;
  background-color: %color:Surface%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 2px 6px 2px rgba(0, 0, 0, 0.15);
  padding: 15px;
}

.anvil-role-tonal-card {
  border-radius: 12px;
  background-color: %color:Surface Variant%;
  padding: 15px;
}
```

Card variants for different content containers:
- `outlined-card`: Basic card with border
- `elevated-card`: Card with shadow for visual hierarchy
- `tonal-card`: Card with variant background color

## Input Field Roles

### Text Input Styling

```css
.anvil-role-outlined {
  background-color: transparent;
  border: 1px solid %color:Outline%;
  border-radius: 4px;
  color: %color:On Surface%;
}

.anvil-role-input-error {
  color: %color:Error%;
  border-color: %color:Error%;
}
```

Input field variants:
- `outlined`: Standard outlined input fields
- `input-error`: Error state for input fields

## Layout Roles

```css
.anvil-role-soft-fp {
    border-radius: 5px;
    padding: 0px 20px;
    border: solid 1px %color:Outline%;
}

.anvil-role-narrow-col {
    overflow: hidden;
    padding: 35px;
}

.anvil-role-vertically-centered {
  height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
}
```

Layout utility roles:
- `soft-fp`: Flow panel with soft borders
- `narrow-col`: Narrow column layout
- `vertically-centered`: Center content vertically

## Table Roles

```css
.anvil-role-table-row {
    border: solid 1px %color:Outline%;
    border-radius: 12px;
    display: flex;
    align-items: center;
    padding: 15px;
    margin: 10px 0;
}

.anvil-role-table-row:hover {
    background: hsl(315, 100%, 98.22%);
    opacity: 100%;
}
```

Table styling roles:
- `table-row`: Custom table row styling
- Includes hover effects and consistent spacing

## Loading State Roles

```css
.anvil-role-skeleton {
  animation: skeleton-loading 1s linear infinite alternate;
  height: 30px;
  border-radius: 12px;
}
```

Loading state roles:
- `skeleton`: Animated loading placeholder

## Usage Examples

### Button Examples
```python
# Primary action button
button_1.role = 'filled-button'

# Secondary action button
button_2.role = 'outlined-button'

# Elevated button for important actions
button_3.role = 'elevated-button'
```

### Card Examples
```python
# Basic card with border
panel_1.role = 'outlined-card'

# Elevated card for important content
panel_2.role = 'elevated-card'

# Tonal card for grouped content
panel_3.role = 'tonal-card'
```

### Input Field Examples
```python
# Standard outlined input
text_box.role = 'outlined'

# Error state input
text_box.role = 'input-error'
```

### Layout Examples
```python
# Centered content container
column_panel.role = 'vertically-centered'

# Narrow column layout
flow_panel.role = 'narrow-col'
```

## Best Practices

1. **Consistent Role Usage**
   - Use the same roles for similar components
   - Maintain visual hierarchy through appropriate role selection

2. **Component State Management**
   - Apply error states using appropriate roles
   - Use loading states for async operations

3. **Responsive Design**
   - Consider mobile views when applying layout roles
   - Use appropriate spacing roles for different screen sizes

4. **Visual Hierarchy**
   - Use elevated components sparingly
   - Maintain consistent use of filled vs outlined variants

5. **Typography**
   - Use appropriate text roles for content hierarchy
   - Maintain readable text sizes and line heights

## Custom Role Creation

When creating new custom roles:

1. Add the role definition to `theme/assets/theme.css`
2. Follow the existing naming convention
3. Document the new role in this guide
4. Consider mobile responsiveness
5. Test across different browsers

Remember that CSS roles are the primary way to style components in the app. Avoid inline styles and maintain consistency by using these predefined roles.
