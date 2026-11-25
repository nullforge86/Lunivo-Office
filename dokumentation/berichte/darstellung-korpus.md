# Darstellung: Vergleich mit den Referenz-PDFs

Erzeugt mit `werkzeuge/pruefungen/darstellung_korpus.py`. Jede DOCX der Sammlung wird eingelesen, als PDF ausgegeben und mit ihrem Referenz-PDF verglichen: Seitenzahl, Wortfolge und das Seitenbild der ersten Seiten (Deckung der Schwärzung, farbige Fläche, Zahl der Bilder). Grenzen des Vergleichs: siehe Kopf des Werkzeugs.

## Stand

| Messwert | Anzahl |
|---|---|
| Dateien | 216 |
| lassen sich öffnen und ausgeben | 213 |
| Seitenzahl, Text und Aussehen stimmen | 35 |
| Seitenzahl stimmt | 136 |
| Text stimmt (Wortfolge ab 0.98) | 89 |
| Text fehlt (über 5%) | 20 |
| Text zu viel (über 5%) | 29 |
| Papiergröße weicht ab | 0 |
| Seitenbild deckt sich (ab 0.60) | 100 |
| farbige Fläche fehlt (Formen, Bilder, Farbbalken) | 21 |
| Bilder fehlen | 35 |
| langsamer als 10 s | 5 |

## Seit dem letzten Lauf

Besser: 1, schlechter: 0.

- besser: `12_DOCX_Webkorpus/forms/000e366a02330e96ce5e878a2c2ecceba7374715a1065a5ece914d024a25d951`

## Fehler beim Öffnen oder Ausgeben

| Anzahl | Fehler |
|---|---|
| 2 | DocumentIOError: Die Datei ist kein gültiges DOCX-Dokument oder beschädigt. |
| 1 | DocumentIOError: Die DOCX-Datei ist in einem Teil |

## Hinweise des Importes

| Anzahl | Hinweis |
|---|---|
| 11 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| 7 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| 3 | Bilder mit „Oben und unten“-Umbruch werden als Bild im Text eingefügt. |
| 1 | Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung) und wird nicht angezeigt. |
| 1 | Formeln werden nicht dargestellt und gehen beim Speichern verloren. |

## Lässt sich nicht darstellen (3)

| Datei | Seiten Lunivo / Vorbild | Wörter Lunivo / Vorbild | Wortfolge | Seitenbild | Farbfläche Lunivo / Vorbild | Bilder Lunivo / Vorbild | Fehler oder Hinweis |
|---|---|---|---|---|---|---|---|
| `05_Fehlerfaelle/renamed-extension` | – | – | – | – | – | – | DocumentIOError: Die Datei ist kein gültiges DOCX-Dokument oder beschädigt. |
| `07_Originalsammlungen/FehlerCorpus/araduru-file-format-test-corpus-main/samples/docx/renamed-extension` | – | – | – | – | – | – | DocumentIOError: Die Datei ist kein gültiges DOCX-Dokument oder beschädigt. |
| `Microsoft test dateien/sample-docx-100mb` | – | – | – | – | – | – | DocumentIOError: Die DOCX-Datei ist in einem Teil („word/media/image1.png“) zu groß (99 MB) und wird aus Sicherheitsgründen nicht geöffnet. |

## Weicht ab (178)

| Datei | Seiten Lunivo / Vorbild | Wörter Lunivo / Vorbild | Wortfolge | Seitenbild | Farbfläche Lunivo / Vorbild | Bilder Lunivo / Vorbild | Fehler oder Hinweis |
|---|---|---|---|---|---|---|---|
| `Microsoft test dateien/docx_sample_file_1MB` | 251 / 246 | 164246 / 160683 | 0.00 | 0.93 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/docx_sample_file_500KB` | 123 / 120 | 80209 / 78470 | 0.01 | 0.93 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/docx_sample_file_200KB` | 49 / 48 | 32072 / 31388 | 0.02 | 0.93 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `12_DOCX_Webkorpus/legal/0019967c9e1c5ecf9dd5dbfa886c1c3be5ee054a37aa7e94562841e385bb4c9f` | 261 / 314 | 63977 / 80360 | 0.17 | 0.47 | 0% / 0% | 17 / 1 |  |
| `12_DOCX_Webkorpus/0013bcb8b619da89b3b5c640ffa5c6c3328ed5dad584f10ded67e12c766e5123` | 9 / 5 | 3415 / 3407 | 0.21 | 0.40 | 0% / 1% | 13 / 3 |  |
| `12_DOCX_Webkorpus/legal/001410a84d3ead5f2a1e8a46963a381f0a6634c662e298ac16a00b0dc8d2f353` | 83 / 80 | 20226 / 20869 | 0.24 | 0.51 | 0% / 0% | 5 / 1 |  |
| `12_DOCX_Webkorpus/legal/0010437a7f75f63624beb064e3b380f8a3a6f9b9ca76c645f4a9fcfa7264c7c8` | 608 / 686 | 171260 / 196319 | 0.48 | 0.54 | 0% / 0% | 2 / 2 |  |
| `12_DOCX_Webkorpus/anschreiben/01e530cdbc02450e57fb2e137f4518215b0862f86e90af5463721b56116d2753` | 6 / 3 | 635 / 643 | 0.52 | 0.16 | 2% / 8% | 53 / 1 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `Microsoft test dateien/docx_sample_file_50KB` | 13 / 12 | 8018 / 7847 | 0.60 | 0.93 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `12_DOCX_Webkorpus/bewerbungsformulare/00b75e5f9e64437cb56fe26d7bfefb869f6fa2c7aed22ba1f030ba945ae0ffcc` | 1 / 2 | 147 / 204 | 0.65 | 0.38 | 0% / 0% | 2 / 2 |  |
| `Microsoft test dateien/docx_meeting_notes_sample` | 1 / 1 | 33 / 27 | 0.70 | 0.63 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/009e6ea6dd12b176c3a644cc050a77e7f6befe7bbb4d0eff139e80ab82b834db` | 2 / 2 | 179 / 265 | 0.71 | 0.09 | 0% / 0% | 4 / 3 |  |
| `11_Microsoft_Originale/SampleDoc` | 2 / 2 | 182 / 230 | 0.74 | 0.39 | 3% / 5% | 5 / 12 | Bilder mit „Oben und unten“-Umbruch werden als Bild im Text eingefügt. |
| `12_DOCX_Webkorpus/anschreiben/01a8fbcebbfa2f9223212c56463373e56ef08e14d68e32d9be668fa4005ba705` | 2 / 1 | 352 / 328 | 0.77 | 0.51 | 0% / 0% | 6 / 3 |  |
| `12_DOCX_Webkorpus/0022d9b76a33e7bdcda8d38ec3c898364c578897fb55d462702cdbb1679282eb` | 1 / 1 | 59 / 51 | 0.78 | 0.94 | 0% / 0% | 1 / 2 |  |
| `12_DOCX_Webkorpus/forms/000ee7c0ec3f9325eef634c0a223296dce5701e06d47a21e090df595748a2d12` | 1 / 2 | 285 / 313 | 0.79 | 0.65 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/docx_project_brief_sample` | 1 / 1 | 30 / 26 | 0.79 | 0.60 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/0007f150074e08d9d0d9a327751ae5808585f3f7c460104334928fb8cafe633d` | 2 / 2 | 452 / 403 | 0.79 | 0.42 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/0036b7d7eb56092d8541c16d929f9f6d7b7e17270b3a1e8551019c341f528b7e` | 1 / 2 | 344 / 442 | 0.80 | 0.67 | 0% / 0% | 9 / 8 |  |
| `08_Eigene_DOCX_Tests/02_formatierungen` | 1 / 1 | 8 / 7 | 0.80 | 0.79 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/0009e9db54323f44d57d185826448b6e7c8a58abd36901433179f977e6a513fc` | 2 / 3 | 538 / 482 | 0.80 | 0.39 | 0% / 8% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/0067822a6cc3dbf94d77fc4b7ae6c622eeacadb4a8d64a353cded3e47b9c62d8` | 10 / 7 | 1057 / 1013 | 0.80 | 0.12 | 0% / 0% | 2 / 0 |  |
| `12_DOCX_Webkorpus/forms/0010349d94f2ac43ee9bee89bc6d06dcc640cbbe6ddf9e6eeafe73ab6ebddd58` | 2 / 2 | 445 / 408 | 0.80 | 0.46 | 0% / 1% | 6 / 3 |  |
| `12_DOCX_Webkorpus/0018715b4769984f2f25e79f523331589996dcacbda2717b103b4ba4442acea4` | 7 / 7 | 3203 / 3260 | 0.81 | 0.60 | 0% / 1% | 0 / 0 |  |
| `12_DOCX_Webkorpus/forms/00447890dc66a9d8514b35b90bf4266443c00a9350b3ee7cd5d5d8a0184b71a0` | 2 / 1 | 122 / 113 | 0.81 | 0.31 | 0% / 0% | 8 / 2 |  |
| `08_Eigene_DOCX_Tests/03_ueberschriften` | 1 / 1 | 30 / 29 | 0.81 | 0.88 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/00253cd4954ac798f035c61b0fae17b4d78c8befc3126d9e241fc6396ba88f7d` | 5 / 7 | 1304 / 1877 | 0.82 | 0.46 | 2% / 0% | 14 / 0 |  |
| `Microsoft test dateien/docx_policy_manual_sample` | 1 / 1 | 32 / 29 | 0.82 | 0.67 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/forms/00396deef5c4871e1e415ecb5a21496040f309d9734537fcb4c43021967326e9` | 6 / 6 | 1012 / 903 | 0.83 | 0.30 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/00602e8ae1f80409e39c548c44c065715e3f43731026aa0eeff77ba0ab267b10` | 7 / 10 | 759 / 776 | 0.83 | 0.31 | 8% / 6% | 7 / 10 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/006d241fd90e05861f80be5df3d6f7904a0ba4301680e082eb1e52b65d90f4e0` | 1 / 2 | 256 / 310 | 0.83 | 0.73 | 1% / 0% | 6 / 4 |  |
| `12_DOCX_Webkorpus/anschreiben/01336ad60af01c0279603c86f0ee90b4fadc99b5445ad60b26c0ef8a0aa805b3` | 2 / 2 | 321 / 428 | 0.84 | 0.49 | 0% / 1% | 3 / 7 |  |
| `12_DOCX_Webkorpus/0000ed4ea10dd138d1d7f0e842be129ee47f35432ffdbba0dd8b7728cde34fb4` | 1 / 1 | 307 / 276 | 0.84 | 0.58 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/0007f6beb064ad06128062700ccf793e8b4db1c37a4672ec32c09271e482a1ba` | 4 / 3 | 1634 / 1471 | 0.84 | 0.73 | 4% / 5% | 1 / 1 |  |
| `12_DOCX_Webkorpus/policies/006e28fde47af3471f8fbcfd56ba2fc59bbcfbacf093f4ad97330a578a9355b6` | 2 / 3 | 465 / 459 | 0.85 | 0.54 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00d50a5888b90f35f11a1cf95e22c7eeb978cd4a348e2aedfa33238511845a43` | 9 / 6 | 1317 / 1401 | 0.85 | 0.27 | 0% / 0% | 3 / 6 |  |
| `12_DOCX_Webkorpus/forms/003709df7bdd1f31e6330a743edb5ca49b5f9286b953da3bc80bc1e9d2adfb3e` | 3 / 3 | 572 / 553 | 0.85 | 0.44 | 0% / 0% | 38 / 0 |  |
| `12_DOCX_Webkorpus/00156ad9f77d017d75739de490c81bb5a43e46407932c8f0a42c565de3b7c1be` | 6 / 8 | 815 / 806 | 0.85 | 0.38 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/0032d96309ac70292de1369c7f8f7d30989e836bac6848a8bad4191cea8d90ff` | 8 / 5 | 1342 / 1229 | 0.86 | 0.35 | 0% / 0% | 2 / 0 |  |
| `12_DOCX_Webkorpus/forms/0048e8c0a15dff646abd96fc5a728789560a65f754c09f1d56c135fc7fa3df63` | 3 / 3 | 287 / 264 | 0.86 | 0.46 | 0% / 0% | 2 / 3 | Formen und gezeichnete Objekte werden nicht dargestellt.; Bilder mit „Oben und unten“-Umbruch werden als Bild im Text eingefügt. |
| `12_DOCX_Webkorpus/00196a2279416de08f9302fddc77d323320dfe821664776a1db42fd6ad3192b7` | 39 / 41 | 15983 / 15658 | 0.86 | 0.63 | 4% / 0% | 2 / 4 |  |
| `12_DOCX_Webkorpus/anschreiben/00a924a0b5bdcf885d3b9d49ba004dd002554ee615fc90cf78f430d43f9b9b01` | 4 / 3 | 612 / 607 | 0.86 | 0.26 | 0% / 1% | 13 / 10 |  |
| `12_DOCX_Webkorpus/forms/002a40f67f2cf0d0adf6467452da83a462e65110f3cb5986bdbbf519a228df89` | 1 / 1 | 146 / 135 | 0.86 | 0.46 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00bf267a1199af6f283ca4883bf9435bbf18b3f44364f4b6175967f308297efe` | 1 / 2 | 227 / 223 | 0.86 | 0.47 | 0% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/forms/002fbe2c6e5f24b5401d7d8ae0c3fb119b83dc3c839361925936d0740789e0cb` | 9 / 10 | 2210 / 2511 | 0.87 | 0.44 | 2% / 2% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/0012597124a4536b9364e7c4a5c439bd9ad82b08bd796e80b9898cd4ea7c724f` | 18 / 16 | 2490 / 2826 | 0.87 | 0.27 | 0% / 0% | 16 / 2 |  |
| `12_DOCX_Webkorpus/anschreiben/01975e5ed96deb65abac1140c5a5f9829a18a4d9ce4d3825746efeef7117c633` | 1 / 1 | 161 / 207 | 0.88 | 0.73 | 0% / 0% | 16 / 22 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/002560bc8a36ddef6298ccf4e5611ed19c9b219e65ac8f085e728278d151fd31` | 2 / 2 | 151 / 169 | 0.88 | 0.53 | 1% / 1% | 4 / 5 |  |
| `12_DOCX_Webkorpus/legal/000d8888039c28666897f4beba4df519fc5a10337e1d89e92e5ea87ebedec6f5` | 7 / 8 | 3375 / 3159 | 0.88 | 0.52 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/0019c86667ee88aa6dc08fb0cc46041b53de1a3da34e647156783fe4b8868b31` | 5 / 5 | 2177 / 2016 | 0.88 | 0.39 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/0035899b9a462cbcda680052fa0874b1c3ea30bf1a0d1ff6928fc45d6f7d0578` | 2 / 2 | 197 / 194 | 0.88 | 0.55 | 0% / 0% | 3 / 2 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00b16922b2558b796577599cf497eace0f4ca21829d994cbf7e83a5886f8de1c` | 7 / 6 | 635 / 729 | 0.88 | 0.26 | 6% / 0% | 5 / 8 |  |
| `12_DOCX_Webkorpus/anschreiben/01a912c08f936c3222730e15f066d25b31a6ca9bb34d9c5257e4df63c319eb3b` | 4 / 4 | 1172 / 1152 | 0.88 | 0.45 | 3% / 5% | 6 / 15 |  |
| `12_DOCX_Webkorpus/policies/000bd832c82cb7afe9a218999fb2ac37938b44ee27a85719f00c3ca373b6c2b2` | 5 / 5 | 1545 / 1447 | 0.88 | 0.49 | 9% / 8% | 10 / 5 |  |
| `Microsoft test dateien/docx_table_report_sample` | 1 / 1 | 22 / 21 | 0.88 | 0.53 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00b653dae82a6787879fb44f245bf89e5c6e1bc4a90f988267f608ff231ccbf3` | 6 / 6 | 755 / 758 | 0.89 | 0.36 | 1% / 1% | 10 / 1 |  |
| `12_DOCX_Webkorpus/001f1397bdc274dc1a9b59a7a138590ce833bda200ee3f95a31f09bec5a23e26` | 11 / 9 | 1574 / 1574 | 0.89 | 0.57 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `12_DOCX_Webkorpus/correspondence/0051d17fadaf76076f398866723b163c9576065ccb663b298e213260ed5f974b` | 1 / 1 | 381 / 357 | 0.89 | 0.74 | 0% / 1% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/003e3c66a0ab5d8e4609fa4897aac2701d68c74413b9aabd1834585d71e00e1b` | 2 / 2 | 533 / 500 | 0.89 | 0.58 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/0071cf0910cc71fed86712d86afe96a45cf5c937af9aa006eb32b0177c194497` | 5 / 3 | 454 / 413 | 0.89 | 0.29 | 0% / 1% | 20 / 6 |  |
| `12_DOCX_Webkorpus/anschreiben/01e90eb716e74804a2ab5264c1048ce41d790b7bea9778a827b584b28605e3dd` | 3 / 3 | 1081 / 1016 | 0.89 | 0.84 | 1% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/001aad1997d18fb42bb4035096089b963b262ff023eebe236e5473aec6e2483a` | 2 / 1 | 463 / 435 | 0.89 | 0.67 | 0% / 0% | 1 / 1 |  |
| `Microsoft test dateien/files-sample-sample` | 1 / 1 | 63 / 60 | 0.89 | 0.57 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `07_Originalsammlungen/FehlerCorpus/araduru-file-format-test-corpus-main/samples/docx/healthy-basic` | 1 / 1 | 15 / 14 | 0.90 | 0.06 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/0018b88f96eb3b8a8d36c36ea386f3686acc7eed50663e92ab03585c7951b3ec` | 3 / 3 | 2811 / 2649 | 0.90 | 0.09 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/005f61d1adaddfc96c3755c30b27ac8dc38c9b738aa2ff3edcf3c9c227a62797` | 3 / 2 | 458 / 530 | 0.90 | 0.29 | 0% / 0% | 2 / 4 | Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung) und wird nicht angezeigt. |
| `12_DOCX_Webkorpus/anschreiben/02213be58bc266316a6cd2f3963a586ce03dca2b5e65dd718c9c8433476f128f` | 3 / 3 | 388 / 368 | 0.91 | 0.53 | 2% / 2% | 1 / 4 | Bilder mit „Oben und unten“-Umbruch werden als Bild im Text eingefügt. |
| `12_DOCX_Webkorpus/legal/0014c86fcae16e21511ffb5badd4d8bf95c7721f94eb2d7f55120c629de734d4` | 36 / 33 | 7008 / 7278 | 0.91 | 0.29 | 0% / 0% | 2 / 1 |  |
| `12_DOCX_Webkorpus/policies/000308bc296a60140a37a107d574f26eace5b9cacf1ab7a93c1f162966f203c6` | 1 / 1 | 536 / 513 | 0.91 | 0.81 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/001f2a51facf718958540647554f58ad0e2539c077e9e10de75c123f9f3f1bd3` | 3 / 2 | 707 / 689 | 0.91 | 0.43 | 2% / 3% | 6 / 11 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00467262742bd3b5eac2de95ac748cb1d50990fc479bac8b44a68c550fd8b98f` | 4 / 3 | 380 / 452 | 0.91 | 0.46 | 1% / 1% | 35 / 1 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00d0fa6cec7b0c0ff98681b821e1a5dbba57801c48e6739958c580752e6f0fed` | 21 / 23 | 1580 / 1617 | 0.91 | 0.38 | 16% / 4% | 3 / 4 | Formeln werden nicht dargestellt und gehen beim Speichern verloren. |
| `12_DOCX_Webkorpus/policies/001cf65cd72d881c991056e26e112e49754ecb1a90f7f3781d5101299f00b037` | 9 / 10 | 1626 / 1561 | 0.92 | 0.22 | 0% / 0% | 11 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/000407cd6c79442ca73c72003321fd71054f8782c4fe240053c9ac064efdb5b6` | 1 / 1 | 284 / 273 | 0.92 | 0.35 | 0% / 0% | 6 / 8 |  |
| `12_DOCX_Webkorpus/forms/0013892c946c551d309fcec9bb3f3500fc08bc77121a3849144b544308ec25c5` | 1 / 1 | 26 / 26 | 0.92 | 0.21 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/files-sample-report` | 1 / 1 | 77 / 73 | 0.93 | 0.73 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/sample-docx-1-page` | 1 / 1 | 120 / 120 | 0.93 | 0.53 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/003013d4d6060d20e32216e5dbbe8ead29710cff6800733df4b23ecf4de70666` | 2 / 2 | 477 / 491 | 0.93 | 0.57 | 2% / 3% | 6 / 11 |  |
| `12_DOCX_Webkorpus/anschreiben/00af3bb0e8885235a1af8d3b67776e6640e6578e458b385540f348b017f2c03b` | 3 / 3 | 1125 / 1132 | 0.93 | 0.58 | 6% / 5% | 6 / 13 |  |
| `12_DOCX_Webkorpus/legal/0016ee20f9ddebf851f1986131fa5e422ea432204d70265ec94e65cc9d105127` | 2 / 2 | 298 / 306 | 0.93 | 0.70 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/001a2c7f07cd358f0b0f06b920de26fb9910d1c947c48026650f48f34dd6940d` | 33 / 28 | 8355 / 8677 | 0.94 | 0.36 | 0% / 0% | 5 / 11 |  |
| `12_DOCX_Webkorpus/correspondence/002a0f18fe6323d4b9a4dda83d9c79cca07a07fe44623623d69993e23f9db585` | 2 / 1 | 445 / 431 | 0.94 | 0.64 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/000e8acdf23713c4299ad3b0f91e35e3c3bbb1daf39e3496d2307f07f163eddd` | 16 / 17 | 4325 / 4346 | 0.94 | 0.54 | 3% / 0% | 12 / 34 |  |
| `12_DOCX_Webkorpus/0001cd2ab6b5825604f6254d624772905c23519e1e73743344aa275ba0e994c3` | 2 / 2 | 952 / 1043 | 0.94 | 0.74 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/forms/0020466f6594cf2d4df29fa2da49d82859bdb2f1651040ff5a2144396f03040f` | 8 / 11 | 1310 / 1331 | 0.94 | 0.45 | 0% / 0% | 2 / 2 |  |
| `Microsoft test dateien/sample-docx-3-pages` | 3 / 3 | 340 / 340 | 0.94 | 0.64 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/0086a3f65dbc22642e1094f1fc6d781301df6e482eb6e794c8e3fab108b656c8` | 2 / 2 | 655 / 636 | 0.94 | 0.76 | 1% / 1% | 5 / 1 |  |
| `12_DOCX_Webkorpus/policies/0021ede195b19bdb8b059ccf9dd1a6b906859fac300f7aa0b1ca454d78a12cb1` | 21 / 16 | 4880 / 4819 | 0.94 | 0.37 | 0% / 1% | 41 / 31 |  |
| `Microsoft test dateien/files-sample-simple` | 1 / 1 | 35 / 35 | 0.94 | 0.74 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/sample-docx-5-pages` | 5 / 5 | 560 / 560 | 0.94 | 0.67 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-docx-10-pages` | 10 / 10 | 1110 / 1110 | 0.94 | 0.67 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-docx-25-pages` | 25 / 25 | 2760 / 2760 | 0.94 | 0.67 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00a69d5b8975af865d3bb770b836f0d0b7807d920b7de0e5516923cae07468c2` | 3 / 3 | 316 / 318 | 0.95 | 0.43 | 0% / 0% | 0 / 2 |  |
| `12_DOCX_Webkorpus/legal/000e5adc27f600448cd90b79438f356354181a93f53d99ca7869e6b5e201d398` | 4 / 4 | 1404 / 1397 | 0.95 | 0.66 | 0% / 0% | 46 / 2 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00752d80eef98123717ad5fc5bbd4ac9528cc382b2b251c0655253f86600290d` | 3 / 2 | 285 / 280 | 0.95 | 0.25 | 0% / 0% | 2 / 2 |  |
| `12_DOCX_Webkorpus/policies/0012f878bad54db7681d0d2b98d8f3f6616401733b4da058c614d7c58a2f2244` | 2 / 3 | 419 / 462 | 0.95 | 0.54 | 2% / 2% | 3 / 1 |  |
| `12_DOCX_Webkorpus/policies/000f71155d45a89d0b760af564b83c2962e762bc0eb909a8b9983e94370ad454` | 40 / 40 | 9780 / 9719 | 0.95 | 0.43 | 2% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/000d173dd26063de66c82158ef1349ad86b528f05742aad87401db5e7723a596` | 4 / 4 | 658 / 669 | 0.95 | 0.40 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/003ccc9549f788e56136eff7b7b6c9ec7c0ce5e58efc1003ec9034c392eee2d5` | 101 / 122 | 28048 / 29152 | 0.95 | 0.12 | 0% / 0% | 118 / 4 |  |
| `08_Eigene_DOCX_Tests/16_schriftgroessen` | 1 / 1 | 35 / 34 | 0.96 | 0.25 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/correspondence/0048b56de6404afd5642086daf34d951576f36622a505ae23385ffad33b542b9` | 1 / 1 | 536 / 526 | 0.96 | 0.78 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/0020157f48ee08b2408e280c8d7bbee6846225477cd27ce1c549ea19a069c09f` | 7 / 4 | 489 / 457 | 0.96 | 0.15 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-docx-field-report-6-pages` | 6 / 6 | 466 / 466 | 0.96 | 0.74 | 2% / 2% | 3 / 3 |  |
| `12_DOCX_Webkorpus/anschreiben/00fc47aa37e11e7e9c07cbf4b5f7d74bc8e1906731221e8ec35f255ed3d360db` | 13 / 14 | 7623 / 7666 | 0.96 | 0.67 | 0% / 0% | 6 / 35 |  |
| `12_DOCX_Webkorpus/forms/003ac2426e110b3cb3dfc45ea1cdff84d4ad440f8469f14fdc2240e42a41db7c` | 2 / 2 | 363 / 365 | 0.96 | 0.50 | 1% / 0% | 2 / 2 |  |
| `Microsoft test dateien/files-sample-large` | 4 / 3 | 800 / 780 | 0.96 | 0.66 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/sample-docx-product-catalogue-4-pages` | 4 / 4 | 331 / 331 | 0.96 | 0.75 | 1% / 1% | 2 / 2 |  |
| `12_DOCX_Webkorpus/forms/001000d54391f84076d88b0d24bafe7504c1b5bfc88074740ff203a0c6130230` | 2 / 1 | 273 / 272 | 0.96 | 0.78 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/009b393dc49ed14cf54f4849e9897c4c95b4d4a9a77568492d34b7d7d2b35f4e` | 2 / 2 | 276 / 275 | 0.97 | 0.61 | 0% / 0% | 3 / 2 |  |
| `12_DOCX_Webkorpus/forms/003a6fc626c845424778354e87b282f6c38bdf60b8e87f9205fbba9cb972b94b` | 3 / 4 | 951 / 965 | 0.97 | 0.45 | 0% / 0% | 0 / 2 |  |
| `12_DOCX_Webkorpus/correspondence/001783eacd9e09ecab448920c6d55179357639d35eec123090d78c9801878bf3` | 1 / 1 | 364 / 364 | 0.97 | 0.85 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/00081e80fae2e9bee867da6cdeefab8644d3f7c75a6133d8d8203c783151073d` | 12 / 15 | 5295 / 5451 | 0.97 | 0.57 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/0022399405d6999a32027aa50e57e4936a14afb6fa664a4ab9394b2ca35e4e8d` | 8 / 9 | 1644 / 1624 | 0.97 | 0.56 | 0% / 0% | 2 / 2 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `07_Originalsammlungen/Microsoft-Office-Samples/Samples/word-import-template/resources/template example` | 1 / 1 | 160 / 159 | 0.97 | 0.17 | 0% / 10% | 0 / 0 |  |
| `11_Microsoft_Originale/template example` | 1 / 1 | 160 / 159 | 0.97 | 0.17 | 0% / 10% | 0 / 0 |  |
| `12_DOCX_Webkorpus/forms/0011786c351ec1dc2d948e3f973cd7578292b6dc88a601f6f8d731de408baef3` | 4 / 4 | 406 / 405 | 0.97 | 0.37 | 0% / 0% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-project-brief-2-pages` | 2 / 2 | 176 / 176 | 0.97 | 0.76 | 0% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/policies/00355ceb3add8e953576569930ed1e1239583d46c09ce5f142244ba0f48f8fca` | 7 / 8 | 1864 / 1869 | 0.97 | 0.33 | 1% / 17% | 6 / 5 |  |
| `12_DOCX_Webkorpus/policies/005871aa5fd4957a89ecccceadcb75cae7ab87cc2e51688f44a9a4631f571368` | 2 / 2 | 500 / 481 | 0.98 | 0.49 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/000dfc8e6955f95b14248f877f8243c6ae95dabe7afbab99d3a3c707e7795378` | 2 / 2 | 410 / 410 | 0.98 | 0.39 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/00109319b9b68554be095d5b34195174e301274d91b01b830d80cd8401e416a5` | 7 / 6 | 2054 / 2138 | 0.98 | 0.53 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/12_langer_text` | 34 / 37 | 19431 / 19002 | 0.98 | 0.84 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/001a702d4b921dc50b96911bb2e4f4043cf5fc4c679261a905982885ed8ad37e` | 3 / 4 | 241 / 241 | 0.98 | 0.37 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/0040da3f99043e09929e269636afd4677527c7e39ac84538b580b0da00449dfe` | 2 / 2 | 709 / 697 | 0.98 | 0.60 | 1% / 1% | 4 / 5 |  |
| `12_DOCX_Webkorpus/anschreiben/021d56ae46dea66b28b5da3f9060fd6acbd643e2089ea94a54c358d7bd5e78fd` | 7 / 6 | 1521 / 1460 | 0.98 | 0.70 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/000ad039fbd3f8b6bcad0e061d3c9676b34eafb4398904a8f19519c1244cef9f` | 104 / 85 | 21432 / 21074 | 0.98 | 0.38 | 0% / 0% | 0 / 1 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `12_DOCX_Webkorpus/0005ba6467c9b78760bab1480e7dcb5d46512413dff2b87d4f8bd41c140842fa` | 6 / 3 | 80 / 77 | 0.98 | 0.49 | 0% / 0% | 3 / 4 |  |
| `12_DOCX_Webkorpus/correspondence/005243975f00b605cfa2fddc9f24b39f75358346337ee99ae62200f3bafdb7bf` | 8 / 7 | 1814 / 1800 | 0.98 | 0.60 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-simple` | 2 / 2 | 162 / 160 | 0.98 | 0.71 | 6% / 9% | 1 / 1 |  |
| `12_DOCX_Webkorpus/forms/00042714bec87fe8097f604fdd230760c956aac77fa56fcd5bc5ffb68c60690a` | 9 / 7 | 1536 / 1534 | 0.98 | 0.23 | 0% / 0% | 7 / 7 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `12_DOCX_Webkorpus/forms/003fcb9100036916464f7a2ec94e230ec20aab989558032dfc46b795c1c1e6b5` | 1 / 1 | 192 / 195 | 0.98 | 0.51 | 0% / 0% | 1 / 2 |  |
| `12_DOCX_Webkorpus/legal/000e65135b02613bbd312317ecb00add418bb479f9c41b8ab52e7dfc4c579bce` | 1 / 2 | 374 / 386 | 0.98 | 0.32 | 0% / 0% | 2 / 7 |  |
| `12_DOCX_Webkorpus/correspondence/003ca1382771428d62ac7b65be135b7f7b04b88d3c7dca672e90233303894c22` | 2 / 2 | 632 / 634 | 0.99 | 0.65 | 6% / 6% | 2 / 5 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00913075e6b90314bd30bb2191151b651d1b8b36df2fd7736dc4d4f2ae6fad53` | 11 / 11 | 1417 / 1406 | 0.99 | 0.66 | 0% / 0% | 0 / 2 |  |
| `08_Eigene_DOCX_Tests/18_viele_seiten` | 6 / 6 | 3312 / 3242 | 0.99 | 0.56 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/0011b1980f1150c308afdbbc5a11fee8e3e4927f6ea71a8d167f85ab0841a3f2` | 28 / 25 | 5624 / 5594 | 0.99 | 0.69 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/20_wiederholter_text` | 13 / 16 | 9282 / 9102 | 0.99 | 0.78 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/15-MB-docx-file-download` | 14 / 15 | 4139 / 4107 | 0.99 | 0.89 | 0% / 0% | 6 / 8 |  |
| `Microsoft test dateien/sample-docx-100kb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 8% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-10mb` | 2 / 2 | 198 / 198 | 0.99 | 0.74 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-15mb` | 2 / 2 | 198 / 198 | 0.99 | 0.75 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-1mb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-200kb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 8% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-20mb` | 2 / 2 | 198 / 198 | 0.99 | 0.75 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-25mb` | 2 / 2 | 198 / 198 | 0.99 | 0.75 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-2mb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-30mb` | 2 / 2 | 198 / 198 | 0.99 | 0.75 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-3mb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-500kb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-50kb` | 2 / 2 | 198 / 198 | 0.99 | 0.72 | 4% / 8% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-50mb` | 2 / 2 | 198 / 198 | 0.99 | 0.75 | 5% / 9% | 1 / 1 |  |
| `Microsoft test dateien/sample-docx-5mb` | 2 / 2 | 198 / 198 | 0.99 | 0.73 | 5% / 9% | 1 / 1 |  |
| `01_DOCX/sample-document-small` | 2 / 2 | 479 / 476 | 0.99 | 0.41 | 0% / 0% | 0 / 0 |  |
| `07_Originalsammlungen/Freetools/documents/docx/sample-document-small` | 2 / 2 | 479 / 476 | 0.99 | 0.41 | 0% / 0% | 0 / 0 |  |
| `DOCX/sample-document-small` | 2 / 2 | 479 / 476 | 0.99 | 0.41 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-docx-file-for-testing` | 11 / 10 | 4153 / 4082 | 0.99 | 0.88 | 0% / 0% | 4 / 4 |  |
| `12_DOCX_Webkorpus/correspondence/00054c43c27f30d64f42287de8015febd9ca5ece3f2a380b66acff512bae2c31` | 7 / 6 | 2014 / 2042 | 0.99 | 0.49 | 0% / 1% | 7 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/00595cd73be1bcd03f011120d0599789f955888f17e91576d9234790adc32ec9` | 4 / 3 | 1282 / 1271 | 1.00 | 0.59 | 0% / 0% | 0 / 2 |  |
| `12_DOCX_Webkorpus/policies/00692cca347f18c13d47c4f50bfa76d1e19b6b2dfb1ee0da64d2a9200e6395f9` | 12 / 10 | 3358 / 3358 | 1.00 | 0.35 | 15% / 1% | 2 / 0 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `12_DOCX_Webkorpus/correspondence/001a2795f0f96f0f1aa543731e3f57757ac819722149f31d4e5e75bcfaea580e` | 2 / 2 | 471 / 472 | 1.00 | 0.43 | 0% / 1% | 1 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/00481561b28985286a2fe0a6d6bb35c9ff6ff2ea2c1ca0311ef1f478b68e8da2` | 3 / 3 | 475 / 478 | 1.00 | 0.35 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/0013aa1d9e54286d62e38782dcc9093cbae747e0615a84c9cf537173508eff1f` | 7 / 7 | 2613 / 2612 | 1.00 | 0.59 | 4% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/10_seitenumbrueche` | 5 / 5 | 291 / 291 | 1.00 | 0.55 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/15_viele_absaetze` | 11 / 20 | 3002 / 3002 | 1.00 | 0.52 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/19_mischdokument` | 1 / 1 | 13 / 13 | 1.00 | 0.33 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/001d0cb28ba01990ad6cc8586fa11bf68eedfcccf1452b30e35a25b43fd25a0a` | 1 / 1 | 460 / 460 | 1.00 | 0.30 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/0097e1d2f6c5f8cb5cf655e1bf1d90318ada60b3103af45524d66c9d5af16a21` | 1 / 1 | 145 / 145 | 1.00 | 0.38 | 10% / 11% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00bc6bbe966f5d2f95e8f2917f981c5cc5aaeb2dc0abd13b2e128a2faac23d9e` | 1 / 1 | 10 / 10 | 1.00 | 0.52 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/correspondence/000ba7e6d860cea0a4e26dbf0760d6b1f0637a29b06e65647558bbb4c159167f` | 1 / 1 | 366 / 366 | 1.00 | 0.48 | 0% / 0% | 0 / 2 |  |
| `12_DOCX_Webkorpus/correspondence/000f9471dada0bc4c09f6383aff45431c93b1a256949ebfedb051fd1911da9de` | 3 / 4 | 737 / 737 | 1.00 | 0.49 | 3% / 2% | 18 / 21 | Formen und gezeichnete Objekte werden nicht dargestellt. |
| `12_DOCX_Webkorpus/correspondence/0053e8c9c47afce57c072e2316040c34a5920e5138a8e4abfef75ee04ea9299b` | 2 / 2 | 358 / 358 | 1.00 | 0.29 | 0% / 0% | 3 / 4 |  |
| `12_DOCX_Webkorpus/forms/001a883b0b4eb90e8ccf2095fb005a5f1a2bc2f5c8d8cdfb2555654466e63b8c` | 1 / 1 | 154 / 154 | 1.00 | 0.37 | 0% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/forms/0046035b323728a8df16f81194a3adc7a5decad6c34576fa5f015ebbdbc73c39` | 1 / 1 | 56 / 56 | 1.00 | 0.53 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/001776ac598833c5360356e3b065dc6a2fe8ee450bbd12ad49b83156641d701c` | 2 / 1 | 277 / 277 | 1.00 | 0.79 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/001b7d3133ca0c69561b36fab4a07c07e828bc24e2ac82036fe20a4f63b1fc91` | 3 / 3 | 789 / 789 | 1.00 | 0.50 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/002f4d99264aca856464e63fc7c2cb353b9ba6ebe27e12102c6c43873a4c680c` | 2 / 4 | 739 / 739 | 1.00 | 0.28 | 0% / 0% | 1 / 1 |  |
| `Microsoft test dateien/files-sample-styled` | 1 / 1 | 55 / 55 | 1.00 | 0.55 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/sample-long` | 18 / 19 | 5031 / 5031 | 1.00 | 0.52 | 25% / 22% | 18 / 18 |  |

## Stimmt (35)

| Datei | Seiten Lunivo / Vorbild | Wörter Lunivo / Vorbild | Wortfolge | Seitenbild | Farbfläche Lunivo / Vorbild | Bilder Lunivo / Vorbild | Fehler oder Hinweis |
|---|---|---|---|---|---|---|---|
| `DOCX/sample-document-xl` | 60 / 60 | 10749 / 10717 | 0.98 | 0.67 | 7% / 7% | 30 / 30 |  |
| `DOCX/sample-document-large` | 20 / 20 | 3669 / 3657 | 0.98 | 0.67 | 7% / 7% | 10 / 10 |  |
| `DOCX/sample-document-medium` | 6 / 6 | 1191 / 1186 | 0.98 | 0.67 | 7% / 7% | 3 / 3 |  |
| `Microsoft test dateien/sample-resume` | 1 / 1 | 119 / 118 | 0.99 | 0.64 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/correspondence/001f8f709a06805dca7f06ed9fe9117eb684010576d8feb1097876d51dbd8d89` | 3 / 3 | 976 / 964 | 0.99 | 0.69 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/01cd0a96f79a31f775a24ae1ce864cd449562190e7614f6691d20de469803ce2` | 1 / 1 | 239 / 238 | 0.99 | 0.79 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/00268604474a77e62a963db965facbc2fe5910d9ef8bf56fd1c146c9c787e550` | 1 / 1 | 455 / 455 | 1.00 | 0.68 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/01_einfacher_text` | 1 / 1 | 20 / 20 | 1.00 | 0.78 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/04_listen` | 1 / 1 | 61 / 61 | 1.00 | 0.75 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/05_tabelle` | 1 / 1 | 82 / 82 | 1.00 | 0.72 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/06_verbundene_zellen` | 1 / 1 | 8 / 8 | 1.00 | 0.67 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/07_grosse_tabelle` | 3 / 3 | 1618 / 1618 | 1.00 | 0.67 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/08_bilder` | 1 / 1 | 5 / 5 | 1.00 | 0.96 | 0% / 0% | 1 / 1 |  |
| `08_Eigene_DOCX_Tests/09_kopf_fusszeile` | 1 / 1 | 9 / 9 | 1.00 | 0.93 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/11_querformat` | 1 / 1 | 6 / 6 | 1.00 | 0.98 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/13_unicode` | 1 / 1 | 21 / 21 | 1.00 | 0.73 | 0% / 0% | 8 / 0 |  |
| `08_Eigene_DOCX_Tests/14_leeres_dokument` | 1 / 1 | 2 / 2 | 1.00 | 0.99 | 0% / 0% | 0 / 0 |  |
| `08_Eigene_DOCX_Tests/17_textausrichtung` | 1 / 1 | 5 / 5 | 1.00 | 0.84 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/00228ad867b921d11a33150ede65b3e6531325f11cc84783c57f39c9b1051c0a` | 1 / 1 | 293 / 293 | 1.00 | 0.89 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/anschreiben/01b670372a1e6c8f308023f4189b7b7cdfb9fea512c07f50720dedf812a0d316` | 2 / 2 | 983 / 983 | 1.00 | 0.86 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/bewerbungsformulare/00cce4a84af4761e2848fd34e1e6165eac94943d673d6e7c914af6f255cc3d80` | 1 / 1 | 122 / 122 | 1.00 | 0.90 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/correspondence/000191ed2e82543361847868fcbde0c31954b3f2457da9238ebfe2509cb7788a` | 1 / 1 | 259 / 259 | 1.00 | 0.74 | 0% / 0% | 2 / 2 |  |
| `12_DOCX_Webkorpus/correspondence/000d7568dda834f960ecc722bc359db1db0fe494874d2d3c834f2f62842a4894` | 1 / 1 | 488 / 488 | 1.00 | 0.71 | 0% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/003f03e90cc5fd1bf10e309c07bd78e05ffbfd748b71aa34b7fdd35856a353a1` | 1 / 1 | 215 / 215 | 1.00 | 0.94 | 7% / 7% | 1 / 1 |  |
| `12_DOCX_Webkorpus/correspondence/0062e0b06a70a83fed2cd0d3436c838dfb22055430af80de9334b8f0274b7f04` | 1 / 1 | 218 / 218 | 1.00 | 0.83 | 4% / 5% | 2 / 2 |  |
| `12_DOCX_Webkorpus/forms/000e366a02330e96ce5e878a2c2ecceba7374715a1065a5ece914d024a25d951` | 1 / 1 | 107 / 107 | 1.00 | 0.76 | 0% / 0% | 1 / 1 |  |
| `12_DOCX_Webkorpus/legal/000949a04e086caa49e35395dbfbf48dec55bde8d08a58ce4ae2c3d83007965d` | 2 / 2 | 490 / 490 | 1.00 | 0.92 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/legal/001bbf7a4fad2c6808d1d3daa87aabcb58340829dbb72a0ede732f10fa535f0f` | 1 / 1 | 82 / 82 | 1.00 | 0.87 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/002fafda7818285890e12c508592b72a476b1145fa9d4238d841584ff806c809` | 2 / 2 | 538 / 538 | 1.00 | 0.77 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/0053a4ffa66436f63a0202a4872c210d70e4460f7fd74041bfd250c443e2e180` | 1 / 1 | 328 / 328 | 1.00 | 0.61 | 0% / 0% | 0 / 0 |  |
| `12_DOCX_Webkorpus/policies/005a2fe96920199cc5c96d47cb8bc475bf7faecb5564023355e43ac2063f9b13` | 1 / 1 | 532 / 532 | 1.00 | 0.60 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/New document` | 1 / 1 | 0 / 0 | 1.00 | 1.00 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/files-sample-tables` | 1 / 1 | 42 / 42 | 1.00 | 0.76 | 0% / 0% | 0 / 0 | Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen. |
| `Microsoft test dateien/sample-blank` | 1 / 1 | 0 / 0 | 1.00 | 1.00 | 0% / 0% | 0 / 0 |  |
| `Microsoft test dateien/sample-document-extra` | 1 / 1 | 0 / 0 | 1.00 | 1.00 | 0% / 0% | 0 / 0 |  |
