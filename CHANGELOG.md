# Changelog

## [v0.03]

### Added
- Forum access gated behind user consent form completion
- Donation button in homepage header for direct contributions
- PayPal webhook endpoints to process recurring subscription payments
- User interface for subscription cancellation in user settings
- Admin interface for managing user subscriptions
- Role indicator in members screen header when accessed from roles view

### Changed
- Router now maintains role context during navigation between screens
- Member Detail page now displays active subscription status
- Setup page reorganized with separate sections for plan creation and editing
- Settings page split into user preferences and subscription management
- Home page layout updated with donation section
- Members list view now shows role assignments

### Fixed
- Subscription expiry dates automatically sync with PayPal payment status
- Role information persists when navigating between member screens
- Role header now correctly displays in members view after role-based navigation

### Security
- Forum access requires explicit user consent via form submission
- PayPal webhook signatures verified for payment authenticity
