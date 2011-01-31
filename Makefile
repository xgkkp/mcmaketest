all: doc

doc: doc/README.html

doc/README.html: README.txt
	rst2html.py README.txt > doc/README.html