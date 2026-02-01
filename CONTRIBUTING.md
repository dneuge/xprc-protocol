# Contribution Guidelines

## Indirect contributions (issue creation, discussions)

New features (such as new commands or additional options on existing commands) can be requested by
[creating an issue](https://codeberg.org/dneuge/xprc-protocol/issues) for discussion.

When creating an issue or participating in discussions:

- issues/bugs with client or server implementations need to be addressed to the respective project unless it's due to an 
  actual issue (e.g. an ambiguity) in the protocol specification
- do not post any material/text from other sources without proper citation/giving credit
- **AI must not have been involved in any part of authoring your contribution** because the original sources involved in AI training and thus their authors
  and license conditions are untraceable, bearing a high risk of copyright/license violation
  - you may be **explicitly asked to truthfully pledge not to have or will be using generative AI in any of your contributions**, neither for source code
    nor any other contribution including issue reports or discussions; violation of this strict requirement may lead to permanent removal from the project
    due to a breach of trust and tainting it with legal issues
  - it is highly recommend to disable all AI-assisted functions in software you use while making or preparing contributions to this project to avoid any
    accidental violations of this rule
- you understand and agree to be listed with all contributed information permanently, unrevokable, both directly concerning your contribution (issue/discussion
  post) as well as with any information that may consequently make it into the specification
- you understand that such information may be copied and archived permanently in uncontrollable ways due to the nature of services used to collaborate on the
  project, as well as source code repositories and open communication on the Internet in general
- by contributing to the project, including communication, you surrender all rights to be removed from or edited out of the project at any point after your
  contribution has been published (this is required because rights usually granted by laws such as DSGVO/GDPR cannot be fulfilled for technical and legal
  reasons)
  - please also refer to the TOS and policies of the service this repository and issue tracker are being hosted on

## Direct contributions to the repository (Commits, Pull/Merge Requests)

Before contributing anything for inclusion to the main repository, please make sure that

- you have read all available documentation of this project
- the contribution you are about to commit can be released under [this project's license terms](LICENSE.md)
    - check with project lead before introducing material or code restricted by licenses
- changes to source code are formatted "correctly", see the section below
- create a pull-request to the main repository to be reviewed for inclusion to the main project
- when copying (or renaming) files try to remember to first commit a plain file copy without modified content, describe what you copied (from/to) in the commit
  message, and only modify the contents in a later commit
    - the reason is that Git cannot mark files as copies, it can only automatically detect file copies based on content changes which requires a
      user-configurable (thus unpredictable) amount of content to be identical to a previously committed file
- the contribution is your own work and does not introduce copyright issues to the project
    - **contributions to specification/documentation must be 100% free from legal issues** as any legal issue introduced to the specification may spread to
      further projects downstream (client and server implementations)
    - significant portions of code should not be verbatim copies from forums/knowledge databases such as StackOverflow
    - basing a source code contribution on documentation or other (online) sources is allowed as long as you make sure to abide by the terms of use set by those
      sources and cite/name the original author(s) were applicable
        - when this results in a conflict to other points in these guidelines, the affected contribution needs to be considered as potentially derivative work
          and treated accordingly (note that e.g. including code from an external project does not necessarily violate the "own work" rule, but special care
          must be taken in terms of copyright and license conformity)
        - for any significant "imported" portion of code the **origin must be documented**; attempting to contribute copied code without proper attribution and
          clear indication of sources and licenses is a severe copyright violation
    - **AI must not have been involved in any part of authoring your contribution** because the original sources involved in AI training and thus their authors
      and license conditions are untraceable, bearing a high risk of copyright/license violation
        - you may be **explicitly asked to truthfully pledge not to have or will be using generative AI in any of your contributions**, neither for source code
          nor any other contribution including issue reports or discussions; violation of this strict requirement may lead to permanent removal from the project
          due to a breach of trust and tainting it with legal issues
        - it is highly recommend to disable all AI-related functions in editors you use (e.g. IDEs) while making or preparing contributions to this project to
          avoid any accidental violations of this rule
- all commits are made under your full real name (no aliases, no short names) and with a working email address (it must be possible to contact you under that
  address for the foreseeable future)
- you understand and agree to be listed with that information permanently, unrevokable, as a contributor to the project in the source repository and, at least
  for larger contributions, accompanying documentation
- you understand that such information will be copied and archived permanently in uncontrollable ways due to the nature of services used to collaborate on the
  project, as well as source code repositories and open communication on the Internet in general
- by contributing to the project, including communication, you surrender all rights to be removed from or edited out of the project at any point after your
  contribution has been published (this is required because rights usually granted by laws such as DSGVO/GDPR cannot be fulfilled for technical and legal
  reasons)

## Formatting code contributions (specification & tooling)

When making code contributions, either to the specification or associated tooling, please maintain the same style as
previously used in similar files. Doing so helps to maintain readability throughout the project.

Some general rules:

- use spaces instead of tabs, 4 spaces per indention level
- if you have open tasks remaining in your code, mark them with a comment in the format of `# TODO: description`
  (`#` being a comment marker)
    - use `FIXME` if you expect potential problems from the code
    - use `TODO` for generally open tasks that do not lead to issues
    - use `DEBUG` on code that can be removed when that level of debugging is no longer required
- as a general rule of thumb, look at existing code if unsure how to format

When editing XML/XSD files it is recommended to use either a JetBrains IDE or Eclipse as both are able to ease editing
with context-specific auto-completion and online documentation.

However, with commercial versions of JetBrains IDEs in particular: Remember to disable all AI integrations that may be
active by default or your contribution will be rejected.
