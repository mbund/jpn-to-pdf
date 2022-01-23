#!/usr/bin/env python
import json
import sys
import re


def main():
    fp = sys.stdin
    doc = json.load(fp)

    # the table of contents should be raw latex in
    # the notebook
    doc['blocks'] = [x for block in doc['blocks']
                     if (x := do_cell(block)) is not None]
    doc['blocks'] += [
        RawBlock("\\clearpage"),
        Header(1, [Str('References')]),
        Div([], id='refs'),
        RawBlock("\\clearpage"),
        Header(1, [Str('Appendix')]),
        *codes
    ]
    json.dump(doc, sys.stdout)


codes = []

# Return None or the modified cell


def do_cell(cell):
    assert cell['t'] == 'Div'
    attr, body = cell['c']
    _id, classes, _metadata = attr
    assert 'cell' in classes

    if 'markdown' in classes:
        header = next((b for b in body if b['t'] == 'Header'), None)
        if header:
            # codes.append(header)
            pass
        return cell

    code = next(b for b in body if b['t'] == 'CodeBlock')
    output = next(
        (b for b in body if b['t'] == 'Div' and 'output' in b['c'][0][1]), None)

    source = code['c'][1]
    if (match := re.search(r'^%figure\s+(.*)$', source, re.MULTILINE)):
        # figure
        codes.append(CodeBlock(source[0:match.start()] + source[match.end():]))
        return Div(
            [
                RawBlock(r'\begin{figure}[h!]'),
                output if output else Div([]),
                Plain([
                    RawInline(r'\caption{'),
                    Str(json.loads(match[1])),
                    RawInline(r'}'),
                ]),
                RawBlock(r'\end{figure}'),
            ]
        )
    elif (match := re.search(r'^%render', source, re.MULTILINE)):
        # do NOT include in code listing
        return output
    else:
        codes.append(CodeBlock(source))


def Str(s):
    return {'t': 'Str', 'c': s}


def Plain(inlines, id='', classes=[], keyvalues=[]):
    return {
        't': 'Plain',
        'c': inlines
    }


def Div(blocks, id='', classes=[], keyvalues=[]):
    return {
        't': 'Div',
        'c': [[id, classes, keyvalues], blocks]
    }


def CodeBlock(text, id='', classes=['python'], keyvalues=[]):
    return {
        't': 'CodeBlock',
        'c': [[id, classes, keyvalues], text]
    }


def RawBlock(latex):
    return {
        't': 'RawBlock',
        'c': ['latex', latex]
    }


def RawInline(latex):
    return {
        't': 'RawInline',
        'c': ['latex', latex]
    }


def Header(level, inlines, id='', classes=[], keyvalues=[]):
    return {
        't': 'Header',
        'c': [level, [id, classes, keyvalues], inlines]
    }


if __name__ == "__main__":
    main()
