# Static Fixture Rules

Static data should preserve the visual contract without carrying production data.

## Construct

- Use deterministic IDs such as `fixture-001`.
- Use plausible but invented names, titles, dates, amounts, statuses, and excerpts.
- Match production field names, nesting, optionality, and content length.
- Include enough rows/cards to exercise pagination, wrapping, truncation, and density.
- Include English and Amharic examples when the route supports bilingual content.
- Include one representative record for each visible status or permission state.
- Keep dates fixed so repeated renders are stable.

## Preserve

- The same hierarchy and ordering of visible information
- The same primary and secondary actions
- The same disabled, read-only, and permission-gated affordances
- The same loading, empty, error, retry, and success boundaries

## Exclude

- Tokens, credentials, cookies, API responses copied from production, or personal data
- Random values, current-time-dependent values, and network calls
- Fake behavior that contradicts the production route
- New domain concepts introduced only to make the page look fuller
