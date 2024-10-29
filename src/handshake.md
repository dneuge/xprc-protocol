### Handshake

Protocol is identified (XPRC), then query to client is formulated (usually: *version* and *password,* in this order and separated by `LF`)

`< XPRC;version,password`  
`> v1`  
`> 8fjdksjfsnjdfsh`  
(Server delays connection for a random amount of time between 0.5 .. 2 seconds)  
(Server closes connection if password is invalid)  
`< v1;OK;2022-02-28T19:35:12.543+01:00`

or:  
`< v2;ERR:Error description text`  
(Login succeeded but server closes connection due to another error such as unsupported protocol versions)

The ISO 8601 timestamp (server system time) provided during a successful handshake should be saved as it is used for time reference in later communication. Full date and time will be provided but the exact format may vary (e.g. with or without milliseconds, Z or \+00:00).

The version number used during handshake only indicates the basic protocol revision. Available commands, their protocol revisions and feature subsets can be queried after login; see Capabilities below.
