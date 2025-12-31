#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p out

# Compile LaTeX to PDF with output in out folder
pdflatex -output-directory=out main.tex

echo "PDF generated in out/main.pdf"
