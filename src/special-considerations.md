# Special Considerations (what to watch out for)

Sections are marked
* "Client" for points concerning client implementations,
* "Server" for server implementations,
* "Application" for applications using clients.

## Race Conditions

### \[Client, Server] Double Termination

When issuing self-terminating commands, such as non-repeating animations via `DRMU`, the channel may have closed on
server-side before clients are aware of it. This can result in a client application requesting to terminate the command
of a channel that is still seen open on client-side (valid request at time of sending). A termination request will be
sent but may only arrive after the channel has already terminated on server-side, leading to an additional out-of-band
server error message (`*ERR`, not `-ERR`) being sent back to the client.

Servers should allow attempted termination of non-existing channels (no protocol violation).

Clients should expect termination requests to result in an error message which will arrive shortly after the channel
has already been closed. Defensively written clients may want to implement additional tracking for recently terminated
channels to only ignore termination errors on expected channels. Lenient implementations may want to even regard the
error as a success indicator (a channel which should have been closed is closed if it does not exist).
Either way clients need to expect this situation to happen and should handle it gracefully.

Error message should use the following (exact) string for correlation to a `TERM` request: (not to be used for any other
error path)

`termination request ignored, channel does not exist: CCCC`

`CCCC` placeholder must be substituted with the channel ID.