from dataclasses import dataclass
from string import digits, ascii_letters, whitespace

commands = {
    "\\cdot": "⋅",
    "\\rangle": "⟩",
    "\\langle": "⟨",
    "\\rightarrow": "→",
    "\\^": "^",
    "\\_": "_",
    "\\{": "{",
    "\\}": "}"
}

@dataclass
class Tok:
    typ: str
    val: str

def tokenize(tex):
    pos = 0
    prevpos = 0
    toks = []
    state = "unknown"

    # improvise a goto label, oops
    def pushtok(typ):
        nonlocal state, nextstate, pos, prevpos
        toks.append(Tok(typ, tex[prevpos:pos]))
        state = nextstate
        prevpos = pos

    while pos < len(tex):
        if tex[pos] in digits:
            nextstate = "number"
        elif tex[pos] in ascii_letters:
            nextstate = "identifier"
        elif tex[pos] == "\\":
            nextstate = "command"
        elif tex[pos] in ["^", "_", "{", "}"]:
            nextstate = tex[pos]
        elif tex[pos] not in whitespace:
            nextstate = "operator"
        elif tex[pos] in whitespace:
            nextstate = "unknown"
        else:
            raise Exception(f"unrecognized char {tex[pos]} at {pos}")

        if state == "unknown":
            prevpos = pos
            state = nextstate

        if state == "command":
            length = pos - prevpos
            if tex[pos-1] in ["^", "_", "{", "}"]:
                pushtok("command")
            elif nextstate != "identifier" and nextstate != "number" and length > 1:
                pushtok("command")
        elif state in ["^", "_", "{", "}", "operator"]:
            # tokens that have a length of 1
            pushtok(state)
        else:
            if state != nextstate:
                pushtok(state)
        pos += 1

    if prevpos < len(tex) and state != "unknown":
        pushtok(state)

    return toks

@dataclass
class Exp:
    typ: str
    val: str
    childs: object

def parse(toks):
    def balancebraces():
        nonlocal toks, pos
        endpos = pos + 1
        cnt = 1
        while cnt > 0:
            if endpos >= len(toks):
                raise Exception("unbalanced curly braces")
            if toks[endpos].typ == "{":
                cnt += 1
            elif toks[endpos].typ == "}":
                cnt -= 1
            endpos += 1
        return endpos

    # first pass: recurse for curly braces
    pos = 0
    exps = []
    while pos < len(toks):
        if toks[pos].typ == "{":
            endpos = balancebraces()
            subexp = parse(toks[pos+1:endpos-1])
            exps.append(subexp)
            pos = endpos-1
        elif toks[pos].typ == "}":
            raise Exception("unbalanced curly braces")
        else:
            exps.append(Exp(toks[pos].typ, toks[pos].val, None))
        pos += 1
    
    # second pass: join sub sup with their operand
    pos = 0
    expout = []
    while pos < len(exps):
        if exps[pos].typ in "^_":
            if pos == 0 or pos == len(exps) - 1:
                raise Exception("expression can't start or end with ^_")
            left = exps[pos-1]
            right = exps[pos+1]
            expout = expout[:-1]
            expout.append(Exp(exps[pos].typ, exps[pos].val, [left, right]))
            pos += 1
        else:
            expout.append(exps[pos])
        pos += 1

    if len(expout) > 1:
        return Exp("row", None, expout)
    else:
        return expout[0]

def emit(ast):
    return f"<math>{emitexp(ast)}</math>"

def emitexp(exp):
    if exp.typ == "row":
        out = "<mrow>"
        for child in exp.childs:
            out += emitexp(child)
        out += "</mrow>"
        return out
    elif exp.typ == "^":
        return f"<msup>{emitexp(exp.childs[0])}{emitexp(exp.childs[1])}</msup>"
    elif exp.typ == "_":
        return f"<msub>{emitexp(exp.childs[0])}{emitexp(exp.childs[1])}</msub>"
    elif exp.typ == "identifier":
        return f"<mi>{exp.val}</mi>"
    elif exp.typ == "operator":
        return f"<mo>{exp.val}</mo>"
    elif exp.typ == "number":
        return f"<mn>{exp.val}</mn>"
    elif exp.typ == "command":
        if exp.val not in commands:
            raise Exception(f"unkown command {exp.val}")
        return emitexp(Exp("operator", commands[exp.val], None))
    return ""

def convertmath(tex):
    toks = tokenize(tex)
    exp = parse(toks)
    return emit(exp)

def convert(html):
    chunks = html.split("$")
    if len(chunks) % 2 != 1:
        raise Exception("unbalanced $")

    out = ""
    for idx, chunk in enumerate(chunks):
        if idx % 2 == 1:
            out += convertmath(chunk)
        else:
            out += chunk
    return out