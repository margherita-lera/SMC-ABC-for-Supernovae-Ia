## 11/02 - Margherita
Resoconto discussione con Liguori: SNANA ha bisogno sostanzialmente dei dati Pantheon+ nel formato giusto
per fare il fit. Mi sembra che ci siano dei files utili a riguardo, check capitolo 5.2. 
Poi serve il file .INPUT per fare partire la simulazione. Ci serve un file ad hoc per il dataset pantheon, in
particolare: ci serve avere gli stessi constraint di redshift, osservazione, ... Non ho trovato un file input 
per Pantheon nello specifico. Da capire se c'è in internet/git oppure se si può modificare un altro file 
input con i parametri giusti una volta che abbiamo capito bene i dati di Pantheon.
LATO SMC-ABC: L'algoritmo si può già cominciare a implementare separatamente. Liguori consiglia di usare una semplice MVN come esempio per sampling 
e simulazione invece dei dati SNANA.
