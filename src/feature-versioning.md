## Feature Versioning

Revisions to the protocol are handled in three ways:

* incompatible changes to basic syntax/behaviour increment the basic protocol version used/indicated during connection handshake
  * as clients are asked for their requested version before the server confirms its protocol revision, it is possible for servers to support multiple revisions of the base protocol
  * if the requested version gets denied by the server, it will indicate its highest supported base protocol revision on the error message, allowing the client to downgrade to the server's latest supported version (if the client supports that)
* command versions are incremented in case of incompatible changes
* command features not requiring a full command revision can be discovered and possibly activated/deactivated using feature flags

In addition to actual protocol versioning, feature flags can also be used to indicate general server-side feature availability, such as optional features (not supported by all servers) or features depending on certain X-Plane/SDK versions (such as `unspecific` flag on `DRLS`).

Feature flags and command versions are explained in command specifications, if available.

Clients/applications are recommended to discover command versions and feature flags through `SRLC` upon connecting to the server. `SRFS` may then be used to switch command versions or enable/disable individual feature flags, if supported by the server.

Servers are not required to support multiple versions (neither base protocol nor commands) or reconfiguration through feature flags. `SRFS` requests need to result in error (`ERR`) indications and `SRLC` should indicate feature flags as unmodifiable in that case.

Version and feature flag selections must be kept local to the session requesting those changes; other sessions must remain unaffected. Clients need to reestablish the desired configuration when reconnecting.

Feature flag names are case-sensitive and consist of one or more basic alpha-numeric characters incl. `-`. However, names must not start with `-` to avoid collision with feature state syntax (see prefixes used by `SRLC` and `SRFS` commands, regular expression for feature flag names: `[a-zA-Z0-9][a-zA-Z0-9\-]*`).

### Recommended Flow for Session Initiation

To ensure command and feature availability/compatibility, clients/applications are recommended to perform the following actions immediately upon session initiation:

1. issue `SRFS` to attempt selecting the expected version for the `SRFS` command
2. issue `SRFS` to attempt selecting the expected versions for `SRID` and `SRLC` commands
3. query `SRLC` to detect command availability incl. versions and feature flags
    * if unsupported versions of `SRLC`, `SRID` or `SRFS` are indicated try downgrading affected commands via `SRFS` and retry, if the client supports more versions than already requested in steps 1 and 2
4. query `SRID` to detect server implementation (`id` and `version`)
   * needed to interpret any experimental commands or experimental feature flags, if relevant
5. configure versions and features of all other commands as required; recommended:
   * if command version is higher than supported, try downgrading commands to a version supported by the client via `SRFS`
   * if command version is lower than supported or the command cannot be switched to a compatible version: block the command on client side, log/issue a warning to application/user if actually used
   * use conditional feature flag selection unless strictly required
   * configure all commands in parallel to minimize delays
6. query `SRLC` again to verify changes and check available feature flags

It is recommended to cache last retrieved `SRLC` and `SRID` results for fast evaluation. If conditional feature selection is insufficient, it may be necessary to select command versions, followed by an extra `SRLC` update, before feature selection.

Applications/users may find it helpful to be able to check availability/support of actually used commands ahead of time. Incompatible commands/features which are not used by the application are unlikely to hold any relevance but failing commands only as they are attempted to be used may be inconvenient for end-users.
