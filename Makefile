# Lab 12 — Speedup y Eficiencia (CC3069)
# Makefile principal del repositorio

CC ?= gcc
CFLAGS = -O2 -Wall -fopenmp

all: lab12

lab12: src/lab12_speedup.c
	$(CC) $(CFLAGS) -o $@ $<

pdfs:
	@echo "Compilando informes en informes/..."
	cd informes && pdflatex -interaction=nonstopmode reporte_lab12.tex
	cd informes && pdflatex -interaction=nonstopmode evidencia_lab12.tex
	cp informes/reporte_lab12.pdf informes/evidencia_lab12.pdf entregables/
	rm -f informes/*.aux informes/*.log informes/*.out informes/*.toc

clean:
	rm -f lab12 src/lab12 informes/*.aux informes/*.log informes/*.out informes/*.toc

.PHONY: all pdfs clean
