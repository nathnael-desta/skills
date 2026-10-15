# Open Design parity checklist

## Source

- [ ] Active or explicit Open Design artifact retrieved through MCP
- [ ] Entry file and referenced dependency bundle inspected
- [ ] Linked design-system resource inspected when present
- [ ] Every CSS variable resolved to light and dark values
- [ ] Fonts, assets, component imports, and responsive rules traced

## Production mapping

- [ ] Source structure mapped to production components
- [ ] Demo data and actions replaced without changing visual behavior
- [ ] Shared values promoted to production tokens or shared components
- [ ] Intentional deviations documented and justified
- [ ] No full Open Design bundle vendored into production

## Verification

- [ ] Relevant formatter, type, lint, and build checks pass
- [ ] Source and production compared at the same desktop viewport
- [ ] Source and production compared at a narrow viewport when responsive
- [ ] Light and dark mode both verified
- [ ] Computed colors, typography, dimensions, spacing, borders, and SVG styles checked
- [ ] Interactive states verified when present
- [ ] No unresolved or fallback CSS custom properties
- [ ] Every visible difference explained or fixed
