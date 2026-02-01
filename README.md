# X-Plane Remote Control (Protocol Specification)

[![Issue Tracking: Codeberg](https://img.shields.io/badge/issue%20tracking-codeberg-2684cf)](https://codeberg.org/dneuge/xprc-protocol/issues)

XPRC provides an easy way to interact with X-Plane datarefs and commands from other applications/computers via a TCP network connection.

This project contains the protocol specification to be implemented by servers and clients.

Official repositories are hosted on [Codeberg](https://codeberg.org/dneuge/xprc-protocol) and [GitHub](https://github.com/dneuge/xprc-protocol).
Both locations are kept in sync and can be used to submit pull requests but issues are only tracked on
[Codeberg](https://codeberg.org/dneuge/xprc-protocol/issues) to gather them in a single place. Please note that
this project has a strict "no AI" policy [affecting all contributions](CONTRIBUTING.md) incl. issue reports.

Related projects:

- [reference server implementation in C](https://github.com/dneuge/xprc-server-plugin-c) (X-Plane plugin, available on
  [Codeberg](https://codeberg.org/dneuge/xprc-server-plugin-c) and [GitHub](https://github.com/dneuge/xprc-server-plugin-c))
- a [Java client library](https://codeberg.org/dneuge/xprc-client-java) (available on [Codeberg](https://codeberg.org/dneuge/xprc-client-java) and [GitHub](https://github.com/dneuge/xprc-client-java))

## Current State

The protocol is not in a stable state yet. Please refer to the [issues list](https://codeberg.org/dneuge/xprc-protocol/issues) for details.

- the basic protocol syntax/encoding is finished
  - however, some special characters conflict with commonly used command syntax and prompt for a more general syntax/encoding rule
- some essential commands still need to be added (version/feature discovery without need of large protocol revisions)
- some command options are under review and may be reworked or removed
- some additional commands are planned to be added

## Contributing (e.g. requesting features)

Please refer to the dedicated [contribution guidelines](CONTRIBUTING.md).

## History

X-Plane offered a UDP network interface for a long time already but any more extensive control of the sim required
writing a plugin (or script, e.g. using FlyWithLua or XPPython). The idea for XPRC came shortly after Hot Start released
their excellent Challenger 650: Using PFPX for flight planning I could not find any performance profile, so I planned to
write a tool to automatically perform the required test flights to derive the required data. This would have required to
*remotely control the aircraft* from an external application (hence the name *X-Plane Remote Control*). As the
UDP interface was not really suitable for that purpose, I gathered the required features and started work on a protocol
specification.

Later in 2022 my focus shifted towards working on a bridge to another flight simulator, which required to also register
DataRefs and X-Plane commands from XPRC instead of just interacting with existing ones.

In 2024, X-Plane 12.1.1 introduced a [REST/WebSockets API](https://developer.x-plane.com/article/x-plane-web-api/),
solving most issues with the legacy UDP interface. The new API makes several of the original use-cases for XPRC at least
partially obsolete. However, more advanced features such as registering custom DataRefs and X-Plane commands or
"animating" DataRefs still is not supported through that new API.

## License

All resources and tooling of this project are provided under [MIT or MIT-like licenses](LICENSE.md), unless declared otherwise
(e.g. by source code comments). Please see the [full license file](LICENSE.md) for details, including an explanation of
how it applies to implementations.

### Note on the use of/for AI

Usage for AI training is subject to individual source licenses, there is no exception. This generally means that proper
attribution must be given and disclaimers may need to be retained when reproducing relevant portions of training data.
When incorporating source code, AI models generally become derived projects. As such, they remain subject to the
requirements set out by individual licenses associated with the input used during training. When in doubt, all files
shall be regarded as proprietary until clarified.

Unless you can comply with the licenses of this project you obviously are not permitted to use it for your AI training
set. Although it may not be required by those licenses, you are additionally asked to make your AI model publicly
available under an open license and for free, to play fair and contribute back to the open community you take from.

AI tools are not permitted to be used for contributions to this project. The main reason is that, as of time of writing,
no tool/model offers traceability nor can today's AI models understand and reason about what they are actually doing.
Apart from potential copyright/license violations the quality of AI output is doubtful and generally requires more
effort to be reviewed and cleaned/fixed than actually contributing original work. Contributors will be asked to confirm
and permanently record compliance with these guidelines.

**Note that providing this project as input to an LLM creates derivatives of this project or at least counts as a
software dependency, requiring you to comply with full license terms (exemptions are not applicable).** See the
[license file](LICENSE.md) for details. Avoid AI to avoid legal issues, it's not worth it.

## Acknowledgements

X-Plane is a registered trademark of Austin Meyer and Aerosoft.
