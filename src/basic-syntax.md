### Basic Syntax

Messages in both directions are terminated by line end.

All requests start with a channel ID chosen by the client at time of request, followed by the command to be requested and parameters. Channel IDs are restricted to basic alpha-numeric characters and must always be 4 characters long (regular expression: `[a-zA-Z0-9]{4}`). Command names always use 4 upper-case basic alpha-numeric characters (`[A-Z0-9]{4}`). Channel ID, command and parameters are separated by single space characters each. Command names may be followed by one or more command options, separated from each other as well as the command name by semicolons. Multiple parameters are also separated by semicolon.

Server messages related to a channel ID indicate by prefix if the channel stays open (`+`) or is being terminated/closed with this message (`-`). Messages unrelated to a channel are prefixed `*`.

If the message is a status indication, `ACK` or `ERR` followed by a space character will be sent in front of the ID, followed by a space, followed by the milliseconds since reference timestamp. Optionally, an additional payload message can be appended following after a space. Servers should only send at most one `ACK` per command request (as first message on the newly created channel) but `ERR` can be sent at any time in case an error occurs while running the command. Errors are expected to always close the associated channel.

If the message holds data, then only channel status, channel ID, space character, milliseconds since reference timestamp, space character and payload message are present.

Channel IDs have to be unique. If a second command is issued to an already open channel, it depends on the command whether or not it will have any effect. The only exception is the `TERM` command which requests the channel to be closed, terminating any pending command on server-side. Note that there is no guarantee when a command or channel will actually be terminated.

It is recommended to reuse previously closed channel IDs only after a reasonable delay (such as 30 to 60 seconds) to avoid any side-effects in implementations.

Servers may choose to terminate a channel or the whole connection at any time.

There is no disconnect command. Just close the connection when done, servers will clean up the session. As with individual channel/command termination there is no guarantee when exactly pending commands will stop.

#### Examples

| Sender  | Content                                                                           |
|---------|-----------------------------------------------------------------------------------|
| Client  | `ABCD DRMV;freq=200ms;times=3 float:some/existing/dataref;int:some/other/dataref` |
| Server  | `+ACK ABCD 8721` *(command acknowledged)*                                         |
| Server  | `+ABCD 8723 1.0;5`                                                                |
| Server  | `+ABCD 8925 0.98;2`                                                               |
| Server  | `-ABCD 9122 0.99;4` *(command completed, channel closed by server)*               |

| Sender | Content                                                                           |
|--------|-----------------------------------------------------------------------------------|
| Client | `ABCD DRMV;freq=200ms;times=3 float:some/existing/dataref;int:some/other/dataref` |
| Server | `+ACK ABCD 8721` *(command acknowledged)*                                         |
| Server | `+ABCD 8723 1.0;5`                                                                |
| Client | `ABCD TERM`                                                                       |
| Server | `-ACK ABCD 8871` *(server confirms channel termination without an error)*         |

| Sender | Content                                                                                      |
|--------|----------------------------------------------------------------------------------------------|
| Client | `ABCD DRMV;freq=200ms int:i/do/not/exist`                                                    |
| Server | `-ERR ABCD 4597 no such dataref: i/do/not/exist` *(server terminates channel with an error)* |

| Sender | Content                                                                                         |
|--------|-------------------------------------------------------------------------------------------------|
| Client | `ABC DRMV;freq=200ms int:i/do/not/exist` *(protocol error: client sends invalid channel ID)*    |
| Server | `*ERR 6742 invalid syntax` *(server issues unspecific error, cannot be related to any channel)* |
