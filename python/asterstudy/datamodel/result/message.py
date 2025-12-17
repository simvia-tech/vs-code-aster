# -*- coding: utf-8 -*-

# Copyright 2016 EDF R&D
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, you may download a copy of license
# from https://www.gnu.org/licenses/gpl-3.0.

"""
Execution messages
------------------

Implementation of objects that give access to the execution messages.

"""


import hashlib
import os
import re
from collections import OrderedDict
from math import log10

from ...common import no_new_attributes, to_list, translate
from ...common.execution import CMDTAG, remove_mpi_prefix
from .utils import MsgLevel, MsgType


class Message:
    """This object contains informations about execution messages.

    Arguments:
        level (*MsgLevel*): Message level.
        text (str): Text of the message
        source (*MsgType*): Type of the origin of the message.
        cmd_id (str): Command identifier (command + stage number in a graphical
            stage or line number in a text stage).
        line (int): Line number in the output file.
        occurrence (int): Index of the message. There may are several messages
            emitted from the same origin.
    """
    _level = _text = _source = _line = _occ = None
    _case_id = _stg_num = _cmd_num = None
    _topo = _unknown = None
    __setattr__ = no_new_attributes(object.__setattr__)

    def __init__(self, level, text, source, cmd_id, line, occurrence):
        self.level = level
        self._text = text
        self._source = source
        self._case_id = -1
        self._stg_num = -1
        self._cmd_num = -1
        mat = re.search("(?P<cmd>[0-9]+)(?::(?P<stg>[0-9]+))?", str(cmd_id))
        if mat:
            if mat.group('stg') is not None:
                self._stg_num = int(mat.group('stg'))
            self._cmd_num = int(mat.group('cmd'))
        self._line = line
        self._occ = occurrence
        self._topo = {}
        self._unknown = []

    @property
    def level(self):
        """Get the message level."""
        return self._level

    @level.setter
    def level(self, value):
        """Set the message level."""
        assert value in (MsgLevel.Debug, MsgLevel.Info, MsgLevel.Warn,
                         MsgLevel.Error), "unexpected value {!r}".format(value)
        self._level = value

    @property
    def text(self):
        """Get the text of the message."""
        return self._text

    @property
    def source(self):
        """*MsgType*: Type of the creator."""
        return self._source

    @property
    def command_num(self):
        """int: The identifier of the command which is the command number or
            line number in a text stage.
        """
        return self._cmd_num

    @property
    def line(self):
        """int: Line number in a text stage for 'stage'."""
        return self._line

    def debug_repr(self):
        """Return a useful for debugging representation."""
        return ("{1} {2} - case:{0.case_id} stage:{0.stage_num} "
                "cmd:{0.command_num} line:{0.line}"
                .format(self, MsgType.to_str(self.source),
                        MsgLevel.to_str(self.level)))

    def source_repr(self, model):
        """Representation of the source of the message.

        Arguments:
            model (*History*): History that contains the referenced source.

        Returns:
            str: String representing the source of the message.
        """
        loc = MsgType.to_str(self.source)
        stgid = self.stage_num
        if self.source == MsgType.Runner:
            if stgid == 0:
                loc += translate("Message", " during initialization")
            else:
                loc += translate("Message", " after run #{0}").format(stgid)
        elif self.source == MsgType.Stage:
            loc += translate("Message", " from line {0}").format(self._cmd_num)
        else:
            case = model.get_node(self._case_id)
            if case:
                stage = case.get_stage_by_num(stgid)
                if stage:
                    cmd = stage.get_cmd_by_index(self.command_num)
                    if cmd and hasattr(cmd, 'title'):
                        loc += " in {}".format(cmd.title)
        loc += " at line {0}".format(self._line)
        return loc

    @property
    def checksum(self):
        """Return a checksum of the message."""
        sha = hashlib.sha1()
        sha.update(MsgLevel.to_str(self._level).encode())
        sha.update(MsgType.to_str(self._source).encode())
        sha.update(str(self._case_id).encode())
        sha.update(str(self._stg_num).encode())
        sha.update(str(self._cmd_num).encode())
        sha.update(str(self._line or 0).encode())
        sha.update(str(self._occ).encode())
        sha.update(self._text.encode())
        digest = sha.hexdigest()
        return digest

    def set_stage(self, stage):
        """Register the 'path' of the related Stage.

        Arguments:
            stage (Stage): The Stage to which the Message is related.
        """
        self._case_id = stage.parent_case.uid
        if self._stg_num < 0:
            self._stg_num = stage.number

    @property
    def case_id(self):
        """Attribute that returns the related Case identifier.

        Returns:
            int: Identifier of the related Case.
        """
        return self._case_id

    @property
    def stage_num(self):
        """Attribute that returns the related Stage identifier.

        Returns:
            int: Identifier of the related Stage.
        """
        return self._stg_num

    def add_topo(self, typ, names):
        """Add one or several topological entities of type *typ*.

        Arguments:
            typ (str): One of 'grel', 'grno', 'el' or 'no'.
            names (str or list[str]): One or more names of entity.
        """
        self._topo[typ] = self._topo.get(typ, []) + to_list(names)

    def add_unknown(self, names):
        """Add one or several unknowns.

        Arguments:
            typ (str): One of 'grel', 'grno', 'el' or 'no'.
            names (str or list[str]): One or more names of entity.
        """
        self._unknown.extend(to_list(names))

    def get_topo(self, typ):
        """Return the list of topological entities of type *typ*."""
        return self._topo.get(typ, [])

    def get_unknown(self):
        """Return the list of unknowns used in the message."""
        return self._unknown


SEPAR = "EXECUTION_CODE_ASTER_EXIT_"

def extract_messages(text):
    """Extract the messages from a text.

    Arguments:
        text (str): Output of an execution.

    Returns:
        list[*Message*]: List of Message objects.
    """
    # must be consistent with usage of supervis2_69 message in code_aster
    xtag = re.compile(r"(?P<orig>run|stg)(?P<stgnum>[0-9]+)_"
                      r"(?P<loc>cmd|txt)(?P<id>[0-9]+(:[0-9]+)?)")
    reinfo = re.compile("^(<I>|<INFO>|{0})".format(SEPAR), re.M)
    msglist = []
    # for unittest and simulator runner
    if text == 'random':
        msglist = _random_messages()
    else:
        dmsg = search_msg(text)
        for key, ltext in dmsg.items():
            mat = xtag.search(key)
            source = MsgType.Stage
            if mat.group("orig") == "run":
                source = MsgType.Runner
            elif mat.group("loc") == "cmd":
                source = MsgType.Command

            uid = mat.group("id")
            for i, linetext in enumerate(ltext):
                line, text = linetext
                if text.startswith("<A>") or 'NOOK' in text:
                    level = MsgLevel.Warn
                elif reinfo.search(text) is not None:
                    level = MsgLevel.Info
                else:
                    level = MsgLevel.Error
                msglist.append(Message(level, text, source, uid, line, i))
    return msglist


def search_msg(text, maxlines=100000):
    """Return all messages found in a text.

    Arguments:
        text (str): Output of a code_aster execution.
        maxlines (int): Parse only the last `maxlines` lines.

    Returns:
        dict: Ordered Dict of list of messages, indexed by command identifier.
    """
    def run_id(irun, line=1):
        "Return an identifier for Runner messages."
        return "run{0}_txt{1}".format(irun, line)

    separ, _ = _regexp_decoration()

    # must be consistent with usage of marker used in code_aster
    expr = re.compile(r"(^[0-9]+:(?:"
                      r"\.\. __stg[0-9]+_\w+[0-9]+(:[0-9]+)?|"
                      r" *![-]{3}[-]*?!.*?![-]{3}[-]*?!|"
                      r" *" + separ + r".*?" + separ + r"|"
                      r" *<(?:INFO|A|E|F|S)>.*?$|"
                      r"Traceback \(most recent call last\)|"
                      r"\w*Error:.*?$|"
                      r">> JDC.py : DEBUT RAPPORT|"
                      r" *" + SEPAR + ".*?$"
                      r"))",
                      re.M | re.DOTALL)
    outofcmd = re.compile("(>> JDC.py : DEBUT RAPPORT|" + SEPAR + ")", re.M)

    # attach first messages to the Runner (also if there is no tag)
    irun = 0
    current = run_id(irun)
    dmsg = OrderedDict()
    closure = None

    # take only the last 'maxlines' lines
    _lines = text.splitlines()
    if len(_lines) > maxlines:
        text = os.linesep.join(_lines[-maxlines:])
        closure = (1, "<A> Only the messages found in the last "
                      "{0} lines have been analyzed.".format(maxlines))

    text = remove_mpi_prefix(text)
    text = _add_line_numbers(text)

    for mat_i in expr.finditer(text):
        text_i = mat_i.group(0)
        # print "DEBUG: current", current, "\n", text_i, "\n" + "+" * 80
        mat = CMDTAG.search(text_i)
        if mat:
            current = "{orig}{stgnum}_{loc}{id}".format(**mat.groupdict())
            continue
        line, cleaned = _remove_decoration(text_i)
        mat = outofcmd.search(text_i)
        if mat:
            irun += 1
            current = run_id(irun, line)
        dmsg.setdefault(current, [])
        dmsg[current].append((line, cleaned))

    if closure:
        dmsg.setdefault(current, [])
        dmsg[current].append(closure)
    return dmsg


def _remove_decoration(text):
    """Remove the message decoration.

    Arguments:
        text (str): Text of a message.

    Returns:
        str: Message without its decoration.
    """
    separ, avert = _regexp_decoration()

    line, text = _remove_line_numbers(text)
    rsepar = re.compile(separ, re.M)
    left = re.compile("^ *" + avert, re.M)
    right = re.compile(avert + " *$", re.M)
    text = rsepar.sub("", text)
    text = left.sub("", text)
    text = right.sub("", text)
    text = text.strip()
    return line, text


def _regexp_decoration():
    """Return regular expressions to search for the horizontal and vertical
    markers of decorated messages
    """
    upleft = chr(0x2554)
    upright = chr(0x2557)
    horiz = chr(0x2550)
    vert = chr(0x2551)
    botleft = chr(0x255a)
    botright = chr(0x255d)
    aleft = "[!" + upleft + botleft + "]"
    aright = "[!" + upright + botright + "]"
    ahoriz = "[-" + horiz + "]"
    avert = "[!" + vert + "]"
    separ = aleft + ahoriz + "{3}" + ahoriz + "*?" + aright
    return separ, avert


def _add_line_numbers(text):
    """
    Insert line numbers at the beginning of the log of code_aster execution.

    Arguments:
        text(str): Log (output) of code_aster execution.
    """
    lines = text.splitlines()
    # 0 not an admissible value for the log
    nbl = max(len(lines), 1)
    fmt = '{{0:0{}d}}:{{1}}'.format(int(log10(nbl)) + 1)
    lines = [fmt.format(i + 1, line) for i, line in enumerate(lines)]
    return os.linesep.join(lines)


def _remove_line_numbers(text):
    number = re.compile("^([0-9]+):", re.M)
    mat_line = number.search(text)
    line = 0
    if mat_line:
        line = int(mat_line.group(1))
        text = number.sub("", text)
    return line, text


def _random_messages():
    from random import choice, randint, randrange
    msglist = []
    lsrc = set()
    uid = -1
    while len(lsrc) != 3 or len(msglist) < 10:
        level = choice([MsgLevel.Debug, MsgLevel.Info,
                        MsgLevel.Warn, MsgLevel.Error])
        source = choice([MsgType.Runner, MsgType.Stage, MsgType.Command])
        lsrc.add(source)
        uid += 1
        line = randrange(500)
        text = 'Sample text for message of level {0}'.format(
            MsgLevel.to_str(level))
        msg = Message(level, text, source, uid, line, 0)
        if source == MsgType.Command:
            for j in range(randint(0, 2)):
                msg.add_topo('grel', 'group{}'.format(j))
            for j in range(randint(0, 2)):
                msg.add_unknown('dof{}'.format(j))
        msglist.append(msg)
    return msglist
