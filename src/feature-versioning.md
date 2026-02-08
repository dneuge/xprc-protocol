## Feature Versioning

Revisions to the protocol are handled in three ways:

* incompatible changes to basic syntax/behaviour increment the basic protocol version used/indicated during connection handshake
  * as clients are asked for their requested version before the server confirms its protocol revision, it is possible for servers to support multiple revisions of the base protocol
  * if the requested version gets denied by the server, it will indicate its highest supported base protocol revision on the error message, allowing the client to downgrade to the server's latest supported version (if the client supports that)
* command versions are incremented in case of incompatible changes
* command features not requiring a full command revision can be discovered and possibly activated/deactivated using feature flags

Feature flags and command versions are explained in command specifications, if available.

Clients/applications are recommended to discover command versions and feature flags through `SRLC` upon connecting to the server. `SRFS` may then be used to switch command versions or enable/disable individual feature flags, if supported by the server.

Servers are not required to support multiple versions (neither base protocol nor commands) or reconfiguration through feature flags. `SRFS` requests need to result in error (`ERR`) indications and `SRLC` should indicate feature flags as unmodifiable in that case.

Version and feature flag selections must be kept local to the session requesting those changes; other sessions must remain unaffected. Clients need to reestablish the desired configuration when reconnecting.
