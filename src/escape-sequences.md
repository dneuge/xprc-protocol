### Escape Sequences

Some information, especially DataRef names, may collide with field separators or other syntax elements such as comma, semicolon, colon or brackets. To avoid misinterpretation, all “free-form” fields, even if not explicitly documented, should be encoded through a basic backslash-based escape sequence:

* The escape character is a backslash: `\`
* An actual backslash `\` in a data field will be encoded as: `\\`
* Syntactically problematic characters such as `,` `;` `:` `[` `]` are prefixed by a backslash, e.g.
    * `sim/weather/turbulence[0]` as a literal name (the brackets are part of the name and not to be interpreted as an array access by XPRC commands) should be encoded as `sim/weather/turbulence\[0\]`

> [!warning]
> Escape sequences are currently under review and their handling may change in the near future. See
> https://codeberg.org/dneuge/xprc-protocol/issues/3 for details. Current recommendation is to avoid sending special
> characters to the server, if possible, and log a warning if being sent or received to relate any errors which
> may arise from subsequent misinterpretation.
