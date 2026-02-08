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

### Recommended Flow for Session Initiation

To ensure command and feature availability/compatibility, clients/applications are recommended to perform the following actions immediately upon session initiation:

1. query `SRID` to detect server implementation (`id` and `version`)
   * needed to interpret any experimental commands or experimental feature flags, if relevant
2. query `SRLC` to detect command availability incl. versions and feature flags
   * if an unsupported version of `SRLC` is indicated try downgrading the command via `SRFS` and retry
     * defensively written clients may want to disconnect if `SRLC` command version is different because responses may be misinterpreted,and commands cannot be verified, `SRFS` command would need to be issued "blindly"
3. for commands using different versions than supported by the client:
   * if higher than supported, try downgrading commands to a version supported by the client via `SRFS`
   * if lower than supported or command cannot be switched to a compatible version: block the command on client side, log/issue a warning to application/user if actually used
4. if any commands were reconfigured in the previous step: query `SRLC` again to verify changes and check available feature flags
5. request changes to command feature flags if necessary using `SRFS`
6. if any commands were reconfigured in the previous step: verify via `SRLC` again

Applications/users may find it helpful to be able to check availability/support of actually used commands ahead of time. Incompatible commands/features which are not used by the application are unlikely to hold any relevance but failing commands only as they are attempted to be used may be inconvenient for end-users.
