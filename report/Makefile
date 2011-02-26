.PHONY : all clean index

SUBTEXS := $(shell find sections -name '*.tex') settings.tex
TEX := report.tex
PDF := $(TEX:.tex=.pdf)

all: $(PDF)

index: all
	pdflatex $(TEX) 2> /dev/null
	pdflatex $(TEX) &> /dev/null

$(PDF) : $(TEX) $(SUBTEXS)
	pdflatex $(TEX) 2> /dev/null

clean:
	rm -f $(PDF) *.aux *.log *.out *.toc

