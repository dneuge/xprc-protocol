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
- success: confirm the protocol revision active on this session followed by `;OK;` and an ISO 8601 timestamp of session start

The server system timestamp provided during a successful handshake should be referenced to the client's local clock and stored if necessary, as it is used for time reference in later communication. Full date and time will be provided but the exact format may vary (e.g. with or without milliseconds, `Z` or `+00:00` for UTC, possibly indicating a different time offset like `+01:00`). Neither server nor client clocks are required to be synchronized, so time reference may drift during longer sessions.

The version number used during handshake only indicates the basic protocol revision. Available commands, their protocol revisions and feature subsets can be queried after login; see the section on Feature Versioning.

Servers may choose to penalize clients failing the handshake for any reason, e.g. by (temporarily) banning/ignoring them if retried too quickly.

Example:

| Sender | Content/Action                                                                                                                                                                                                                                                                     |
|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Server | `XPRC;version,password`                                                                                                                                                                                                                                                            |
| Client | `v1`                                                                                                                                                                                                                                                                               |
| Client | `8fjdksjfsnjdfsh`                                                                                                                                                                                                                                                                  |
| Server | (Server delays connection for a random amount of time between 0.5 .. 2 seconds)                                                                                                                                                                                                    |
| Server | either: `v1;OK;2022-02-28T19:35:12.543+01:00`<br /><br /> or: `v2;ERR:Error description text` <br /> (Login succeeded but server closes connection due to another error such as unsupported protocol versions) <br /> <br /> or: (Server closes connection if password is invalid) |
  
