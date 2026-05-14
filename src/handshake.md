### Handshake

Upon establishing a TCP connection to the server, the server sends a protocol identification string (`XPRC`) followed by a semicolon (`;`). Still on the same line, a query is formulated to the client as a comma-separated list. The client must respond to these queries, in the specified order with each response on a separate line, within a reasonably short time period:

| Query      | Expected Response                        |
|------------|------------------------------------------|
| `version`  | base protocol revision requested by client |
| `password` | authentication to server                 |

The client must respond within a reasonably short time period, sending each response on a separate line.

Servers may delay further communication (incl. closing the connection) for a random time of up to 2.0 seconds (recommended: 0.5 to 2.0 seconds) after the last query response has been received to slow down brute-force attacks by obfuscating the result of authentication challenges.

The server will then either, in case of
- failed authentication: close the connection without further response
- unsupported protocol revision: indicate the highest supported protocol revision, followed by `;ERR:` and a descriptive message intended to be shown to users (not machine-readable)
- success: confirm the protocol revision active on this session followed by `;OK;` and an ISO 8601 timestamp of session start (see details below)

The server system timestamp provided during a successful handshake should be stored by clients and may be advisable to be referenced to the client's local clock at time of reception, as later communication uses only relative timestamps.

The ISO 8601 timestamp must feature full date and time, including the time zone offset in *plus/minus hours:minutes* format (e.g. `+05:30`) or, alternatively (in addition to `+00:00`), `Z` for UTC. This protocol requires neither server nor client clocks to be synchronized, so clock drifts on remote connections may be noticeable over longer sessions. Precision for sub-second parts can be arbitrary and may be shortened to tens or hundreds of a second. Missing decimal places should be assumed as zero when higher precision is available on client side (0.4 seconds = 0.400 seconds = 400 milliseconds). While higher precision (such as micro or even nanoseconds) may be indicated, sub-millisecond precision is unnecessary due to network delays and relative timestamps allowing only millisecond precision anyway.

The version number used during handshake only indicates the basic protocol revision. Available commands, their protocol revisions and feature subsets can be queried after login; see the section on Feature Versioning.

Servers may choose to penalize clients failing the handshake for any reason, e.g. by (temporarily) banning/ignoring them if retried too quickly.

Examples:



| Sender | Content                                                                                                  |
|--------|----------------------------------------------------------------------------------------------------------|
| Server | `XPRC;version,password`                                                                                  |
| Client | `v1`                                                                                                     |
| Client | `8fjdksjfsnjdfsh`                                                                                        |
|        | *(server delays connection for a random amount of time)*                                                 |
| Server | `v1;OK;2022-02-28T19:35:12.543+01:00` *(server accepted connection, confirming base protocol version 1)* |
|        | *(session has been started, server is waiting for commands)*                                             |

| Sender | Content                                                                                                         |
|--------|-----------------------------------------------------------------------------------------------------------------|
| Server | `XPRC;version,password`                                                                                         |
| Client | `v1`                                                                                                            |
| Client | `8fjdksjfsnjdfsh`                                                                                               |
|        | *(server delays connection for a random amount of time)*                                                        |
| Server | `v2;ERR:Error description text` *(login succeeded but an error occurred; base protocol version 2 is supported)* |
|        | *(server closes connection because handshake failed)*                                                           |

| Sender | Content                                                   |
|--------|-----------------------------------------------------------|
| Server | `XPRC;version,password`                                   |
| Client | `v1`                                                      |
| Client | `skd9234n`                                                |
|        | *(server delays connection for a random amount of time)*  |
|        | *(server closes connection because password was invalid)* |


