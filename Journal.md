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

Basandomi sull'ultima direttiva di Margherita, mi sono occupato di estrarre 7 punti dai file .dat output di snlc_sim.exe. Siccome SNANA non permette una selezione randomica delle epochs che formano la curva di luce, ho fatto una funzione python. Vedi branch fitting7points. 

## 13 Gio 02
Questi inetti non riuscirebbero ad accendere una sigaretta con una tanica di benzina e un lanciafiamme, ma per loro immensa fortuna faccio parte del gruppo. Ho fatto un esame, ho mangiato un golosino fritto, ho fatto una vm che forse non useremo e sono tornato a casa contemplando il coma etilico. Non c'è di che.

State lavorando bene piccoli minions, continuate così e se vinciamo vi offro da bere. Se perdiamo beviamo il vino della sconfitta che è stra più buono. Questa era la carota, aspettatevi dieci anni di bastone. Perfettamente bilanciato come fette di torta tagliate con il template di Gab. Ora vado che domattina ci si sveglia presto per fare la spesa al Lidl.

## Gigi 13/02 parte 2

Ieri sono andato a dormire senza aggiornare. Nella vm fatta da gio ho aggiunto due cartelle dentro SNANA: custom_input_files e scripts. In una ho messo delle versioni funzionanti per i nostri scopi degli input files, nell'altra gli script a cui sto lavorando e mi immagino anche quello di marghe. Ho messo un file .LIST in SIM/ in modo che snana non smatti. ho fatto un ambiente conda chiamato abc. Ho finito di fare il wrapper più o meno ora devo testarlo e bisogna capire quali quantità vadano estratte dal FITRES. infatti ci sono almeno 6 quantit relative al redshift e sembra non esistere una quantità sul modulo di distanza, probabilmente questa andrà calcolata ma la formula che ho trovato usa dei parametri che non conosco per cui boh. Forse il problema è SALT2 che non genera questa quantità ma altri motori (non ho ancora capito cosa sia salt2) magari si?

## 15 Gio 02

Ieri abbiamo fatto delle cose, ma non le abbiamo riportate. E chi se ne frega.

Oggi ho finito di leggere il paper, quindi ho potuto rilasciare tutto il mio incontrollato autismo sulla funzione di gg sim_whatever_the_fuck_hubble. Ho sistemato gli output probabilmente ma c'è ancora qualcosa che non mi torna per niente. Also se non l'hai già fatto Margherita dovresti leggere i messaggi del gruppo in cui ci chiediamo se H0 sia davvero 72 e non 65. Ora vado a mangiare perché ho fame, dovrei aver commentato le cose cambiate nella funzione, se c'è qualcosa che proprio non capite siete stupidi e potete chiedermi. Il prossimo passo e separare i tre subprocesses, ma non dovrebbe essere complesso.

## 16 Gio 02
EHEHEEHEHEHEHEHEHEHH volevo fare qualcosa di produttivo, ma sono passato da leggere la doc di SNANA a toccare di nuovo sim_whatever_the_fuck_hubble, creando l'assouluto pazzo terrore delle 01:43 in funky.py.

## 17/02 Margherita
Fatto un altro wrapper con le funzioni di giovanni, imprecato sugli errorini del pazzo terrore delle 01.43. 
Once again i'm asking myself when will we be able to actually start ABC con dei dati veri.

Riporto ora le parole di un vecchio saggio meno gli insulti a margherita: 

Cose che abbiamo capito sul redshift:
- Bisogna leggere il paper bene
- Sulle misure osservate (.DAT files) esiste un redshift heliocentrico ZHEL or some shit e un redshift CMB che è il redshift corretto per il movimento del Sistema Solare (SS per gli amici). Noi vogliamo usare quello (CMB stupido)
- Credevi fosse finita qui e invece esiste anche zHD, che è il redshift ad alta definizione (scherzo gg, non è davvero il suo nome). Da quanto abbiamo visto non c'è nei dati reali, ma possiamo calcolarlo noi con una semplice formula nella sezione 11.2 del manuale di SNANA
- È molto probabile che non esiste davvero un redshift fotometrico e uno spettroscopico, è solo che il paper considera come redshift fotometrico quello simulato e spettroscopico quello osservato. Cosa cambia: per noi una funcia di minchia, TecNiCAmeNtE il redshift spettroscopico è più preciso.
