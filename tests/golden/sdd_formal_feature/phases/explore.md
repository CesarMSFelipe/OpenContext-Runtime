# Explore — authentication API

Surveyed the existing session layer, user table, and provider gateway. OAuth2 login
is a broad/high-risk change touching auth, persistence, and security; it routes to the
SDD workflow rather than the localized OC Flow.
