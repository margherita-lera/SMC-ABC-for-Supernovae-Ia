## 11/02 - Margherita
Resoconto discussione con Liguori: SNANA ha bisogno sostanzialmente dei dati Pantheon+ nel formato giusto
per fare il fit. Mi sembra che ci siano dei files utili a riguardo, check capitolo 5.2. 
Poi serve il file .INPUT per fare partire la simulazione. Ci serve un file ad hoc per il dataset pantheon, in
particolare: ci serve avere gli stessi constraint di redshift, osservazione, ... Non ho trovato un file input 
per Pantheon nello specifico. Da capire se c'è in internet/git oppure se si può modificare un altro file 
input con i parametri giusti una volta che abbiamo capito bene i dati di Pantheon.
LATO SMC-ABC: L'algoritmo si può già cominciare a implementare separatamente. Liguori consiglia di usare una semplice MVN come esempio per sampling 
e simulazione invece dei dati SNANA.

## 12/02 - Marghe
Gigi forse ha capito come mettere dentro i parametri cosmologici nelle simulazioni.

Quello che ho capito per ora è che ci serve da Snana:

Per i dati reali, per ogni curva:
- reperire il redshift z (noto! redshift spettroscopico),
- estrarre 7 punti
- fare il fit (mlcs2k2, o salt) in modo da tirare fuori il modulo di distanza mu. Ci dovrebbe uscire dal fit diretto.

Per i dati simulati, Noti omega_m, w:
- far partire 200 simulazioni di curva di luce,
- estrarne 7 punti e il redshift che è stato simulato,
- dai 7 punti ricavare mu (come sopra).
Questo è tutto quello che ci serve. Ottenuto mu e z per sia dati che simulazioni siamo a cavallo.
Intanto sto abbozzando l'algoritmo di ABC con dati finti e sfruttando la distanza di luminosità per mu.

## Gigi 12/02

generare curve di luce:
 - Vai in `$SNDATA_ROOT/sample_input_files/` e scegli il file di input che ti serve. (occhio che alcuni all'interno ne chiamano un altro per cui controlla di prenderli tutti e due.)
 - fai una copia, modifica `GENVERSION` (sarà il nome della tua run) e.g. {tuonome}
 - modifica `NGENTOT_LC` e `NGEN_LC` con i numeri che vuoi. Il primo sono i tentativi il secondo i tentativi che vengono salvati i think
 - vai in `$SNANA_DIR/bin`
 - scrivi `snlc_sim.exe file.input` (`file.input` è quello che hai scelto ricorda che se ne include un altro modifica il path del file in `file.input`)
 - premi invio. il programma parte.
 - I risultati si trovano in `$SNDATA_ROOT/SIM/{tuonome}/`
 - dentro questa cartella ci sono i tuoi risultati. Il formato degli output dipende da una flag in `file.input` chiamata `FORMAT_MASK`, se è 2 l'output è in .DAT e human readable, altrimenti è in .FITS.

come cambiare `OMEGA_MATTER` e `w0_LAMBDA` (o analoghi parametri in `$SNANA_DIR/src/sntools.h`):
 - li setti nell'input file:
    - `OMEGA_MATTER`:  valore_Che_vuoi
    - `OMEGA_LAMBDA`:  valore_Che_vuoi
 - oppure mentre lanci il programma: `snlc_sim.exe file.input OMEGA_MATTER 0.315 OMEGA_LAMBDA 0.685`
 - puoi verificare che hai usato valori diversi da quelli di default guardando in `$SNDATA_ROOT/SIM/{tuonome}/{tuonome}.README`

## Gigi 13/02

Basandomi sull'ultima direttiva di Margherita, mi sono occupato di estrarre 7 punti dai file .dat output di snlc_sim.exe. Siccome SNANA non permette una selezione randomica delle epochs che formano la curva di luce, ho fatto una funzione python. Vedi branch fitting7points
