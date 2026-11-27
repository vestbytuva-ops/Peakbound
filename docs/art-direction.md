# Visuell retning for Peakbound

Spilleren ser bilen fra siden i et Pygame-vindu på 1280 × 720. Uttrykket er inspirert av et trykt feltkart for fjellruter, med blokkerte pikselflater, matte farger og tydelig forskjell mellom spillets forgrunn og fjellene i det fjerne.

## Farger og form

- **Spillobjekter.** Grafittkonturer (`#20262b`), lyse flater i elfenben, kobberrød Ridge og okergul Tinde. Bruk rustrødt til drivstoff og skadet last. Bruk varmt gull til mynter og andre belønninger.
- **Landskap.** Det bakerste fjellet har roligere farger og færre kontraster enn kjørebanen. Høylys på venstre vendte fjellflater samler scenen rundt én lysretning. Sikt på store, gjenkjennelige silhuetter og få grupper av tekstur.
- **Variasjon.** Everest bruker kalde blåtoner og brede snørygger. K2 bruker mørke bergflater og rust i himmelen. Kilimanjaro bruker et bredt vulkanfjell og varme jordtoner. Fjellveien beholder landskapet fra den første versjonen.
- **Lesbarhet.** Bruk den lyseste sammenhengende kanten til å vise kjøreflaten. Mynt, drivstoff og pakke skal kunne skilles på silhuetten. Funksjonstekst og tall tegnes av Pygame.

## Pikselrutenett

Karosseriet tegnes på en gjennomsiktig flate på 64 × 32. Det skaleres til 128 × 64 med nærmeste piksel. Hjulene er 13 × 13 på kildenivå. Begge biler bruker de samme hjulankrene, 24 piksler under karosseribilde-midtpunktet etter skalering. Posthytta forankres ved bakken. Spritene bruker mellom 6 og 11 farger med gjennomsiktighet medregnet.

Se over en sprite både på lys snø og foran mørke berg. Kontroller hjulenes kontaktpunkt på flatmark og i en bakke. Se gjennom landskapslagene mens kameraet flytter seg, særlig når et lag begynner på nytt langs x-aksen.

Arbeidsflyten følger [Create Game Assets](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/c6ca6c41c839b68319ffc08430b99ab768debc32/skills/disciplines/create-game-assets/SKILL.md) og [pygame Core](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/c6ca6c41c839b68319ffc08430b99ab768debc32/skills/other-engines/pygame-core/SKILL.md). Bruk [grafikkoversikten](asset-manifest.json) når du legger til eller erstatter grafikk.
