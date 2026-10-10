# Makefile para compilar el código fuente en src/
CC ?= gcc
CFLAGS = -O2 -Wall -fopenmp

lab12: lab12_speedup.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f lab12

.PHONY: clean
