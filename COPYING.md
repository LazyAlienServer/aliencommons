# AlienCommons licensing

This file describes how licenses apply across the AlienCommons monorepo. It is
a scope guide; the referenced license files contain the governing terms.

## Software and documentation

Unless a file or directory says otherwise, original source code,
documentation, configuration, and other non-brand materials in this repository
are licensed under the [MIT License](LICENSE).

Published packages carry a copy of the MIT License in their own package
directories so the terms remain available when those packages are distributed
independently:

- [`packages/alienmark/`](packages/alienmark/LICENSE)
- [`packages/drf-std-response/`](packages/drf-std-response/LICENSE)

## Brand assets

The AlienCommons name, logo mark, wordmark, logo lockups, social-preview
images, and other visual branding assets under [`branding/`](branding/) and
[`.github/assets/`](.github/assets/) are excluded from the MIT License. They
are governed by the separate
[AlienCommons Brand Assets License](branding/LICENSE).

## Third-party materials

Third-party materials retain their original copyright and license terms. A
dependency's inclusion in a lockfile does not relicense that dependency under
the licenses of this repository.
