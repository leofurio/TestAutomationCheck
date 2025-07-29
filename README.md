# TestAutomationCheck

Questo progetto permette di eseguire test automatizzati su pagine web utilizzando [Microsoft Playwright](https://playwright.dev/). I test vengono descritti tramite un file JSON contenente le istruzioni in linguaggio naturale.

## Installazione

1. Installare le dipendenze Python:

```bash
pip install -r requirements.txt
playwright install
```

2. Eseguire un test di esempio:

```bash
python run_test.py example_test.json
```

## Formato del file di test

Un test è definito da un file JSON con i seguenti campi:

- `name`: nome del test.
- `url`: indirizzo della pagina da testare.
- `variables`: dizionario di variabili utilizzabili all'interno della descrizione.
- `description`: lista di istruzioni in linguaggio naturale separate da punti.

Esempio (`example_test.json`):

```json
{
  "name": "Modulo contatto demo",
  "url": "https://example.com/contact",
  "variables": {
    "nome": "Mario",
    "email": "mario@example.com",
    "messaggio": "Ciao, questo è un test"
  },
  "description": "Click on the Contact link. Fill the nome field with {{nome}}. Fill the email field with {{email}}. Fill the messaggio textarea with {{messaggio}}. Click the submit button. Verify that confirmation message contains 'Grazie'."
}
```

Le variabili racchiuse tra `{{` e `}}` vengono sostituite con i valori specificati in `variables` prima dell'esecuzione del test.

## Limitazioni

Il parser compreso in `run_test.py` scompone il testo in frasi e riconosce alcune azioni in base al verbo iniziale ("click", "fill", "select", "expect", "go", "wait"). Il target e l'eventuale valore vengono estratti con espressioni regolari. Se una frase non corrisponde a nessuna regola viene riportato un passaggio TODO. È comunque possibile estendere le regole personalizzando `parse_step` e `execute_step`.

## Screenshot in caso di errore

Se durante l'esecuzione di un test avviene un errore, il programma cattura uno screenshot della pagina corrente e lo salva nel file `error_step_<numero>.png` nella cartella da cui viene eseguito lo script.
