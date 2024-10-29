### Basic Syntax

Messages in both directions are terminated by LF.

All requests are identified by prefixing with a case-sensitive 4 character basic alpha-numeric (\[a-zA-Z0-9\]) channel ID chosen by the client at time of request. IDs are followed by a space character, then the requested command. Command options are attached semicolon-separated to the command itself while command parameters are provided after a space character.

Server messages related to a channel ID indicate by prefix if the channel stays open (`+`) or is being closed with this message (`-`). Messages unrelated to a channel are prefixed `*`.

If the message is a status indication `ACK` or `ERR` followed by a space character will be sent in front of the ID, followed by a space, followed by the milliseconds since reference timestamp. Optionally, an additional payload message can be appended following after a space. Servers should only send at most one `ACK` per command request (as first message on the newly created channel) but `ERR` can be sent at any time in case an error occurs while running the command.

If the message holds data only channel status, channel ID, space character, milliseconds since reference timestamp, space character and payload message are present.

Channel IDs have to be unique. If a second command is issued to an already open channel, it depends on the command whether or not it will have any effect. The only exception is the TERM command which requests the channel to be closed, terminating any pending command on server-side. Note that there is no guarantee when a command or channel will actually be terminated.

It is recommended to reuse previously closed channel IDs only after a reasonable delay (such as 30 to 60 seconds) to avoid any side-effects in implementations.

Server may choose to terminate a channel or the whole connection at any time.

There is no disconnect command. Just close the connection when done, server will clean up the session. As with individual channel/command termination there is no guarantee when exactly pending commands will stop.

`> ABCD DRMV;freq=200ms;times=3 float:some/existing/dataref;int:some/other/dataref`  
`< +ACK ABCD 8721`  
`< +ABCD 8723 1.0;5`  
`< +ABCD 8925 0.98;2`  
`< -ABCD 9122 0.99;4`

Or:  
`> ABCD TERM`  
`< -ACK ABCD 8871`  *(server confirms channel termination without an error)*

`> ABCD DRMV;freq=200ms int:i/do/not/exist`  
`< -ERR ABCD 4597 no such dataref: i/do/not/exist`

`> ABC DRMV;freq=200ms int:i/do/not/exist` *(invalid channel ID)*  
`< *ERR 6742 invalid syntax`
