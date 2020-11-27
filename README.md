# html 2 SMLY

> Umritar html kóða yfir í SmileyCoin færsluupphæðir

Lokaverkefni í námskeiðinu STÆ532M í Háskóla Íslands. Ég valdi verkefnið að geyma vefsíðu á bálkakeðju og fór ég þá leið að geyma vefsíðuna bókstaflega á bálkakeðjunni.

## Uppsetning

```sh
git clone https://github.com/ivar1309/HTML2SMLY.git
cd HTML2SMLY
python -m venv .
pip install -r requirements.txt
```

## Notkun

> Sem stendur styður forritið eingöngu enska stafrófið þar sem notast er við ASCII staðalinn við umritun.

Til að umrita vefsíðu yfir í SMLY þá þarf að setja þann einkalykil og það veskisfang í skránna .env sem greiða fyrir umritunina:

```sh
touch .env
echo "signingPrivKey=EINKALYKILL" >> .env
echo "sendingAddress=VESKISFANG" >> .env
```

Ef html kóði síðunnar er í index.html þá nægir að keyra:

```sh
python HtmlToSmly.py
```

annars er nafn html skráarinnar gefið sem viðfang á skipanalínu.

_Gæta þarf þess að nægileg upphæð sé á veskisfangi svo að umritunin gangi að fullu_

Ef umritun heppnast þá koma skilaboð í lokin um það veskisfang sem tók við færslunum svo og einkalykill til að geta haldið utanum eignarhald.

###### t.d.

```sh
HTML is encoded into SMLY and sent to this address: b'VESKISFANG'
To spend them and therefore erase the HTML use this private key
Private Key: EINKALYKILL
```

Skráin Server.py inniheldur lítin Flask vefþjón sem les af SMLY bálkakeðjunni og umritar aftur yfir í html og birtir.

sjá dæmi um síðu á [bálkaskoðara][blocks] annars vegar og [Flask þjón][heroku] hins vegar.

## Tæknileg lýsing

Umritunin fer þannig fram að fyrst er búið til veskisfang sem verður vísun í vefsíðuna. Því næst er html kóðinn umritaður, fjögur tákn í senn yfir í upphæð í SMLY, sem sett er í færslu undirritaðri af einkalykli viðkomandi. Færslunni er síðan gefið raðnúmer til að halda röðinni réttri við aflestur síðar. Loks er færslan send út á bálkakeðjuna.

Umritunin úr html yfir í SMLY notast við [ASCII][asciitable] töfluna. Tákn er lesið inn, flett upp í töflunni tugakerfisgildinu og frá því svo dregið talan 31. Ástæðan fyrir því er sú að prentanlegir stafir liggja á bilinu 32-126 en til að geta umritað fjóra stafi í upphæð færslu þá má hver stafur ekki vera hærri en 99. Þannig að frádráttur 31 gefur númer á hvert prentanlegt tákn frá 1-95.

Notast er við forritasöfn sem hjálpa til við stærðfræðilega hlið þess að útbúa einka- og opinbera lykla. Fyrst eru fengnir 256 bitar frá slembitöluúttaki stýrikerfisins sem verður einkalykillinn. Hann er síðan margfaldaður við punkt á sporgera ferlinum [secp256k1][ecurve]. Þá höfum við tvennd, sem eru hnit á ferlinum, sem standa fyrir opinbera lykilinn.

Því næst þarf að beyta tætiföllunum [sha256][sha256] og [ripemd160][ripemd160] á opinbera lykilinn. Þá fæst svokallað "payload". Skeyta þarf framan við það útgáfunúmeri bálkakeðjunar og beyta [sha256][sha256] tvisvar á útkomuna. Þá höfum við það sem kallað er "checksum". Síðast er svo útgáfunúmerinu, "payload" og "checksum" skeytt saman og sent í umritun yfir í [base58check][base58]. Þá loks höfum við veskisfang.

Færslan er svo sett saman eftir kúnstarinnar reglum eins og lýst er í staðlinum. En brotin niður í einingar þá er hrá færsla í bætum svo hljóðandi:

1. 4 bæti - útgáfunúmer gagnasniðs.
2. 1+ bæti - fjöldi inn-færslna.
3. 41+ bæti - listi af inn-færslum.
4. 5 bæti - tímabundið gildi sem skipt er út við undirskrift.
5. 1+ bæti - fjöldi út-færslna.
6. 9+ bæti - listi af út-færslum.
7. 4 bæti - tímalás (0 fyrir ekki í lás).

þar sem inn-færsla er:

1. færslu númer (txid).
2. út-númer (vout).

og út-færsla er:

1. upphæð færslu.
2. lengd pubkey skriftu (pubKeyScript).
3. pubkey skrifta.

###### t.d.

```sh
01000000
01
76e9decac25bb7718a27ec19a3e3857441133c71131b214db26730333160aafa00000000
00ffffffff
0100be04ef020000001976a9146f98a59ccfdee54bbfa91e8effa2e7e4c450292588ac
00000000
```

Næst þarf að undirrita færsluna. Þá er færslan eins og hún er núna tekin og skeytt aftan við hana tegund tætingar (01000000) og svo beytt á hana **sha256** tvisvar sinnum. Því næst er einkalykillinn notaður til að undirrita útkomuna. Þá höfum við undirskrift sem við endan bætist 01. Síðan þarf að útbúa skriftuna sem er samskeyting lengdar á undirskrift, undirskrift, lengdar á opinberum lykli og loks opinberum lykli. Nú höfum við "scriptSig".

Að lokum þarf að útbúa færsluna aftur en skipta þá út 4. liðnum í upphaflegu færlunni með "scriptSig" og svo senda útkomuna út á bálkakeðjuna.

Allar aðgerðir á bálkakeðjuni eru framkvæmdar í gegnum "api" sem hefur slóðina: https://blocks.smileyco.in/api/

- Endinn **/addr/ADDRESS/utxo** til að sækja færslur sem á að eyða í umritunina.
- Og endinn **/tx/send** til að senda færslur á keðjuna.

Sjá [SMLY API][smlyapi] fyrir frekari upplýsingar.

## Höfundur

Ívar Árnason – iva1@hi.is

## Heimildir

1. Bókin _Mastering Bitcoin 2e: Programming the Open Blockchain_ e. Andreas Antonopoulos
2. Vefsíðan [Transaction][specs]
3. Vefsíðan [Bitcoins the hard way: Using the raw Bitcoin protocol][hardway]
4. og Google :)

<!-- Markdown link & img dfn's -->

[blocks]: https://blocks.smileyco.in/address/B7bEk5zaXjQwahCbKZp3hg5JwHYceVcE8e
[heroku]: http://htmlfromsmly.herokuapp.com/addr/B7bEk5zaXjQwahCbKZp3hg5JwHYceVcE8e
[specs]: https://en.bitcoin.it/wiki/Protocol_documentation#tx
[hardway]: http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html
[asciitable]: https://upload.wikimedia.org/wikipedia/commons/d/dd/ASCII-Table.svg
[ecurve]: https://en.wikipedia.org/wiki/Elliptic_curve
[sha256]: https://en.wikipedia.org/wiki/SHA-2
[ripemd160]: https://en.wikipedia.org/wiki/RIPEMD
[base58]: https://en.wikipedia.org/wiki/Binary-to-text_encoding
[smlyapi]: https://github.com/smileycoin/insight-api#api
