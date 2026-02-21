# XPRC Protocol Specification License Information

Copyright (c) 2022-2026 Daniel Neugebauer

## Preamble / Intention

Being a network protocol, the specification for XPRC has been split to a separate repository instead of mixing it with
a server or client implementation. This also allows the specification to be worked on and evolve separate from any
specific implementation but prompts the question which license can be applied to it.

Official XPRC server/client implementations, as of 2026, are released under MIT licenses and the intention was to also
apply the same license to the protocol specification. However, the original MIT license was written in respect to
software and it begs the question how/if a protocol specification (primarily documentation) on its own qualifies as
"software" when it is more of a resource used to write actual software based on it.

There are some wide-spread variations of the MIT license mentioning "Materials" instead of "Software", however still
referring to those "Materials" as supplements to "Software", hence also not exactly applying to this project. Common
alternatives also did not seem to fit the purpose of specification documents used for software development, so the
project was insteaad released with this clarification put in front of original MIT and a "Materials"-specific
modification to the MIT license.

If unsure or in legal conflict:

- the official MIT license (see below) takes precedence where applicable
- assert the specification to be "Software" as it is used to base software on
- if not possible, assert the specification to be "associated documentation files" in terms of the original MIT license
- if not possible, assert the specification to be "Materials" in terms of commonly used variations of the MIT license,
  swapping "Software" for "Materials"
- if still not possible, use the intentions stated above
- if even that isn't sufficient: ask the project

If a provision of these licenses and preamble is or becomes illegal, invalid or unenforceable in any jurisdiction, the
validity and enforceability of any other provision shall remain unaffected. The provision in question shall be
reinterpreted as close to the original intention as possible.

## Exemptions for Protocol Implementations

The protocol specification is provided as a common reference document to enable implementations, both servers and
clients, to be interoperable with each other.

Implementations following the specification are recommended to link to this project for reference but are not required
to treat the specification as a dependency, copy, modification or derivate in terms of the licenses below unless actual
files or significant portions of verbatim copies from this project are actually being included.

Examples:

- reading the specification to create a new client or server implementation (naturally requiring to use the same command
  names, options and terms of the network protocol being specified by this project): no need to treat this project as a
  dependency (the developer implementing such software is just using this project for reference)
- including copies from the protocol specification as part of client/software documentation: properly quoting the
  specification is sufficient (cite with clear reference to the source)
  - recommendation: instead of introducing verbatim copies to your project, you may simply refer to the specification or
    describe the relevant functionality in your own words to avoid any legal uncertainty
- *automatically* generating/deriving software or other resources based on this repository: such generation will create
  an actual derivative product, requiring you to follow all license terms (exemptions do not apply)
  > [!caution]
  > Using "Artificial Intelligence" for code generation is a prime example for this case. It is generally
  > recommended to not use this project together with "AI" (see also the clarification on AI usage in the
  > [readme](README.md) file). AI users are recommended to seek international legal advice to avoid license violations.
- forking this project or creating new revisions of the specification is fully subject to all licenses (exemptions do
  not apply)

## Variation of the MIT License applying primarily to documentation/"Materials"

**Applicable to the specification in this repository and document releases based on this repository**

Copyright (c) 2022-2026 Daniel Neugebauer

Permission is hereby granted, free of charge, to any person obtaining a copy
of these documentation and associated software files (the "Materials"), to deal
in the Materials without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Materials, and to permit persons to whom the Materials is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Materials.

THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN
THE MATERIALS.

## Original MIT License (MIT)

**Applicable to software/tooling contained in this repository**

Copyright (c) 2022-2026 Daniel Neugebauer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
