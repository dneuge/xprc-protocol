## Settings & Persistence

### Location/Directory Structure

To facilitate auto-configuration of local clients (in best case requiring zero configuration by users), connection-relevant information such as the password and server port should be stored in plain-text files at well-known locations:

* *X-Plane preferences directory*
  * `xprc` (directory)
    * `password.cfg` (plain-text file)
    * `port.cfg` (plain-text file)
    * *Implementation ID* (directory)
      * any implementation-specific files/sub-directories go here 

For X-Plane 11 and 12, the `preferences` directory can currently be found as `Output/preferences` underneath the X-Plane installation's base path, however the exact location may change in the future. Servers are recommended to use [`XPLMGetPrefsPath`](https://developer.x-plane.com/sdk/XPLMGetPrefsPath/) to determine the correct location at runtime.

Only standard files described by this specification should be stored directly in the `xprc` directory. Implementation-specific files, including any sub-directory structures, can be stored in further sub-directories using the implementation ID to create unique namespaces.

For compatibility with case-sensitive filesystems all standardized names should be written in lower-case.

### Passwords

Passwords are supposed to be automatically generated and stored in `xprc/password.cfg` underneath X-Plane's "preferences" directory. For compatibility and ease of implementation, only [visible 7-bit ASCII characters](https://en.wikipedia.org/wiki/ASCII#Character_set) should be used (i.e. 0x20..0x7E). The password is the first line of the file (without any other formatting/syntax) which can be optionally terminated by LF or CR LF. Clients must ignore any additional lines (they do not belong to the password), if multiple lines should be present. Server implementations following this version of the protocol specification should not write more than the single password line to the file.

By default, server implementations should regenerate the password regularly (e.g. on each plugin restart). Such generated passwords should be of sufficient complexity and entropy.

Due to plain-text exposure (both on storage and network), it is recommended to not offer users any direct way of entering custom passwords (other than by manually editing the file). Direct file editing for such purpose, even if possible, should not be advertised.

To avoid frequent reconfiguration of clients running over the network, users should have a choice to disable automated password regeneration (maintaining last password, only regenerated on user request).

If an existing password is found to be insecure (as determined by the server implementation), it may be invalidated (getting regenerated or refusing startup) for security reasons.

### Server Port

The server port should be stored in `xprc/port.cfg` underneath X-Plane's "preferences" directory. Equivalent to password storage, the file must be plain-text containing the port on the first (single) line, optionally terminated by LF or CR LF. Clients must discard any extra lines, if present. The port number must be formatted as a decimal number ASCII string without leading zeros (e.g. `1234`, not `01234`).

### Implementation-Specific Files

Server implementations are recommended to use their uniquely chosen implementation ID (see `SRID`) to create their personal namespace underneath the `xprc` directory.

Implementations are free to choose whatever layout they want to use within their namespace but should avoid storing files on the standardized shared `xprc` directory level. Even if an implementation only needs to maintain a single custom file, that file should still be stored in a unique namespace to avoid collisions with future protocol revisions or other servers.

### Multiple Servers

Users should be expected to choose a single server implementation instead of running multiple plugins providing XPRC service at the same time, except (possibly) for testing.

However, in case of multiple simultaneous servers, the standardized files (`password.cfg` and `port.cfg`) would be in conflict. Server implementations are currently not expected to handle such collisions.
