## Dataref Types

X-Plane datarefs can be overloaded, offering multiple types (with different values) under the same name. Hence, types
must always be specified together with datarefs for retrieval, manipulation or registration. This also allows early
agreement on value encodings to be used for further XPRC channel messages.

Value encodings are human-readable, following the basic premise of text mode being easy to work with:

* integer numbers are simply decimal strings
* floating-point numbers are represented in "standard C formatting"
* arrays specify the number of items before all item values
* binary data is encoded to upper-case hex strings, always using a multiple of 2 characters (one for each nibble)
  * bytes are directly concatenated without any delimiters in-between

> [!warning]
> More details on floating-point encoding, in particular encoding of special values (NaN and infinities) still has to be
> specified; see <https://codeberg.org/dneuge/xprc-protocol/issues/9> for details.

Note that X-Plane's plugin API (XPLM) also has an "unknown" type (a placeholder for any type unsupported by current
API) which is omitted from XPRC as it has no relevant use outside X-Plane internals.

Commands handling multiple types at once, such as `DRCI`, may use the index column (#) to establish a defined
(non-customizable) order for values.

| # | Type name | Description                               | Encoding                                                                                                                                                               |
|---|-----------|-------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `int`     | 32 bit integer                            | human-readable string<br/>Example: `123`                                                                                                                               |
| 2 | `float`   | 32 bit floating-point value               | human-readable string<br/>Example: `-1.63e-3`                                                                                                                          |
| 3 | `double`  | 64 bit floating-point value               | human-readable string<br/>Example: `-1.63e-3`                                                                                                                          |
| 4 | `int[]`   | array of 32 bit integers                  | Comma-separated:<ol><li>array length as human-readable string</li><li>`int` values as human-readable strings (see above)</li></ol>Example: `3,1,2,3`                   |
| 5 | `float[]` | array of 32 bit floating-point values     | Comma-separated:<ol><li>array length as human-readable string</li><li>`float` values as human-readable strings (see above)</li></ol>Example: `2,4.0,2.12`              |
| 6 | `blob`    | byte array (binary data)                  | Comma-separated:<ol><li>blob size (decoded) as human-readable string</li><li>Content as concatenated human-readable hexadecimal string</li></ol>Example: `4,A201FF0D`  |
