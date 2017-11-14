# FantaStat 2.0

Questa applicazione scritta in Python 2.7.8, serve per visualizzare le statistiche
dei calciatori di una lega di fantacalcio.
Il database player importa i file txt standard del MagicCupCampionato (MCCnn.txt),
con formato:
    'code|NAME|TEAM|fanta voto|voto|quotazione'
e sarà possibile modificare gli stessi dati dei giocatori o delle valutazioni,
in caso si verificassero errori.

## Moduli utilizzati

Vengono usate le librerie wx per la grafica e django come ORM.

## Operazioni preliminari

Dopo aver installato django e le librerie wx, creare il database.

Creazione database:

```
python manage.py makemigrations players
```

in seguito:

```
python manage.py migrate
Operations to perform:
  Apply all migrations: players
Running migrations:
  Applying players.0001_initial... OK
```

una volta creato il database players.db, lanciare l'applicazione.

```
>python main.py
```

L'iter è il seguente:
prima si importano i giocatori, poi le valutazioni.
Una volta importati i giocatori, non si potranno più importare, se non 
dopo la cancellazione dei dati. Questo per aver sottocontrollo il
cambiamento della quotazione di un giocatore. Ogni nuovo giocatore valutato
nelle giornate successive, sarà inserito a database durante l'importazione
delle valutazioni.


### 1. Importare i giocatori

Dal menu 'Import -> import players' selezionare i file txt dalla cartella days 
(alcune giornate vengono fornite da esempio), o direttamente dal web
https://bancaldo.wordpress.com/2017/08/23/lista-calciatori-gazzetta-2017-2018/
Il numero di giornata viene estratto direttamente dal nome del file,
il formato di tale file deve essere similare agli standard MCCnn.txt, dove
nn indica il numero di giornata


### 2. Importare i voti

Dal menu 'Import -> import evaluations' selezionare i file txt dalla cartella days.

### 3. Pannello Principale

All'avvio della applicazione, con i dati caricati sarà possibile visualizzare le
statistiche di ogni giocatore: media_fantavoto, media_voto, rapporto partite giocate/partite 
disputate, variazione di valore dalla prima giornata. In caso non siano presenti dati sul 
database, un messaggio avviserà di effettuare l'importazione degli stessi

### 4. Players Summary

Visualizza il sommario dei giocatori disponibili, filtrabili per ruolo.
Cliccando sulla colonna si ordinano i dati per quel campo, mentre
cliccando sulla cella, si può editare il calciatore per modificarlo

### 5. Evaluations Summary

Visualizza il sommario dei voti, selezionabili per giornata e per ruolo.
Cliccando sulla colonna si ordinano i dati per quel campo, mentre
cliccando sulla cella, si può editare il voto per modificarlo

### 6. Evaluations Summary

Il reset dei dati viene effettuato dal menu Reset, sia i giocatori che
le valutazioni, dovranno essere rieseguite da zero.

## Licenza

GPL
