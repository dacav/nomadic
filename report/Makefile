.PHONY : all clean index

SUBTEXS := $(shell find sections -name '*.tex') settings.tex
TEX := report.tex
PDF := $(TEX:.tex=.pdf)

all: $(PDF)

index: all
	pdflatex $(TEX) 2> /dev/null
	pdflatex $(TEX) 2> /dev/null

$(PDF) : $(TEX) $(SUBTEXS)
	pdflatex $(TEX)

clean:
	rm -f $(PDF) *.aux *.log *.out *.toc

