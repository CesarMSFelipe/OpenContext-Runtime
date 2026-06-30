# Spec — authentication API

## Requirement: OAuth2 login
The system MUST authenticate users via an OAuth2 authorization-code flow and issue a
signed session token.

#### Scenario: successful login
- GIVEN a valid OAuth2 callback
- WHEN the token is exchanged
- THEN a signed session is created and persisted
