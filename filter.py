#!/usr/bin/env python
import json
import sys
import re

from black import out


def main():
    fp = sys.stdin
    # fp = open('test.json')
    doc = json.load(fp)
    doc['blocks'] = [x for block in doc['blocks']
                     if (x := do_cell(block)) is not None]
    doc['blocks'] += [
        RawBlock("\\clearpage"),
        Header(1, [Str('Appendix')]),
        CodeBlock('\n\n'.join(codes), classes=['python'])
    ]
    json.dump(doc, sys.stdout)

# Return None or the modified cell


codes = []


def do_cell(cell):
    assert cell['t'] == 'Div'
    attr, body = cell['c']
    _id, classes, _metadata = attr
    assert 'cell' in classes

    if not 'code' in classes:
        # leave markdown alone
        return cell

    code = next(b for b in body if b['t'] == 'CodeBlock')
    output = next(
        (b for b in body if b['t'] == 'Div' and 'output' in b['c'][0][1]), None)

    source = code['c'][1]
    if (match := re.search(r'^%figure\s+(.*)$', source, re.MULTILINE)):
        # figure
        codes.append(source[0:match.start()] + source[match.end():])
        return Div(
            [
                RawBlock(r'\begin{figure}[h]'),
                Plain([
                    RawInline(r'\caption{'),
                    Str(json.loads(match[1])),
                    RawInline(r'}'),
                ]),
                output,
                RawBlock(r'\end{figure}')
            ]
        )
    elif (match := re.search(r'^%show', source, re.MULTILINE)):
        # show
        # do NOT include in code listing
        return output
    else:
        codes.append(source)


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


def CodeBlock(text, id='', classes=[], keyvalues=[]):
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
