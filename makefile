LATEX	= pdflatex
BIBTEX	= bibtex
MAKEINDEX = makeindex

RERUN = "(There were undefined references|Rerun to get (cross-references|the bars) right)"
RERUNBIB = "No file.*\.bbl|Citation.*undefined"
MAKEIDX = "^[^%]*\\makeindex"

COPY = if test -r $(<:%.tex=%.toc); then cp $(<:%.tex=%.toc) $(<:%.tex=%.toc.bak); fi 
RM = rm -f

SRC	:= $(shell egrep -l '^[^%]*\\begin\{document\}' *.tex)
PDF	= $(SRC:%.tex=%.pdf)

define run-latex
	plantuml $<
	$(COPY);$(LATEX) $<
	egrep $(MAKEIDX) $< && ($(MAKEINDEX) $(<:%.tex=%);$(COPY);$(LATEX) $<) >/dev/null; true
	egrep -c $(RERUNBIB) $(<:%.tex=%.log) && ($(BIBTEX) $(<:%.tex=%);$(COPY);$(LATEX) $<) ; true
	egrep $(RERUN) $(<:%.tex=%.log) && ($(COPY);$(LATEX) $<) >/dev/null; true
	egrep $(RERUN) $(<:%.tex=%.log) && ($(COPY);$(LATEX) $<) >/dev/null; true
	if cmp -s $(<:%.tex=%.toc) $(<:%.tex=%.toc.bak); then true ;else $(LATEX) $< ; fi
	$(RM) $(<:%.tex=%.toc.bak)
	# Display relevant warnings
	egrep -i "(Reference|Citation).*undefined" $(<:%.tex=%.log) ; true
endef

clean:
	-rm -rf plant_*.png $(PDF) $(PDF:%.pdf=%.aux) $(PDF:%.pdf=%.bbl) $(PDF:%.pdf=%.blg) $(PDF:%.pdf=%.log) $(PDF:%.pdf=%.out) $(PDF:%.pdf=%.idx) $(PDF:%.pdf=%.ilg) $(PDF:%.pdf=%.ind) $(PDF:%.pdf=%.toc) $(PDF:%.pdf=%.d) *.pyc postgres.sql xml

all: pdf

pdf: postgres.sql $(PDF)

.PHONY	: all clean pdf xml_dir xml_files pep8 postgres

$(PDF) : %.pdf : %.tex
	@$(run-latex)

pep8:
	pep8 *.py

postgres.sql: pep8
	python postgres.py >postgres.sql

postgres: postgres.sql
	sudo -u postgres psql <postgres.sql

xml_dir:
	mkdir -p xml

xml_files: pep8 xml_dir
	python exist.py

validate_xml: xml_files
	xmllint --dtdvalid http://www.w3.org/2009/XMLSchema/XMLSchema.dtd programmes.xsd
	for xmlfile in `ls xml`; do xmllint --schema programmes.xsd xml/$$xmlfile || exit 1 ; done

exist: xml_files
	/opt/eXist/bin/client.sh -m /db/programmes -p xml

ads-coursework.pdf: xml_files