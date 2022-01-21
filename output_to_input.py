import nbformat
import sys
import re
nb = nbformat.reads(sys.stdin.read(), nbformat.NO_CONVERT)


def output_to_input(cell):
    if cell.cell_type == "code":
        for output in cell.outputs:
            if "text/markdown" in output.data and re.search(r'^%show', cell.source, re.MULTILINE):
                return nbformat.v4.new_markdown_cell(output.data["text/markdown"])
    return cell


nb.cells = list(map(output_to_input, nb.cells))
print(nbformat.writes(nb))
