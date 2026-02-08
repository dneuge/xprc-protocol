## Extending the Protocol

### Experimental Commands (implementation-specific, not standardized)

Server implementations may choose to offer experimental XPRC commands, which are not (yet) specified in the
protocol standard.

Servers should start experimental command names with `X` to avoid name collisions. That `X` command namespace has been
reserved for free use by implementations and will never hold any standardized commands. `SRLC` should list those
commands unless only meant for temporary server-internal use. Developers adding or maintaining such commands should be
aware that clients/applications may start depending on exact meaning, behaviour or features of those commands, so even
these commands should ideally be named uniquely (not to be removed and redefined for something else at a later point)
and use stable behaviour. It may be helpful to publish a specification for such commands as part of the server and
use features through `SRLC` just like it would be done for standardized commands.

Applications and clients should confirm server implementation (`id` in `SRID`) and command/feature list (`SRLC`)
before using any `X` commands. Although the server `version` presented by `SRID` is not meant to be interpreted by
clients/applications, it may be advisable to check that string against a list of known "good" versions.
Unknown or unidentifiable/uncertain commands should never be used automatically; applications may want to ask users
for confirmation before doing so.

### Experimental Feature Flags (implementation-specific, not standardized)

Standardized commands may be altered by experimental feature flags which must be disabled by default (default behaviour,
unless requested to be altered, must always follow official specification).

Servers should start experimental feature flag names with `x-` to avoid name collisions. Similar to the reserved
command namespace, officially specified feature flags will never use `x-` prefixes.

Clients can discover (published) experimental feature flags via `SRLC` and request them using `SRFS`.

Experimental commands are entirely implementation-specific and thus do not need to prefix feature flags (if present)
with `x-` nor do they need to restrict activation.
