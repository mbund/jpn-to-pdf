poetry run "cat paper.ipynb | python output_to_input.py | pandoc --from ipynb --filter filter.py --out test.pdf"