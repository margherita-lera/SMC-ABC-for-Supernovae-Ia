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
