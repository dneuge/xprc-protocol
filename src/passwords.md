## Password handling

Passwords are supposed to be automatically generated and stored in a fixed location underneath the X-Plane directory as a plain-text file: `Output/preferences/xprc_password.cfg`

This allows local connections to be established automatically by clients after locating the X-Plane directory (which may be automated), requiring zero configuration by users, in best case. By default, server implementations should regenerate the password regularly (e.g. on each plugin restart). Such generated passwords should be of sufficient complexity and entropy.

Due to plain-text exposure (both on storage and network), it is recommended to not offer users any direct way of entering custom passwords (other than by manually editing the file). Direct file editing for such purpose should not be advertised.

To avoid frequent reconfiguration of clients running over the network, users should have a choice to disable automated password regeneration (maintaining last passwordm, only regenerated on user request).