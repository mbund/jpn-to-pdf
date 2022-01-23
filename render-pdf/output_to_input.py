import nbformat
import sys
import re

f = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
nb = nbformat.reads(f.read(), nbformat.NO_CONVERT)

def output_to_input(cell):
    if cell.cell_type == "code":
        for output in cell.outputs:
            if "data" in output and "text/markdown" in output.data and re.search(r'^%render', cell.source, re.MULTILINE):
                return nbformat.v4.new_markdown_cell(output.data["text/markdown"])
    return cell


nb.cells = list(map(output_to_input, nb.cells))
print(nbformat.writes(nb))
