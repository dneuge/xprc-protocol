# X-Plane Remote Control

X-Plane Remote Control (XPRC) allows easy interaction with X-Plane via network connections. This is a 3rd party project; the protocol is not implemented by X-Plane itself but requires a plugin to be installed by users. XPRC is **not** compatible with X-Plane's legacy UDP-based or the modern web-based protocols. It is also not meant to replace the native web-based protocol which is a more recent development (work on XPRC began in early 2022).

Offering a text-based protocol means that XPRC clients can be implemented with minimal effort and communication can be monitored without any special decoding. To test XPRC, a connection can even be established via `telnet` or other plain-text terminal clients.

While XPRC offers users to bind to any network interface incl. IPv6 support, it is only meant to be accessed from private secure local networks. Security must be established by users as needed but server plugins are recommended to choose safe defaults and warn users when they select a potentially insecure configuration.
