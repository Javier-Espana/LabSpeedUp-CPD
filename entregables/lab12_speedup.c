/*
 * lab12_speedup.c — VERSIÓN RETO OPCIONAL (Lab 12, CC3069)
 *
 * Cambios respecto a la versión original:
 * ----------------------------------------
 * 1. Se añadió el experimento exp_superlineal() que busca intencionalmente
 *    speedup superlineal (S > p) mediante el efecto de caché distribuida.
 *
 * ¿Por qué ocurre el speedup superlineal?
 * -----------------------------------------
 * Cada núcleo tiene su propia caché L2 privada (1 MiB) y comparten la L3 (16 MiB).
 * Cuando el arreglo completo es demasiado grande para caber en la L3 de un solo
 * núcleo pero, al dividirlo entre p hilos, el fragmento de cada hilo SÍ cabe en su
 * caché L2 privada, se eliminan los fallos de caché masivos.
 * Resultado: cada hilo lee su trozo directamente de L2 (~10 ciclos/acceso)
 * en lugar de ir a RAM (~100 ciclos/acceso), lo que produce un tiempo paralelo
 * desproporcionadamente menor que Ts/p → S > p.
 *
 * En nuestro AMD Ryzen 5 8400F (6 núcleos, 12 lógicos):
 *   - L1d: 192 KiB total (6 × 32 KiB por núcleo)
 *   - L2:    6 MiB total (6 × 1 MiB por núcleo)
 *   - L3:   16 MiB compartida
 *
 * Arreglos alrededor del límite L3 (~16 MiB total / ~8 MiB por grupo SMT)
 * son los candidatos a generar S > p con p = 2 o p = 4.
 *
 * Nota sobre "falso" speedup superlineal:
 * Si S > p solo en una corrida, podría ser ruido de medición.
 * Aquí ejecutamos REPS = 7 repeticiones y reportamos la mediana para
 * garantizar repetibilidad (se requieren ≥ 5 corridas externas además).
 */

#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ITERS 1000
#define REPS  7     /* Aumentado de 5 a 7 para mayor robustez estadística */

#define BARRERA() __asm__ volatile("" ::: "memory")

static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}
static double mediana_n(double *v, int n) {
    qsort(v, n, sizeof(double), cmp_d);
    return v[n / 2];
}

static double checksum = 0.0;
static volatile double semilla = 1.2345;

static inline double unidad(double x, int iters) {
    for (int k = 0; k < iters; k++) x = x * 0.9999999 + 1e-7;
    return x;
}

static double parte_secuencial(long ns) {
    double x = semilla;
    for (long i = 0; i < ns; i++) x = unidad(x, ITERS);
    return x;
}

static double programa_seq(long ns, long np) {
    double acc = parte_secuencial(ns);
    for (long i = 0; i < np; i++) acc += unidad((double)i, ITERS);
    return acc;
}

static double programa_par(long ns, long np, int p, double *t_parte_seq) {
    double t0 = omp_get_wtime();
    double acc = parte_secuencial(ns);
    *t_parte_seq = omp_get_wtime() - t0;
    double suma = 0.0;
#pragma omp parallel for num_threads(p) reduction(+ : suma) schedule(static)
    for (long i = 0; i < np; i++) suma += unidad((double)i, ITERS);
    return acc + suma;
}

static double medir_seq(long ns, long np) {
    double v[REPS];
    for (int r = 0; r < REPS; r++) {
        double t0 = omp_get_wtime();
        checksum += programa_seq(ns, np);
        v[r] = omp_get_wtime() - t0;
    }
    return mediana_n(v, REPS);
}

static double medir_par(long ns, long np, int p, double *t_ps) {
    double v[REPS], vps[REPS];
    for (int r = 0; r < REPS; r++) {
        double t0 = omp_get_wtime();
        checksum += programa_par(ns, np, p, &vps[r]);
        v[r] = omp_get_wtime() - t0;
    }
    double m = mediana_n(v, REPS);
    for (int r = 0; r < REPS; r++)
        if (v[r] == m) { *t_ps = vps[r]; break; }
    return m;
}

/* ===================== Experimento 1: Amdahl ===================== */
static void exp_amdahl(long W, double fp, int pmax) {
    long np = (long)(W * fp + 0.5), ns = W - np;
    double ts = medir_seq(ns, np);
    for (int p = 1; p <= pmax; p++) {
        double tps, tp = medir_par(ns, np, p, &tps);
        printf("amdahl,%ld,%d,fp=%.2f,%.6f,%.6f,%.6f\n", W, p, fp, ts, tp, tps);
        fflush(stdout);
    }
}

/* ============ Experimento 2: suma ============ */
static void exp_suma(int pmax) {
    long tamanos[] = {16, 1024, 65536, 1048576, 16777216};
    int nt = sizeof(tamanos) / sizeof(tamanos[0]);
    long nmax = tamanos[nt - 1];
    double *a = malloc(nmax * sizeof(double));
    if (!a) { fprintf(stderr, "sin memoria\n"); exit(1); }
    for (long i = 0; i < nmax; i++) a[i] = 1.0 / (double)(i + 1);
    int ps[64], nps = 0;
    for (int p = 1; p <= pmax; p *= 2) ps[nps++] = p;
    if (ps[nps - 1] != pmax) ps[nps++] = pmax;
    { double s = 0.0; for (long i = 0; i < nmax; i++) s += a[i]; checksum += s; }
    for (int k = 0; k < nt; k++) {
        long n = tamanos[k];
        long R = 50000000L / n;
        if (R < 3) R = 3;
        if (R > 100000) R = 100000;
        double v[REPS];
        for (int rep = 0; rep < REPS; rep++) {
            double t0 = omp_get_wtime();
            for (long r = 0; r < R; r++) {
                double s = 0.0;
                for (long i = 0; i < n; i++) s += a[i];
                checksum += s; BARRERA();
            }
            v[rep] = (omp_get_wtime() - t0) / R;
        }
        double ts = mediana_n(v, REPS);
        for (int j = 0; j < nps; j++) {
            int p = ps[j];
            for (int rep = 0; rep < REPS; rep++) {
                double t0 = omp_get_wtime();
                for (long r = 0; r < R; r++) {
                    double s = 0.0;
#pragma omp parallel for num_threads(p) reduction(+ : s) schedule(static)
                    for (long i = 0; i < n; i++) s += a[i];
                    checksum += s; BARRERA();
                }
                v[rep] = (omp_get_wtime() - t0) / R;
            }
            double tp = mediana_n(v, REPS);
            printf("suma,%ld,%d,R=%ld,%.9f,%.9f,0\n", n, p, R, ts, tp);
            fflush(stdout);
        }
    }
    free(a);
}

/* ============ Experimento 3: desbalance ============ */
static inline int costo(long i, long W) { return 1 + (int)((2.0 * ITERS * i) / W); }

static void exp_desbalance(const char *sched, long W, int pmax) {
    omp_sched_t kind = omp_sched_static;
    int chunk = 0;
    if (strcmp(sched, "dynamic") == 0) { kind = omp_sched_dynamic; chunk = 64; }
    else if (strcmp(sched, "guided") == 0) { kind = omp_sched_guided; chunk = 0; }
    else if (strcmp(sched, "static") != 0) { fprintf(stderr, "schedule inválido: %s\n", sched); exit(1); }
    omp_set_schedule(kind, chunk);
    double v[REPS];
    for (int rep = 0; rep < REPS; rep++) {
        double t0 = omp_get_wtime(), acc = 0.0;
        for (long i = 0; i < W; i++) acc += unidad((double)i, costo(i, W));
        v[rep] = omp_get_wtime() - t0;
        checksum += acc;
    }
    double ts = mediana_n(v, REPS);
    for (int p = 1; p <= pmax; p++) {
        for (int rep = 0; rep < REPS; rep++) {
            double t0 = omp_get_wtime(), acc = 0.0;
#pragma omp parallel for num_threads(p) reduction(+ : acc) schedule(runtime)
            for (long i = 0; i < W; i++) acc += unidad((double)i, costo(i, W));
            v[rep] = omp_get_wtime() - t0;
            checksum += acc;
        }
        double tp = mediana_n(v, REPS);
        printf("desbalance,%ld,%d,%s,%.6f,%.6f,0\n", W, p, sched, ts, tp);
        fflush(stdout);
    }
}

/* ============ Experimento 4: Gustafson ============ */
static void exp_gustafson(long w_por_hilo, long w_seq, int pmax) {
    for (int p = 1; p <= pmax; p++) {
        long np = w_por_hilo * p;
        double ts = medir_seq(w_seq, np);
        double tps, tp = medir_par(w_seq, np, p, &tps);
        printf("gustafson,%ld,%d,Wseq=%ld,%.6f,%.6f,%.6f\n", w_seq + np, p, w_seq, ts, tp, tps);
        fflush(stdout);
    }
}

/*
 * ============================================================
 * RETO OPCIONAL: Speedup Superlineal por Efecto de Caché
 * ============================================================
 *
 * Estrategia:
 *   Se elige un arreglo de tamaño N tal que:
 *     - La versión secuencial lo lee desde RAM (N > L3/p → muchos cache misses)
 *     - Con p hilos, cada fragmento cabe en la L2 privada de cada núcleo
 *       → los accesos van a caché L2 (~10 ciclos) en lugar de RAM (~100 ciclos)
 *
 * Para el AMD Ryzen 5 8400F:
 *   - L2 por núcleo:  1 MiB = 131,072 doubles
 *   - L3 total:      16 MiB = 2,097,152 doubles
 *   - Con N = 786,432 (6 MiB de doubles):
 *       * Secuencial: no cabe en L3 cuando hay otros procesos → falla a RAM
 *       * Con p=2: fragmento = 3 MiB → no cabe en L2 (1 MiB)
 *       * Con N = 1,572,864 (12 MiB):
 *           - Secuencial: excede L3 → accesos a RAM
 *           - p=2: fragmento = 6 MiB → tampoco cabe en L2 pero ocupa L3 mejor
 *           - p=4: fragmento = 3 MiB → apenas cabe en L3, mejor hit rate
 *
 * El reto usa N alrededor de la frontera L3 y muestra que la mediana (no min)
 * supera S = p en varias corridas consecutivas.
 */
static void exp_superlineal(int pmax) {
    /*
     * Tamaños escogidos estratégicamente:
     *   - 786,432  doubles = 6 MB: justo bajo la L3 dividida (p=2)
     *   - 1,572,864 doubles = 12 MB: supera la L3 del grupo SMT de 2 núcleos
     *   El objetivo es el punto de inflexión donde la caché distribuida da ventaja.
     */
    long tamanos[] = {786432, 1572864};
    int nt = 2;
    long nmax = tamanos[nt - 1];

    double *a = malloc(nmax * sizeof(double));
    if (!a) { fprintf(stderr, "sin memoria\n"); exit(1); }
    for (long i = 0; i < nmax; i++) a[i] = 1.0 / (double)(i + 1);

    /* Calentamiento: llevamos datos a caché para que la primera medición no sea ruido */
    { double s = 0.0; for (long i = 0; i < nmax; i++) s += a[i]; checksum += s; }

    int ps[64], nps = 0;
    for (int p = 1; p <= pmax; p *= 2) ps[nps++] = p;
    if (ps[nps - 1] != pmax) ps[nps++] = pmax;

    for (int k = 0; k < nt; k++) {
        long n = tamanos[k];
        long R = 50000000L / n;
        if (R < 10) R = 10;
        if (R > 20000) R = 20000;

        double v[REPS];
        /* Medición secuencial — leemos con caché fría (flush implícito por el tamaño) */
        for (int rep = 0; rep < REPS; rep++) {
            double t0 = omp_get_wtime();
            for (long r = 0; r < R; r++) {
                double s = 0.0;
                for (long i = 0; i < n; i++) s += a[i];
                checksum += s;
                BARRERA();
            }
            v[rep] = (omp_get_wtime() - t0) / R;
        }
        double ts = mediana_n(v, REPS);

        for (int j = 0; j < nps; j++) {
            int p = ps[j];
            if (p < 2) continue; /* sin paralelismo no hay efecto caché distribuida */
            for (int rep = 0; rep < REPS; rep++) {
                double t0 = omp_get_wtime();
                for (long r = 0; r < R; r++) {
                    double s = 0.0;
                    /* Cada hilo trabaja sobre un fragmento contiguo (cache-friendly) */
#pragma omp parallel for num_threads(p) reduction(+ : s) schedule(static)
                    for (long i = 0; i < n; i++) s += a[i];
                    checksum += s;
                    BARRERA();
                }
                v[rep] = (omp_get_wtime() - t0) / R;
            }
            double tp = mediana_n(v, REPS);
            double S = ts / tp;
            double E = S / p;
            /* Imprimimos en formato CSV estándar */
            printf("superlineal,%ld,%d,N_MB=%.1f,%.9f,%.9f,0.0\n",
                   n, p, (n * 8.0) / (1024 * 1024), ts, tp);
            fprintf(stderr, "N=%ld (%.1f MB), p=%d: S=%.4f, E=%.4f %s\n",
                    n, (n * 8.0) / (1024 * 1024), p, S, E,
                    (S > p ? "--> SUPERLINEAL! (S > p)" : ""));
            fflush(stdout);
        }
    }
    free(a);
}

int main(int argc, char **argv) {
    int ncpu = omp_get_num_procs();
    if (argc < 2) {
        fprintf(stderr,
                "Uso:\n"
                "  %s amdahl       [W=400000] [fp=0.90] [pmax=%d]\n"
                "  %s suma         [pmax=%d]\n"
                "  %s desbalance   [static|dynamic|guided] [W=40000] [pmax=%d]\n"
                "  %s gustafson    [W_por_hilo=100000] [W_seq=20000] [pmax=%d]\n"
                "  %s superlineal  [pmax=%d]   <-- RETO OPCIONAL\n",
                argv[0], ncpu, argv[0], ncpu, argv[0], ncpu,
                argv[0], ncpu, argv[0], ncpu);
        return 1;
    }
    printf("modo,N,p,param,t_seq,t_par,t_parte_seq\n");
    const char *modo = argv[1];
    if (strcmp(modo, "amdahl") == 0) {
        long W    = argc > 2 ? atol(argv[2]) : 400000;
        double fp = argc > 3 ? atof(argv[3]) : 0.90;
        int pmax  = argc > 4 ? atoi(argv[4]) : ncpu;
        exp_amdahl(W, fp, pmax);
    } else if (strcmp(modo, "suma") == 0) {
        int pmax = argc > 2 ? atoi(argv[2]) : ncpu;
        exp_suma(pmax);
    } else if (strcmp(modo, "desbalance") == 0) {
        const char *s = argc > 2 ? argv[2] : "static";
        long W = argc > 3 ? atol(argv[3]) : 40000;
        int pmax = argc > 4 ? atoi(argv[4]) : ncpu;
        exp_desbalance(s, W, pmax);
    } else if (strcmp(modo, "gustafson") == 0) {
        long wph = argc > 2 ? atol(argv[2]) : 100000;
        long wsq = argc > 3 ? atol(argv[3]) : 20000;
        int pmax = argc > 4 ? atoi(argv[4]) : ncpu;
        exp_gustafson(wph, wsq, pmax);
    } else if (strcmp(modo, "superlineal") == 0) {
        int pmax = argc > 2 ? atoi(argv[2]) : ncpu;
        exp_superlineal(pmax);
    } else {
        fprintf(stderr, "modo desconocido: %s\n", modo);
        return 1;
    }
    fprintf(stderr, "(checksum %.3e)\n", checksum);
    return 0;
}
