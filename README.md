# X-Plane Remote Control (Protocol Specification)

[![Issue Tracking: Codeberg](https://img.shields.io/badge/issue%20tracking-codeberg-2684cf)](https://codeberg.org/dneuge/xprc-protocol/issues)

XPRC provides an easy way to interact with X-Plane datarefs and commands from other applications/computers via a TCP network connection.

This project contains the protocol specification to be implemented by servers and clients.

Official repositories are hosted on [Codeberg](https://codeberg.org/dneuge/xprc-protocol) and [GitHub](https://github.com/dneuge/xprc-protocol).
Both locations are kept in sync and can be used to submit pull requests but issues are only tracked on
[Codeberg](https://codeberg.org/dneuge/xprc-protocol/issues) to gather them in a single place. Please note that
this project has a strict "no AI" policy [affecting all contributions](CONTRIBUTING.md) incl. issue reports.

Related projects:

- [reference server implementation in C](https://codeberg.org/dneuge/xprc-server-plugin-c) (X-Plane plugin, available on
  [Codeberg](https://codeberg.org/dneuge/xprc-server-plugin-c) and [GitHub](https://github.com/dneuge/xprc-server-plugin-c))
- a [Java client library](https://codeberg.org/dneuge/xprc-client-java) (available on [Codeberg](https://codeberg.org/dneuge/xprc-client-java) and [GitHub](https://github.com/dneuge/xprc-client-java))

## Current State

The protocol is not in a stable state yet. Please refer to the [issues list](https://codeberg.org/dneuge/xprc-protocol/issues) for details.

- the basic protocol syntax/encoding is finished
  - however, some special characters conflict with commonly used command syntax and prompt for a more general syntax/encoding rule
- some essential commands are still under review (`SRLC` and `SRFS`)
- some essential command options are under review and may still be reworked or removed

## Contributing (e.g. requesting features)

Please refer to the dedicated [contribution guidelines](CONTRIBUTING.md).

Documentation source code is mostly kept inside the [`src`](src) directory. The document structure is controlled through [`document.xml`](src/document.xml) (complemented by a [schema](src/document.xsd)) whereas the individual parts are provided in two ways:

- [commands](src/commands) are described in XML (according to the [command schema](src/command.xsd)) to ensure uniform templating, text blocks generally use Markdown formatting
- other sections are written in Markdown (`.md`) format

### Documentation format

Markdown files and command sections support the following special formats:

#### Highlight boxes

Particularly important information can be highlighted using the same extension used by e.g. [GitHub](https://github.com/orgs/community/discussions/16925) and [Gitlab](https://docs.gitlab.com/user/markdown/#alerts):

```markdown
> [!warning]
> Take extra care about whatever was written surrounding this box.
```

The HTML template currently supports the following tags, listed in ascending order of severity:

1. `note` to point out generally important information
2. `warning` for indicating something that might lead to issues if not taken care of (e.g. unintended results)
3. `caution` to warn about something that could have severe consequences if not followed (e.g. general protocol incompatibility)

#### Conversation transcripts

In addition to XML command descriptions, transcripts describing client/server communication can also be provided from
Markdown files by following a specific table layout:

* header columns must read `Sender` and `Content`
* sender column
  * must indicate `Client` or `Server` for data sent by either actor
  * must be blank for full-line remarks or "later"/"time passes" markers
* content column
  * must start with inline code for data sent by `Client`/`Server`
  * must indicate remarks emphasized in parentheses `*(like this)*`
  * remarks may stand alone (full-line) or follow client/server content
  * three dots (`...`) can be used for "later"/"time passes"

```markdown
| Sender  | Content                                            |
|---------|----------------------------------------------------|
| Client  | `ABCD XTST whatever`                               |
| Server  | `+ACK ABCD 2837` *(remark referring to this line)* |
|         | ...                                                |
|         | *(full-line remark)*                               |
```

## Compiling the documentation locally

This repository includes custom tooling and templates to compile an HTML-based documentation, located in
[`tools/htmldocs/`](tools/htmldocs).

Compilation requires a Linux-compatible environment with Bash, [Less](https://lesscss.org) (command `lessc`) and a recent
version of Python.

Instead of invoking the compiler directly and taking care of dependencies, you may want to invoke
[`do_all.sh`](do_all.sh) which [validates](validate.sh) and [builds](build.sh) the documentation to your local `target`
directory (created parallel to `src`).

> [!warning]
> The `target` directory will be deleted, in part or as a whole, at the start of a build and is excluded from version
> control.

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

All original resources and tooling of this project are provided under [MIT or MIT-like licenses](LICENSE.md), unless
declared otherwise (e.g. by source code comments). Please see the [full license file](LICENSE.md) for details, including
an explanation of how it applies to implementations.

The HTML template and compiled documentation in HTML format contain fonts which are also
[included in this repository](tools/htmldocs/template/fonts) as unpacked original copies.
Please refer to each directory's `_source.txt` file and each font's website/repository for
detailed information:

* [Inter](https://rsms.me/inter/), licensed SIL OFL 1.1
* [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono), licensed SIL OFL 1.1
* [Source™ Sans](https://github.com/adobe-fonts/source-sans), licensed SIL OFL 1.1

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

Source is a trademark of Adobe in the United States and/or other countries.
