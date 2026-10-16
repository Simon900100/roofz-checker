# Roofz checker

Checkt ieder uur roofz.eu op nieuwe woningen in Amsterdam en stuurt je een pushmelding op je telefoon. Draait gratis op GitHub, dus je laptop hoeft niet aan te staan.

## Installeren (ongeveer 10 minuten)

1. Zet de app **ntfy** op je telefoon (gratis, iOS en Android).
2. Verzin een topicnaam die niemand kan raden, bijvoorbeeld `roofz-simon-8k3p2x`. Abonneer je in de app op dat topic.
3. Maak op github.com een nieuwe **private** repository aan en upload deze bestanden. Let op dat de map `.github/workflows` meekomt.
4. Ga in de repo naar Settings > Secrets and variables > Actions > New repository secret. Naam: `NTFY_TOPIC`, waarde: jouw topicnaam.
5. Ga naar de tab Actions, kies "Roofz checker" en klik op "Run workflow".

Na de eerste run krijg je een melding dat de checker aanstaat en hoeveel woningen er nu in Amsterdam online staan. Daarna hoor je alleen nog iets als er een nieuwe bijkomt. Tik op de melding en je gaat direct naar de woning.

## Goed om te weten

- GitHub start geplande runs soms een paar minuten later dan gepland.
- Vindt het script helemaal niks op de site, dan faalt de run en krijg je een mail van GitHub. Meestal betekent dat dat roofz.eu iets aan de site heeft veranderd.
- Een andere stad? Zet in de workflow bij de stap "Check roofz.eu" onder `env:` de regel `ROOFZ_CITY: ROTTERDAM` erbij.
- GitHub zet geplande workflows uit als een repo 60 dagen niks doet. Komt er al die tijd geen nieuwe woning bij, zet hem dan via de Actions-tab weer aan.
