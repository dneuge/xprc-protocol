# DataRef Types

DataRefs in X-Plane can be overloaded to provide more than one type at a time.

Text-mode is supposed to fulfill two use-cases: Easy implementation and the chance of human-readable interpretation without requiring any tools.

When comparing this list to the original XPLM API notice that the "unknown" type (a placeholder for any type unsupported by current API) is omitted from this protocol. That's because the "unknown" type cannot be interpreted anyway, so we treat it simply as non-existent. In case a dataref would only be available with an "unknown" type the response will simply be `ERR`.

| # |  Type name | Description                           | Encoding (text mode)                                          |
|---|------------|---------------------------------------|---------------------------------------------------------------|
| 1 | `int`      | 32 bit integer                        | human-readable string
                                                           Example: `123` |
| 2 | `float`    | 32 bit floating-point value           | human-readable string
                                                           Example: `-1.63e-3` |
| 3 | `double`   | 64 bit floating-point value           | human-readable string
                                                           Example: `-1.63e-3` |
| 4 | `int[]`    | array of 32 bit integers              | Comma-separated:
                                                           1. array length as human-readable string
                                                           2. ints as human-readable strings
                                                           Example: `3,1,2,3` |
| 5 | `float[]`  | array of 32 bit floating-point values | Comma-separated:
                                                           1. array length as human-readable string
                                                           2. floats as human-readable strings
                                                           Example: `2,4.0,2.12` |
| 6 | `blob`     | byte array (binary data)              | Comma-separated:
                                                           1. blob size (decoded) as human-readable string
                                                           2. Content as concatenated human-readable hexadecimal string
                                                           Example: `4,A201FF0D` |
