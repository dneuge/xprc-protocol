#!/bin/env python3
import html
import re
import sys
from argparse import ArgumentParser
import os.path
from enum import StrEnum
from pathlib import Path
from datetime import datetime, date, UTC
from pydoc import describe
from time import strftime
from typing import Callable
from xml.dom import minidom
from xml.dom.minicompat import NodeList
from xml.dom.minidom import Text, Comment, Element

import mistletoe

arg_parser = ArgumentParser()
arg_parser.add_argument('--src', type=Path, required=True)
arg_parser.add_argument('--out', type=Path, required=True)
arg_parser.add_argument('--template', type=Path, required=True)
arg_parser.add_argument('--release-version', type=str, help='release version; only to be set for release compilation')
arg_parser.add_argument('--repo-refhash', type=str, help='repository commit hash')
arg_parser.add_argument('--repo-refname', type=str, help='repository commit tag/branch name (if available)')
arg_parser.add_argument('--repo-timestamp', type=str, help='commit timestamp as ISO8601 string')

args = arg_parser.parse_args()

if (args.repo_refhash is not None or args.repo_refname is not None) != (args.repo_timestamp is not None):
    print('--repo-timestamp must be provided together with --repo-refhash and/or --repo-refname')
    sys.exit(1)

repo_version : str|None = ''
re_valid_refhash = re.compile(r'^[0-9a-f]{32}$', re.IGNORECASE)
if args.repo_refhash is not None:
    if re_valid_refhash.match(args.repo_refhash) is None:
        raise ValueError(f'Invalid commit hash format: "{args.repo_refhash}"')
    repo_version = args.repo_refhash[:8].lower()

if args.repo_refname is not None:
    if repo_version == '':
        repo_version = args.repo_refname
    else:
        repo_version += f' ({args.repo_refname})'

if repo_version == '':
    repo_version = None

repo_timestamp : datetime|None = None
repo_date : date|None = None
if args.repo_timestamp is not None:
    try:
        repo_timestamp = datetime.fromisoformat(args.repo_timestamp).astimezone(UTC)
        repo_date = repo_timestamp.date()
    except:
        raise ValueError(f'failed to parse repository timestamp: "{args.repo_timestamp}"')
build_date = datetime.now(tz=UTC).date()

HTML_GENERATOR_MARKER_INTRO = 'XPRC DOCUMENTATION AUTOMATICALLY GENERATED AT '

out_path = args.out
if os.path.exists(out_path):
    old_contents = ''
    with open(out_path, 'r') as fh:
        old_contents = fh.read()
    if HTML_GENERATOR_MARKER_INTRO not in old_contents:
        print(f'Output file {out_path} already exists and does not contain expected marker. Please check and delete manually.')
        sys.exit(1)
    old_contents = None

document_path = args.src
if not os.path.isfile(document_path):
    print(f'Source file {document_path} not found')
    sys.exit(1)
document_dir = os.path.dirname(document_path)

template_path = args.template
if not os.path.isfile(template_path):
    print(f'Template file {template_path} not found')
    sys.exit(1)
template_dir = os.path.dirname(template_path)

head_title = f'XPRC Protocol Specification {args.release_version or repo_version or "Draft"}'
body_title = f'XPRC Protocol Specification {args.release_version or "Draft"}'

def get_path(root_dir:str, rel_path:str)->str:
    # FIXME: restrict to root_dir
    return root_dir + os.path.sep + rel_path

print(f'Parsing document: {document_path}')
document_root = minidom.parse(str(document_path))
part_elems = document_root.getElementsByTagName('parts')
if len(part_elems) != 1:
    raise ValueError('exactly one "parts" element required')

re_remove_html_tags = re.compile(r'<[^>]+>')
def remove_html_tags(s:str)->str:
    return re_remove_html_tags.sub('', s)

re_any_whitespace = re.compile(r'\s+')
def remove_any_whitespace(s:str)->str:
    return re_any_whitespace.sub('', s)

def contains_any_whitespace(s:str)->bool:
    return re_any_whitespace.match(s) is not None

class DocumentElement:
    def get_html(self)->str: ...

class RenderedHtml(DocumentElement):
    def __init__(self, html):
        self.html : str = html

    def get_html(self)->str:
        return self.html

class NavigationItem:
    def __init__(self, id:str, title:str, level:int):
        self.id : str = id
        self.title : str = title
        self.level : int = level

    def __repr__(self):
        return f'NavigationItem(id="{self.id}", title="{self.title}", level={self.level})'

class NavigationIndex:
    def __init__(self):
        self.used_ids : set[str] = set()
        self.items : list[NavigationItem] = []
        self._re_id_sanitization = re.compile(r'[^a-zA-Z0-9]+')

    def _generate_id(self, title:str):
        id : str = '__' + self._re_id_sanitization.sub('_', title).strip('_').lower()

        collisions = 0
        original_id = id
        while id in self.used_ids:
            collisions += 1
            id = original_id + '__' + str(collisions)

        return id

    def add(self, title:str, level:int|str|None=None, id:str=None)->NavigationItem:
        if id is None:
            # generate automatically
            id = self._generate_id(title)
        else:
            # supplied by user
            if id in self.used_ids:
                raise ValueError(f'Provided ID is not unique: "{id}"')

        self.used_ids.add(id)

        item = NavigationItem(id, title, level)
        self.items.append(item)

        return item

    def get_current_level(self)->int:
        if len(self.items) == 0:
            return 1

        return self.items[-1].level

    def get_html(self)->str:
        out = ''

        current_level = 1
        for item in self.items:
            if item.level > current_level+1:
                raise ValueError(f'Invalid document structure, attempted to skip navigation levels from {current_level} to {item.level}: {item}')
            elif item.level > current_level:
                out += '<ul>'
                current_level += 1
            elif out != '':
                while current_level > item.level:
                    out += '</li></ul>'
                    current_level -= 1
                out += '</li>'

            out += f'<li><a href="#{item.id}">{item.title}</a>'

        while current_level > 1:
            out += '</li></ul>'
            current_level -= 1
        out += '</li>'

        return out


class XprcMistletoeConversation(mistletoe.block_token.BlockToken):
    def __init__(self, conversation:"Conversation", line_number:int):
        super().__init__([], lambda x:None)
        self.conversation : "Conversation" = conversation
        self.line_number = line_number

    @property
    def content(self):
        return self.conversation


class CustomMistletoeHtmlRenderer(mistletoe.HtmlRenderer):
    def __init__(self):
        super().__init__()

        self._re_special_block = re.compile(r'^\s*\[!([^]]+)]')

    def render_quote(self, token: mistletoe.block_token.Quote) -> str:
        self._suppress_ptag_stack.append(False)
        inner = '\n'.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()

        m = self._re_special_block.match(remove_html_tags(inner))
        if m is not None:
            special_block = m[1]
            inner = inner.replace(f'[!{special_block}]', '')
            return f'<div class="special-block special-block-{special_block.lower()}">{inner}</div>'

        return '<blockquote>\n'+inner+'\n</blockquote>'

    def render_link(self, token: mistletoe.span_token.Link) -> str:
        out = super().render_link(token)

        end_first_tag = out.find('>')
        out = out[:end_first_tag] + ' target="_blank"' + out[end_first_tag:]

        return out

    def render_auto_link(self, token: mistletoe.span_token.AutoLink) -> str:
        out = super().render_auto_link(token)

        end_first_tag = out.find('>')
        out = out[:end_first_tag] + ' target="_blank" class="autolink"' + out[end_first_tag:]

        return out

class CustomFragmentMistletoeHtmlRenderer(CustomMistletoeHtmlRenderer):
    def __init__(self):
        super().__init__()

    def render_heading(self, token: mistletoe.block_token.Heading) -> str:
        template = '<span class="headline">{inner}</span>'
        inner = self.render_inner(token)
        return template.format(level=token.level, id=id, inner=inner)

class CustomDocumentMistletoeHtmlRenderer(CustomMistletoeHtmlRenderer):
    def __init__(self, navigation_index:NavigationIndex):
        super().__init__()
        self.render_map['XprcMistletoeConversation'] = self._render_xprc_conversation

        self.navigation_index : NavigationIndex = navigation_index

    def render_heading(self, token: mistletoe.block_token.Heading) -> str:
        template = '<h{level} id="{id}">{inner}</h{level}>'
        inner = self.render_inner(token)
        id = self.navigation_index.add(inner, int(token.level)).id
        return template.format(level=token.level, id=id, inner=inner)

    def _render_xprc_conversation(self, token: XprcMistletoeConversation):
        return token.content.render_html()


def transform_conversation_tables(elem:mistletoe.Document) -> "Conversation|None":
    if isinstance(elem, mistletoe.block_token.Table):
        return Conversation.parse_mistletoe_table(elem)
    elif isinstance(elem, mistletoe.Document) or isinstance(elem, mistletoe.block_token.BlockToken):
        if elem.children is None or not isinstance(elem.children, list):
            return None

        for i in range(len(elem.children)):
            transformed = transform_conversation_tables(elem.children[i])
            if transformed is not None:
                elem.children[i] = XprcMistletoeConversation(transformed, elem.children[i].line_number)

    return None

def parse_markdown(markdown_path, navigation_index:NavigationIndex)->list[DocumentElement]:
    out = []
    with open(markdown_path, 'r') as fh:
        with CustomDocumentMistletoeHtmlRenderer(navigation_index) as r:
            mddoc = mistletoe.Document(fh)
            transform_conversation_tables(mddoc)

            out.append(RenderedHtml(r.render(mddoc)))
    return out

def get_inner_xml(elem: Element):
    serialized = elem.toxml(standalone=True)
    re_outer = re.compile(r'^\s*<' + re.escape(elem.tagName) + r'(|[^>]+)>(.*)</' + re.escape(elem.tagName) + r'>\s*$', re.DOTALL)

    m = re_outer.match(serialized)
    if m is None:
        raise ValueError(
            f'Serialization did not generate expected XML for element {elem.tagName}, got:\n{serialized}')

    return m[2]

def get_inner_content(elem: Element):
    return unindent(html.unescape(get_inner_xml(elem)))

def count_leading_spaces(s:str)->int:
    return len(s) - len(s.lstrip(' '))

def unindent(s:str)->str:
    lines = s.splitlines(keepends=True)

    indention : int|None = None
    for line in lines:
        # skip blank lines
        if line.strip() == '':
            continue

        num_spaces = count_leading_spaces(line)
        if indention is None or indention > num_spaces:
            indention = num_spaces

    if indention == 0:
        return s

    out = ''
    for line in lines:
        if len(line) > indention:
            out += line[indention:]
        else:
            out += line.lstrip(' ')

    return out

class ConversationAction(StrEnum):
    CLIENT_TO_SERVER = 'client'
    SERVER_TO_CLIENT = 'server'
    TIME_PASSES = 'later'
    REMARK_ONLY = 'remark'

class Conversation:
    def __init__(self):
        self.parts : tuple[ConversationAction, str|None, str|None] = []

    @classmethod
    def parse_mistletoe_table(cls, table_elem:mistletoe.block_token.Table) -> "Conversation|None":
        out : "Conversation" = cls()

        if table_elem.header is None:
            return None

        if not isinstance(table_elem.header, mistletoe.block_token.TableRow):
            raise ValueError(f'Unhandled element in mistletoe Table header, expected TableRow, got {table_elem.header}')

        # the header we search for has exactly 2 header cells containing RawText, anything else is not a conversation
        # so we can abort early on mismatches
        header_contents = []
        for cell_elem in table_elem.header.children:
            if not isinstance(cell_elem, mistletoe.block_token.TableCell):
                raise ValueError(f'Unhandled element in mistletoe header TableRow, expected TableCell, got {cell_elem}')

            if len(list(cell_elem.children)) != 1:
                return None

            inner_elem = next(iter(cell_elem.children))
            if not isinstance(inner_elem, mistletoe.span_token.RawText):
                return None

            header_contents.append(inner_elem.content)

        # identify conversation table by header content
        if header_contents != ['Sender', 'Content']:
            return None

        for row_elem in table_elem.children:
            if not isinstance(row_elem, mistletoe.block_token.TableRow):
                raise ValueError(f'Unhandled element in mistletoe Table, expected TableRow, got {row_elem}')

            cell_elems = list(row_elem.children)
            if len(cell_elems) != 2:
                raise ValueError(f'Unexpected number of conversation table columns: {cell_elems}')

            for cell_elem in cell_elems:
                if not isinstance(cell_elem, mistletoe.block_token.TableCell):
                    raise ValueError(f'Unhandled element in mistletoe TableRow, expected TableCell, got {cell_elem}')

            sender_cell : mistletoe.block_token.TableCell = cell_elems[0]
            content_cell : mistletoe.block_token.TableCell = cell_elems[1]

            sender : str = ''
            for sender_elem in sender_cell.children:
                if not isinstance(sender_elem, mistletoe.span_token.RawText):
                    raise ValueError(f'Unhandled element in conversation table sender column, expected RawText, got {sender_elem}')

                if sender != '':
                    raise ValueError(f'Sender has already been set; too many tokens in conversation table sender cell: {sender_cell.children}')

                sender = sender_elem.content.strip().lower()

            action : ConversationAction|None = None
            if sender == 'client':
                action = ConversationAction.CLIENT_TO_SERVER
            elif sender == 'server':
                action = ConversationAction.SERVER_TO_CLIENT

            msg : str|None = ''
            remark : str|None = ''
            for content_elem in content_cell.children:
                if isinstance(content_elem, mistletoe.span_token.RawText):
                    s = content_elem.content.strip()

                    # we get blank RawText in between elements, ignore
                    if s == '':
                        continue

                    # detect 3 dots as "time passes"/"later"
                    # requirement: unmarked action, no remark, no protocol message
                    if action is None and msg == '' and remark == '' and s == '...':
                        action = ConversationAction.TIME_PASSES
                        continue

                    # anything else is unexpected
                    raise ValueError(f'Unhandled RawText in conversation table sender column: {s}')

                if isinstance(content_elem, mistletoe.span_token.InlineCode):
                    # InlineCode is used for protocol messages

                    inner_elems = list(content_elem.children)
                    if len(inner_elems) != 1:
                        raise ValueError(f'Unhandled number of elements in mistletoe InlineCode, expected exactly one child, got {inner_elems}')

                    inner_elem = inner_elems[0]
                    if not isinstance(inner_elem, mistletoe.span_token.RawText):
                        raise ValueError(f'Unhandled element in mistletoe InlineCode, expected RawText, got {inner_elem}')

                    s = inner_elem.content.strip()
                    if s == '':
                        raise ValueError(f'Message content must not be empty')

                    if msg != '':
                        raise ValueError(f'Message has already been set: "{msg}" + "{s}"')

                    if remark != '':
                        raise ValueError(f'Remarks must stand alone or be appended to messages; preceeding remarks are not supported: remark "{remark}", message "{s}"')

                    if not action in [ConversationAction.CLIENT_TO_SERVER, ConversationAction.SERVER_TO_CLIENT]:
                        raise ValueError(f'Action "{action}" does not expect any protocol message: "{msg}"')

                    msg = s
                elif isinstance(content_elem, mistletoe.span_token.Emphasis):
                    # Emphasis is used for remarks

                    inner_elems = list(content_elem.children)
                    if len(inner_elems) != 1:
                        raise ValueError(f'Unhandled number of elements in conversation table content cell mistletoe Emphasis, expected exactly one child, got {inner_elems}')

                    inner_elem = inner_elems[0]
                    if not isinstance(inner_elem, mistletoe.span_token.RawText):
                        raise ValueError(f'Unhandled element in conversation table content cell mistletoe Emphasis, expected RawText, got {inner_elem}')

                    s = inner_elem.content.strip()

                    # remove parenthesis used for original table rendering
                    if s.startswith('(') and s.endswith(')'):
                        s = s[1:-1]

                    if s == '':
                        raise ValueError(f'Remark must not be empty')

                    if remark != '':
                        raise ValueError(f'Remark has already been set: "{remark}" + "{s}"')

                    remark = s
                else:
                    raise ValueError(f'Unexpected element in conversation table content cell: {content_elem}')

            if msg == '':
                msg = None

            if remark == '':
                remark = None

            if action is None and msg is None and remark is not None:
                action = ConversationAction.REMARK_ONLY
            elif msg is not None:
                if action not in [ConversationAction.CLIENT_TO_SERVER, ConversationAction.SERVER_TO_CLIENT]:
                    raise ValueError(f'Protocol messages must be marked with client/server as sender, got action="{action}", msg="{msg}", remark="{remark}"')
            elif not (action == ConversationAction.TIME_PASSES and msg is None and remark is None):
                raise ValueError(f'Unexpected conversation content, got action="{action}", msg="{msg}", remark="{remark}"')

            out.parts.append((action, msg, remark))

        return out

    @classmethod
    def parse_xml(cls, root_elem : Element) -> "Conversation":
        out : "Conversation" = cls()

        for part_elem in root_elem.childNodes:
            if isinstance(part_elem, Comment):
                continue
            elif isinstance(part_elem, Text):
                if part_elem.wholeText.strip() != '':
                    raise ValueError(f'found unannotated stray text within conversation: "{part_elem.wholeText.strip()}"')
                continue
            elif not isinstance(part_elem, Element):
                raise ValueError(f'unhandled XML node within conversation: {part_elem}')

            action : ConversationAction|None = None
            if part_elem.tagName == 'client':
                action = ConversationAction.CLIENT_TO_SERVER
            elif part_elem.tagName == 'server':
                action = ConversationAction.SERVER_TO_CLIENT
            elif part_elem.tagName == 'later':
                action = ConversationAction.TIME_PASSES
            elif part_elem.tagName == 'remark':
                action = ConversationAction.REMARK_ONLY
            else:
                raise ValueError(f'unhandled conversation action: "{part_elem.tagName}"')

            msg : str|None = ''
            remark : str|None = ''
            if action in [ConversationAction.CLIENT_TO_SERVER, ConversationAction.SERVER_TO_CLIENT]:
                for inner_elem in part_elem.childNodes:
                    if isinstance(inner_elem, Comment):
                        continue
                    elif isinstance(inner_elem, Text):
                        # text nodes may be "padded" with whitespace due to XML, remove
                        # (leading/trailing white-space should never be part of a message)
                        s = unindent(inner_elem.wholeText).strip()

                        # ignore blank text nodes (may be caused by XML)
                        if s == '':
                            continue

                        # we may encounter multiple non-blank text blocks
                        if msg != '':
                            # remarks are only allowed to follow messages, we can't display them inline/prepended
                            if remark != '':
                                raise ValueError(f'Remarks should only follow messages, found one inlined or prepended to message; separate from protocol message. Message "{msg}" + "{s}", remark: "{remark}"')

                            # continue protocol message by space
                            msg += ' '

                        msg += s
                    elif isinstance(inner_elem, Element):
                        if inner_elem.tagName == 'remark':
                            # remarks must be appended, not prepended
                            if msg == '':
                                raise ValueError(f'remark within {action} action preceeds message or message is missing (consider using standalone remark instead)')

                            s = get_inner_content(inner_elem).strip()
                            if s == '':
                                raise ValueError(f'empty remark within message "{msg}"')

                            # we can't display more than one remark per message
                            if remark != '':
                                raise ValueError('only a single remark is allowed per message')

                            remark = s
                        else:
                            raise ValueError(f'unhandled element within conversation: {inner_elem}')
                    else:
                        raise ValueError(f'unhandled XML node within conversation: {inner_elem}')

                if msg == '':
                    raise ValueError(f'conversation action {action} has no message: {part_elem}')
            elif action == 'remark':
                s = unindent(get_inner_xml(part_elem)).strip()
                if s == '':
                    raise ValueError(f'empty standalone remark')

                remark = s
            elif action != 'later':
                raise ValueError(f'unhandled action {action}')

            if msg == '':
                msg = None

            if remark == '':
                remark = None

            out.parts.append((action, msg, remark))

        return out

    def render_html(self):
        out = '<div class="box">'
        out += '<div class="box-content">'
        out += '<ul class="conversation">'

        action_classes : dict[ConversationAction, str] = {
            ConversationAction.CLIENT_TO_SERVER: 'conversation-client',
            ConversationAction.SERVER_TO_CLIENT: 'conversation-server',
            ConversationAction.REMARK_ONLY: 'conversation-remark',
            ConversationAction.TIME_PASSES: 'conversation-time-passes',
        }

        for action, msg, remark in self.parts:
            out += f'<li class="{action_classes[action]}">\n'

            if msg is not None:
                actor = 'Client' if action == ConversationAction.CLIENT_TO_SERVER else 'Server'
                out += f'<div class="conversation-actor">{actor}</div>\n'
                out += '<code>' + html.escape(msg) + '</code>\n'

                if remark is not None:
                    out += '<div class="conversation-remark">' + render_markdown(remark) + '</div>\n'
            elif remark is not None:
                out += render_markdown(remark) + '\n'
            elif action == ConversationAction.TIME_PASSES:
                out += '&#8230;\n'  # ellipsis (three dots)
            else:
                raise ValueError(f'Unhandled conversation part: action={action}, msg="{msg}", remark="{remark}"')

            out += '</li>\n'

        out += '</ul>\n'
        out += '</div>\n'
        out += '</div>\n'

        return out

class CommandOption:
    def __init__(self, name:str, description:str):
        self.name : str = name
        self.description : str = description
        self.default : str|None = None
        self.default_remark : str|None = None
        self.variable_name : str|None = None
        self.suffixes : list[tuple[str,str]] = []
        self.constants : list[tuple[str,str]] = []

    def set_default(self, default: str):
        if contains_any_whitespace(default):
            raise ValueError(f'default value must not contain any whitespaces, got: "{default}"')

        self.default = default

    def set_default_remark(self, default_remark: str):
        self.default_remark = default_remark if default_remark.strip() != "" else None

    def set_variable_name(self, variable_name: str):
        if contains_any_whitespace(variable_name):
            raise ValueError(f'variable name must not contain any whitespaces, got: "{variable_name}"')

        self.variable_name = variable_name

    def add_suffix(self, suffix:str, description:str):
        if suffix == '':
            raise ValueError(f'suffix must not be blank')

        if description.strip() == '':
            raise ValueError(f'suffix description must not be blank')

        if contains_any_whitespace(suffix):
            raise ValueError(f'suffix must not contain any whitespaces, got: "{suffix}"')

        for existing_suffix, _ in self.suffixes:
            if existing_suffix.lower() == suffix.lower():
                raise ValueError(f'suffix must be unique; got multiple definitions for "{suffix}"')

        self.suffixes.append((suffix, description))

    def add_constant(self, constant:str, description:str):
        if constant == '':
            raise ValueError(f'constant must not be blank')

        if description.strip() == '':
            raise ValueError(f'constant description must not be blank')

        if contains_any_whitespace(constant):
            raise ValueError(f'constant must not contain any whitespaces, got: "{constant}"')

        for existing_suffix, _ in self.suffixes:
            if existing_suffix.lower() == constant.lower():
                raise ValueError(f'constant must be unique; got multiple definitions for "{constant}"')

        self.constants.append((constant, description))

    @classmethod
    def parse(cls, root_elem:Element) -> "CommandOption":
        name = root_elem.getAttribute('name')

        description_elems = root_elem.getElementsByTagName('description')
        if len(description_elems) != 1:
            raise ValueError(f'command option "{name}" is missing description')
        option = cls(name, get_inner_content(description_elems[0]))

        if root_elem.hasAttribute('default'):
            option.set_default(root_elem.getAttribute('default'))

        if root_elem.hasAttribute('defaultRemark'):
            option.set_default_remark(root_elem.getAttribute('defaultRemark'))

        if root_elem.hasAttribute('variableName'):
            option.set_variable_name(root_elem.getAttribute('variableName'))

        suffixes_group_elems = root_elem.getElementsByTagName('suffixes')
        if len(suffixes_group_elems) > 1:
            raise ValueError('at most one "suffixes" group must be defined')
        elif len(suffixes_group_elems) == 1:
            for suffix_elem in suffixes_group_elems[0].getElementsByTagName('suffix'):
                option.add_suffix(
                    suffix_elem.getAttribute('name'),
                    unindent(get_inner_xml(suffix_elem)),
                )

        constants_group_elems = root_elem.getElementsByTagName('constants')
        if len(constants_group_elems) > 1:
            raise ValueError('at most one "constants" group must be defined')
        elif len(constants_group_elems) == 1:
            for constant_elem in constants_group_elems[0].getElementsByTagName('constant'):
                option.add_constant(
                    constant_elem.getAttribute('name'),
                    unindent(get_inner_xml(constant_elem)),
                )

        return option

class CommandParameterMultiplicity(StrEnum):
    OPTIONAL = '?'
    EXACTLY_ONCE = '1'
    AT_LEAST_ONCE = '+'
    ANY_NUMBER = '*'

    @classmethod
    def resolve(cls, s:str) -> "CommandParameterMultiplicity":
        found = None
        for e in cls:
            if e.value == s:
                if found is not None:
                    raise ValueError(f'Ambiguous enum values, unable to resolve "{s}", matched {found} and {e}')
                found = e

        if found is None:
            raise ValueError(f'unknown multiplicity value: "{s}"')

        return found

class CommandParameter:
    def __init__(self, description:str):
        if description.strip() == '':
            raise ValueError('parameter description must not be blank')

        self.description : str = description
        self.multiplicity : CommandParameterMultiplicity = CommandParameterMultiplicity.EXACTLY_ONCE
        self.condition : str|None = None

        self._multiplicity_descriptions : dict[CommandParameterMultiplicity, str] = {
            CommandParameterMultiplicity.EXACTLY_ONCE: 'exactly once',
            CommandParameterMultiplicity.OPTIONAL: 'optional',
            CommandParameterMultiplicity.AT_LEAST_ONCE: 'at least once',
            CommandParameterMultiplicity.ANY_NUMBER: 'any number of times (incl. omission)',
        }

    def set_condition(self, condition:str):
        condition = condition.strip()
        if condition == '':
            raise ValueError('condition must not be blank')

        self.condition = condition

    def set_multiplicity(self, multiplicity:CommandParameterMultiplicity):
        self.multiplicity = multiplicity

    def validate(self):
        # no validation necessary yet
        pass

    def render_html(self, templates: dict[str, str]) -> str:
        out = templates['PARAMETERS_ITEM']

        annotations_html = ''
        annotation_items_html = ''

        if self.multiplicity != CommandParameterMultiplicity.EXACTLY_ONCE:
            annotation_item_html = templates['PARAMETER_ANNOTATION_ITEM']
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_LABEL', 'Multiplicity:')
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_VALUE', html.escape(self._multiplicity_descriptions[self.multiplicity]))
            annotation_items_html += annotation_item_html

        if self.condition is not None:
            annotation_item_html = templates['PARAMETER_ANNOTATION_ITEM']
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_LABEL', 'Condition:')
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_VALUE', html.escape(self.condition))
            annotation_items_html += annotation_item_html

        if annotation_items_html != '':
            annotations_html = replace_template_markers(templates['PARAMETER_ANNOTATION'], 'COMMAND_PARAMETER_ANNOTATION_ITEM', annotation_items_html)

        out = replace_template_markers(out, 'COMMAND_PARAMETER_ANNOTATION', annotations_html)

        out = replace_template_markers(out, 'COMMAND_PARAMETER', render_markdown(self.description))

        return out

    @classmethod
    def parse(cls, elem:Element) -> "CommandParameter":
        param = cls(description=get_inner_content(elem))

        if elem.hasAttribute('multiplicity'):
            param.set_multiplicity(CommandParameterMultiplicity.resolve(elem.getAttribute('multiplicity')))

        if elem.hasAttribute('condition'):
            param.set_condition(elem.getAttribute('condition'))

        return param


class CommandParameterGroup:
    def __init__(self, delimiter:str):
        if delimiter == '':
            raise ValueError("parameter group must specify a delimiter")

        if len(delimiter) > 1:
            raise ValueError(f'delimiter must be a single character, got: {delimiter}')

        self.items : "list[CommandParameter|CommandParameterGroup]" = []
        self.delimiter : str = delimiter
        self.multiplicity : CommandParameterMultiplicity = CommandParameterMultiplicity.EXACTLY_ONCE
        self.condition : str|None = None

        self._multiplicity_descriptions : dict[CommandParameterMultiplicity, str] = {
            CommandParameterMultiplicity.EXACTLY_ONCE: 'exactly once',
            CommandParameterMultiplicity.OPTIONAL: 'optional',
            CommandParameterMultiplicity.AT_LEAST_ONCE: 'at least once',
            CommandParameterMultiplicity.ANY_NUMBER: 'any number of times (incl. omission)',
        }

    def set_condition(self, condition:str):
        condition = condition.strip()
        if condition == '':
            raise ValueError('condition must not be blank')

        self.condition = condition

    def set_multiplicity(self, multiplicity:CommandParameterMultiplicity):
        self.multiplicity = multiplicity

    def add(self, item:"CommandParameter|CommandParameterGroup"):
        item.validate()
        self.items.append(item)

    def validate(self):
        # items have already been checked before they were added, no second validation necessary

        if len(self.items) == 0:
            raise ValueError('parameter groups must not be empty')

    def needs_delimiter(self) -> bool:
        # FIXME: the intention was only to avoid printing root-level delimiter if not necessary, evaluate with root level in mind
        if len(self.items) > 1:
            return True

        singular_item = self.items[0]
        if singular_item.multiplicity not in [CommandParameterMultiplicity.EXACTLY_ONCE, CommandParameterMultiplicity.OPTIONAL]:
            return True

        return False

    def render_html(self, templates : dict[str, str]) -> str:
        out = templates['PARAMETERS_ITEM']

        group_description = f'delimited by <code>{html.escape(self.delimiter)}</code>'

        #if self.multiplicity != CommandParameterMultiplicity.EXACTLY_ONCE:
        #    group_description = self._multiplicity_descriptions[self.multiplicity] + ', ' + group_description

        #if self.condition is not None:
        #    group_description = f"Conditional: {html.escape(self.condition)} / if applicable: {group_description}"

        out = replace_template_markers(out, 'COMMAND_PARAMETER', group_description)

        annotations_html = ''
        annotation_items_html = ''

        if self.multiplicity != CommandParameterMultiplicity.EXACTLY_ONCE:
            annotation_item_html = templates['PARAMETER_ANNOTATION_ITEM']
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_LABEL', 'Multiplicity:')
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_VALUE', html.escape(self._multiplicity_descriptions[self.multiplicity]))
            annotation_items_html += annotation_item_html

        if self.condition is not None:
            annotation_item_html = templates['PARAMETER_ANNOTATION_ITEM']
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_LABEL', 'Condition:')
            annotation_item_html = replace_template_markers(annotation_item_html, 'COMMAND_PARAMETER_ANNOTATION_ITEM_VALUE', html.escape(self.condition))
            annotation_items_html += annotation_item_html

        if annotation_items_html != '':
            annotations_html = replace_template_markers(templates['PARAMETER_ANNOTATION'], 'COMMAND_PARAMETER_ANNOTATION_ITEM', annotation_items_html)

        out = replace_template_markers(out, 'COMMAND_PARAMETER_ANNOTATION', annotations_html)

        items_html = replace_template_markers(templates['SUBPARAMETERS'], 'COMMAND_SUBPARAMETER_ITEMS', self.render_items_html(templates))
        out = replace_template_markers(out, 'COMMAND_SUBPARAMETERS', items_html)

        return out

    def render_items_html(self, templates : dict[str, str]) -> str:
        out = ''

        for item in self.items:
            out += item.render_html(templates)

        return out

    @classmethod
    def parse(cls, elem:Element) -> "CommandParameterGroup":
        group = cls(delimiter=elem.getAttribute('delimiter'))

        if elem.hasAttribute('multiplicity'):
            group.set_multiplicity(CommandParameterMultiplicity.resolve(elem.getAttribute('multiplicity')))

        if elem.hasAttribute('condition'):
            group.set_condition(elem.getAttribute('condition'))

        for item in cls.parse_items(elem):
            group.add(item)

        return group

    @classmethod
    def parse_items(cls, parent_elem:Element) -> list["CommandParameter|CommandParameterGroup"]:
        out = []

        for child in parent_elem.childNodes:
            if isinstance(child, Text):
                if child.wholeText.strip() != '':
                    raise ValueError(f'unexpected text in parameter group: "{child.wholeText.strip()}"')
            elif isinstance(child, Element):
                if child.nodeName == 'subparameters':
                    out.append(cls.parse(child))
                elif child.nodeName == 'parameter':
                    out.append(CommandParameter.parse(child))
                else:
                    raise ValueError(f'unexpected element in parameter group: {child}')
            elif not isinstance(child, Comment):
                raise ValueError(f'unexpected node in parameter group: {child}')

        return out


class Command(DocumentElement):
    def __init__(self, root_elem, renderer: "CommandRenderer"):
        self.renderer = renderer

        self.navigation_item : NavigationItem|None = None

        self.name : str = root_elem.getAttribute('name').upper()
        self.title : str = root_elem.getAttribute('title')
        self.group : str = root_elem.getAttribute('group')

        self.mnemonic : list[tuple[str, bool]] = []
        num_mnemonic = 0
        re_mnemonic_mark = re.compile('^[A-Z]+$', re.IGNORECASE)
        for node in root_elem.getElementsByTagName('mnemonic')[0].childNodes:
            if isinstance(node, Text):
                self.mnemonic.append((node.wholeText, False))
            elif node.tagName == 'm':
                inner = node.childNodes
                if len(inner) != 1 or not isinstance(inner[0], Text):
                    raise ValueError('Unexpected content in mnemonic "m" tag: '+repr(inner))

                text = inner[0].wholeText
                if re_mnemonic_mark.match(text) is None:
                    raise ValueError(f'Mnemonic mark must be at least one character long and not contain any whitespace or special characters, got: "{text}"')
                self.mnemonic.append((text, True))
                num_mnemonic += len(text)
            else:
                raise ValueError('Unexpected node for mnemonic sequence: '+repr(node))
        if num_mnemonic != len(self.name):
            raise ValueError(f'Expected {len(self.name)} marks for mnemonic sequence to match command name "{self.name}", got {num_mnemonic}')

        self.description = get_inner_content(root_elem.getElementsByTagName('description')[0])

        self.options : list[CommandOption] = []
        options_group_elems = root_elem.getElementsByTagName('options')
        if len(options_group_elems) > 1:
            raise ValueError('Only a single "options" block is expected per command.')
        elif len(options_group_elems) == 1:
            for option_elem in options_group_elems[0].getElementsByTagName('option'):
                option = CommandOption.parse(option_elem)
                for existing_option in self.options:
                    if existing_option.name.lower() == option.name.lower():
                        raise ValueError(f'Option names must be unique, got multiple definitions for "{option.name}"')
                self.options.append(option)

        self.parameters : CommandParameterGroup|None = CommandParameterGroup(delimiter=';')
        parameters_group_elems = root_elem.getElementsByTagName('parameters')
        if len(parameters_group_elems) > 1:
            raise ValueError('Only a single "parameters" block is expected per command.')
        elif len(parameters_group_elems) == 1:
            for item in CommandParameterGroup.parse_items(parameters_group_elems[0]):
                self.parameters.add(item)
        if len(self.parameters.items) == 0:
            self.parameters = None
        else:
            self.parameters.validate()

        self.responses : list[str] = []
        responses_group_elems = root_elem.getElementsByTagName('responses')
        if len(responses_group_elems) > 1:
            raise ValueError('at most one "responses" group must be defined')
        elif len(responses_group_elems) == 1:
            for response_elem in responses_group_elems[0].getElementsByTagName('response'):
                response = get_inner_content(response_elem)
                if response.strip() == '':
                    raise ValueError('responses must not be blank')
                self.responses.append(response)

        self.notes : list[str] = []
        notes_group_elems = root_elem.getElementsByTagName('notes')
        if len(notes_group_elems) > 1:
            raise ValueError('at most one "notes" group must be defined')
        elif len(notes_group_elems) == 1:
            for note_elem in notes_group_elems[0].getElementsByTagName('note'):
                note = get_inner_content(note_elem)
                if note.strip() == '':
                    raise ValueError('notes must not be blank')
                self.notes.append(note)

        self.examples : list[Conversation] = []
        examples_group_elems = root_elem.getElementsByTagName('examples')
        if len(examples_group_elems) > 1:
            raise ValueError('at most one "examples" group must be defined')
        elif len(examples_group_elems) == 1:
            for example_elem in examples_group_elems[0].getElementsByTagName('example'):
                example = Conversation.parse_xml(example_elem)
                self.examples.append(example)

    def get_html(self) ->str:
        return command_renderer.render(self)

def parse_commands(commands_basedir:str, group_name:str, command_renderer:"CommandRenderer")->dict[str, Command]:
    out : dict[str, Command] = {}

    group_dir = commands_basedir + os.sep + group_name
    if not os.path.isdir(group_dir):
        raise ValueError(f'Not a directory or inaccessible: {group_dir}')

    for name in (os.listdir(group_dir) or []):
        basename, ext = os.path.splitext(name)
        if ext.lower() != '.xml':
            continue

        path = group_dir + os.sep + name
        if not os.path.isfile(path):
            raise ValueError(f'Not a file or inaccessible: {path}')

        command : "Command|None" = None
        try:
            print(f'Parsing command: {path}')
            root = minidom.parse(str(path))
            elems = root.getElementsByTagName('command')
            if len(elems) != 1:
                raise ValueError('exactly one "command" element required')

            command = Command(elems[0], command_renderer)
        except RuntimeError as e:
            raise ValueError(f'Failed parsing command file {path}') from e

        if command.group != group_name:
            raise ValueError(f'Command {command.name} indicates group {command.group} but has been filed in {group_name} directory')

        if command.name.lower() != basename.lower():
            raise ValueError(f'Command {command.name} was filed as {name}, names have to match')

        if command.name in out:
            raise ValueError(f'Duplicate definition of command {command.name}')

        out[command.name] = command

    return out

def parse_document(parts:NodeList, navigation_index:NavigationIndex, command_renderer:"CommandRenderer", parent_parts:list|None=None)->list[DocumentElement]:
    out : list[DocumentElement] = []

    if parent_parts is None:
        parent_parts = []

    for part in parts:
        if isinstance(part, Text):
            if part.wholeText.strip() != '':
                raise ValueError(f'Unexpected text in document structure: {part.wholeText}')
            continue
        elif isinstance(part, Comment):
            continue

        path = parent_parts + [part]

        if part.tagName == 'chapter':
            chapter_level = 1
            for parent in parent_parts:
                if parent.tagName == 'chapter':
                    chapter_level += 1
            chapter_title = part.getAttribute('title')
            nav_id = navigation_index.add(chapter_title, chapter_level).id
            out.append(RenderedHtml(f'<h{chapter_level} id="{nav_id}">{chapter_title}</h{chapter_level}>'))
            out += parse_document(part.childNodes, navigation_index, command_renderer, path)
        elif part.tagName == 'markdown':
            # TODO: option to change all headlines to be relative to current/chapter level
            markdown_file = part.getAttribute('file')
            markdown_path = get_path(document_dir, markdown_file)
            out += parse_markdown(markdown_path, navigation_index)
        elif part.tagName == 'commands':
            command_group = part.getAttribute('group')
            commands = parse_commands(document_dir + os.sep + 'commands', command_group, command_renderer)
            if len(commands) == 0:
                raise ValueError(f'No commands found for group {command_group}')

            navigation_level = navigation_index.get_current_level() + 1
            for command_name in sorted(commands.keys()):
                command = commands[command_name]

                navigation_id = '_command_' + command_name.lower()  # single underscore for protected namespace
                navigation_title = command.name + ' &ndash; ' + command.title
                command.navigation_item = navigation_index.add(navigation_title, navigation_level, id=navigation_id)

                out.append(command)
        else:
            raise ValueError('Unhandled part: '+part.tagName)

    return out

def replace_template_markers(template:str, marker:str|re.Pattern, replacement:str|Callable[[re.Match],str]) -> str:
    if isinstance(marker, str):
        if not marker.startswith('TEMPLATE_'):
            marker = 'TEMPLATE_' + marker
        marker = re.compile(r'<!--\s*###'+re.escape(marker)+r'(\s+(.*?)|(?:_BEGIN###\s*-->.*?<!--\s*###'+re.escape(marker)+r'_END)?)###\s*-->', re.DOTALL|re.MULTILINE)

    return marker.sub(replacement, template)

re_template_removal = re.compile(r'<!--\s*(###(?:SUB)?TEMPLATE_[^>]+(?<!_BEGIN))(?:_BEGIN###\s*-->.*?<!--\s*\1_END)?###\s*-->', re.DOTALL|re.MULTILINE)
def remove_template_markers(s:str) -> str:
    return re_template_removal.sub('', s)

def extract_subtemplate(template:str, name:str, insert_marker:bool=True) -> tuple[str, str]:
    marker = re.compile(r'<!--\s*###SUBTEMPLATE_'+re.escape(name)+r'_BEGIN###\s*-->(.*?)<!--\s*###SUBTEMPLATE_'+re.escape(name)+r'_END###\s*-->', re.DOTALL|re.MULTILINE)

    extracted : list = []
    def _extract(m:re.Match)->str:
        extracted.append(m[1])
        return '<!-- ###TEMPLATE_'+name+'### -->' if insert_marker else ''

    cleaned, num_found = marker.subn(_extract, template)
    if num_found != 1:
        raise ValueError(f'Subtemplate "{name}" found {num_found} times; expected exactly once')

    return extracted[0], cleaned

def insert_file(m:re.Match)->str:
    params = m.group(1).strip().split(' ')
    type = params[0]
    path = get_path(template_dir, params[1])

    content = ''
    with open(path, 'r') as fh:
        content = fh.read()

    if type == 'style':
        return '<style>\n'+content+'\n</style>'

    if type == 'script':
        return '<script type="application/javascript">\n'+content+'\n</script>'

    raise ValueError('Unhandled type: '+type)

def render_markdown(markdown:str)->str:
    with CustomFragmentMistletoeHtmlRenderer() as r:
        mddoc = mistletoe.Document(markdown)
        return r.render(mddoc)

class CommandRenderer:
    def __init__(self, templates:dict[str, str]):
        self.templates : dict[str, str] = templates

    def render(self, command:Command) -> str:
        out = self.templates['']

        navigation_item = command.navigation_item
        if navigation_item is None:
            raise ValueError(f'Missing navigation item for command {command.name}')

        navigation_level = navigation_item.level

        out = replace_template_markers(out, 'COMMAND_NAME', command.name)
        out = replace_template_markers(out, 'COMMAND_TITLE', f'<h{navigation_level} id="{navigation_item.id}" class="command-title">{command.title}</h{navigation_level}>')

        mnemonic_html = ''
        for mnemonic_part in command.mnemonic:
            text, mark = mnemonic_part
            if not mark:
                mnemonic_html += text
            else:
                mnemonic_html += '<span class="command-mnemonic-mark">'
                mnemonic_html += text
                mnemonic_html += '</span>'
        out = replace_template_markers(out, 'COMMAND_MNEMONIC', mnemonic_html)

        out = replace_template_markers(out, 'COMMAND_DESCRIPTION', render_markdown(command.description))

        if len(command.options) > 0:
            options_items_html = ''
            for option in command.options:
                options_item_description_html = render_markdown(option.description)

                if len(option.suffixes) > 0:
                    suffixes_items_html = ''
                    for suffix_name, suffix_description in option.suffixes:
                        suffixes_item_html = self.templates['SUFFIXES_ITEM']
                        suffixes_item_html = replace_template_markers(suffixes_item_html, 'COMMAND_SUFFIX_NAME', suffix_name)
                        suffixes_item_html = replace_template_markers(suffixes_item_html, 'COMMAND_SUFFIX_DESCRIPTION', render_markdown(suffix_description))

                        suffixes_items_html += suffixes_item_html

                    options_item_description_html += replace_template_markers(self.templates['SUFFIXES'], 'COMMAND_SUFFIXES_ITEM', suffixes_items_html)

                if len(option.constants) > 0:
                    constants_items_html = ''
                    for constant_name, constant_description in option.constants:
                        constants_item_html = self.templates['CONSTANTS_ITEM']
                        constants_item_html = replace_template_markers(constants_item_html, 'COMMAND_CONSTANT_NAME', constant_name)
                        constants_item_html = replace_template_markers(constants_item_html, 'COMMAND_CONSTANT_DESCRIPTION', render_markdown(constant_description))

                        constants_items_html += constants_item_html

                    options_item_description_html += replace_template_markers(self.templates['CONSTANTS'], 'COMMAND_CONSTANTS_ITEM', constants_items_html)

                options_item_html = self.templates['OPTIONS_ITEM']
                options_item_html = replace_template_markers(options_item_html, 'COMMAND_OPTION_DESCRIPTION', options_item_description_html)
                options_item_html = replace_template_markers(options_item_html, 'COMMAND_OPTION_NAME', option.name)
                options_item_html = replace_template_markers(options_item_html, 'COMMAND_OPTION_VARIABLE', option.variable_name or 'x')

                options_items_html += options_item_html

            options_html = replace_template_markers(self.templates['OPTIONS'], 'COMMAND_OPTIONS_ITEM', options_items_html)
            out = replace_template_markers(out, 'COMMAND_OPTIONS', options_html)

        parameters_html = ''
        if command.parameters is not None:
            parameters_html = self.templates['PARAMETERS']

            # root-level is rendered different from actual sub-parameter groups, we just use the same container
            if command.parameters.needs_delimiter():
                parameters_headline = f'Parameters: <span class="headline-annotation">(delimited by <code>{html.escape(command.parameters.delimiter)}</code>)</span>'
            else:
                parameters_headline = 'Parameter:'
            parameters_html = replace_template_markers(parameters_html, 'COMMAND_PARAMETERS_HEADLINE', parameters_headline)

            parameters_html = replace_template_markers(parameters_html, 'COMMAND_PARAMETERS_ITEM', command.parameters.render_items_html(self.templates))
        out = replace_template_markers(out, 'COMMAND_PARAMETERS', parameters_html)

        responses_html = ''
        if len(command.responses) > 0:
            responses_items_html = ''
            for response in command.responses:
                responses_items_html += replace_template_markers(self.templates['RESPONSES_ITEM'], 'COMMAND_RESPONSE', render_markdown(response))
            responses_html = replace_template_markers(self.templates['RESPONSES'], 'COMMAND_RESPONSES_ITEM', responses_items_html)
        out = replace_template_markers(out, 'COMMAND_RESPONSES', responses_html)

        notes_html = ''
        if len(command.notes) > 0:
            notes_items_html = ''
            for note in command.notes:
                notes_items_html += replace_template_markers(self.templates['NOTES_ITEM'], 'COMMAND_NOTE', render_markdown(note))
            notes_html = replace_template_markers(self.templates['NOTES'], 'COMMAND_NOTES_ITEM', notes_items_html)
        out = replace_template_markers(out, 'COMMAND_NOTES', notes_html)

        examples_html = ''
        for example in command.examples:
            examples_html += example.render_html()
        out = replace_template_markers(out, 'COMMAND_EXAMPLES', examples_html)

        return out

    @staticmethod
    def for_template(template:str)->tuple["CommandRenderer", str]:
        templates : dict[str, str] = {}

        template_command, cleaned_template = extract_subtemplate(template, 'COMMAND')
        templates[''] = template_command

        def _extract(extraction_key:str, outer_template_key:str='', insert_marker:bool=True):
            name = 'COMMAND_' + extraction_key

            if outer_template_key not in templates:
                raise ValueError(f'Template for outer template (source) key "{outer_template_key}" not extracted yet')
            if extraction_key in templates:
                raise ValueError(f'Template for extraction (destination) key "{extraction_key}" already extracted')

            outer_template = templates[outer_template_key]
            extracted, cleaned_outer_template = extract_subtemplate(outer_template, name, insert_marker)
            templates[outer_template_key] = cleaned_outer_template
            templates[extraction_key] = extracted

        # part of option/parameter description; marker for outer container not needed
        _extract('CONSTANTS', insert_marker=False)
        _extract('CONSTANTS_ITEM', 'CONSTANTS')
        _extract('SUFFIXES', insert_marker=False)
        _extract('SUFFIXES_ITEM', 'SUFFIXES')

        _extract('OPTIONS')
        _extract('OPTIONS_ITEM', 'OPTIONS')

        _extract('PARAMETERS')
        _extract('PARAMETERS_ITEM', 'PARAMETERS')
        _extract('PARAMETER_ANNOTATION', 'PARAMETERS_ITEM')
        _extract('PARAMETER_ANNOTATION_ITEM', 'PARAMETER_ANNOTATION')
        _extract('SUBPARAMETERS', 'PARAMETERS_ITEM')

        _extract('RESPONSES')
        _extract('RESPONSES_ITEM', 'RESPONSES')

        _extract('NOTES')
        _extract('NOTES_ITEM', 'NOTES')

        return CommandRenderer(templates), cleaned_template

out = ''
with open(template_path, 'r') as fh:
    out = fh.read()

out = replace_template_markers(out, 'REMOVE', '')

def format_date(d:date)->str:
    # custom implementation to avoid locale issues and use single-digit day numbers
    month_names = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    ]

    return f'{d.day} {month_names[d.month-1]} {d.year}'

def format_timestamp(ts:datetime)->str:
    ts = ts.astimezone(UTC)
    out = format_date(ts.date())
    out += ' '
    out += ts.strftime('%H:%M:%S')
    out += ' UTC'
    return out

dev_info_html = ''
dev_info_template, out = extract_subtemplate(out, 'DEVELOPMENT_INFO')
if repo_version is not None:
    dev_info_html = dev_info_template
    dev_info_html = replace_template_markers(dev_info_html, 'BUILD_REF', repo_version)

    dev_info_build_date = format_date(repo_date)
    if repo_date != build_date:
        dev_info_build_date += ', built ' + format_date(build_date)
    dev_info_html = replace_template_markers(dev_info_html, 'BUILD_DATE', dev_info_build_date)
out = replace_template_markers(out, 'DEVELOPMENT_INFO', dev_info_html)

doc_info_html = ''
if args.repo_refname is not None:
    doc_info_html += f'<code>{html.escape(args.repo_refname)}</code>'
if args.repo_refhash is not None:
    if doc_info_html != '':
        doc_info_html += ' / '
    doc_info_html += f'<code>{html.escape(args.repo_refhash)}</code>'
if doc_info_html != '':
    doc_info_html = '<br />Source revision: ' + doc_info_html

if repo_timestamp is not None:
    doc_info_html = '<br />Source time: ' + format_timestamp(repo_timestamp) + doc_info_html

doc_info_html = 'Build date: ' + format_timestamp(datetime.now(tz=UTC)) + doc_info_html

command_renderer, out = CommandRenderer.for_template(out)

out = replace_template_markers(out, 'FILEMARK', '<!-- '+HTML_GENERATOR_MARKER_INTRO+datetime.now(tz=UTC).isoformat()+' -->')
out = replace_template_markers(out, 'HEAD_TITLE', '<title>'+head_title+'</title>')
out = replace_template_markers(out, 'INSERT', insert_file)
out = replace_template_markers(out, 'TITLE', body_title)
out = replace_template_markers(out, 'DOCUMENT_INFO', doc_info_html)

navigation_index = NavigationIndex()
doc : list[DocumentElement] = parse_document(part_elems[0].childNodes, navigation_index, command_renderer)

# change first headline in navigation (intro), unindent all following headlines
if navigation_index.items[0].title == 'X-Plane Remote Control':
    navigation_index.items[0].title = 'Introduction'
    for i in range(1, len(navigation_index.items)):
        item = navigation_index.items[i]
        if item.level <= 1:
            # headline is already on top-level, do not try unindenting further
            break

        item.level -= 1

document_menu_html = navigation_index.get_html()
content_html = '\n'.join([elem.get_html() for elem in doc])

out = replace_template_markers(out, 'DOCUMENT_MENU', document_menu_html)
out = replace_template_markers(out, 'CONTENT', content_html)

out = remove_template_markers(out)

with open(out_path, 'w') as fh:
    fh.write(out)

print(f'Output written to {out_path}')
