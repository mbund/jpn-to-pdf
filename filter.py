#!/usr/bin/env python
import json
import sys

from black import out


def main():
    fp = sys.stdin
    # fp = open('test.json')
    doc = json.load(fp)
    doc['blocks'] = [x for block in doc['blocks']
                     if (x := do_cell(block)) is not None]
    json.dump(doc, sys.stdout)

# Return None or the modified cell


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

    if (name := get_figure_or_show(code['c'][1])) is not None:
        if name == '':  # show
            return output
        # figure
        return Div(
            [
                RawBlock(r'\begin{figure}[h]'),
                Plain([
                    RawInline(r'\caption{'),
                    Str(name),
                    RawInline(r'}'),
                ]),
                output,
                RawBlock(r'\end{figure}')
            ]
        )
    elif output:
        return None


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


def get_figure_or_show(source: str):
    lines = source.split('\n')
    for line in lines:
        l = line.lstrip()
        if l.startswith(r'%figure'):
            arg = l.partition(' ')[2]
            name = json.loads(arg)
            assert isinstance(name, str)
            return name
        if l.startswith(r'%show'):
            return ''
    return None


if __name__ == "__main__":
    main()
