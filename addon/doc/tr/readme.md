# NVDA için Sesli Komut

NVDA komutlarını tuşlara basmak yerine konuşarak çalıştır.

NVDA'nın Girdi Hareketleri iletişim kutusunda her komut için bir açıklama vardır. Sesli Komut, mikrofonundan seni dinler, konuşmanı çevrimdışı çalışan bir ses tanıma motoruyla (varsayılan olarak [Vosk](https://alphacephei.com/vosk/); istersen seçeceğin bir [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) modeli, bkz. Ses tanıma modeli) yazıya çevirir, bu yazıyı o açıklamalarla (ve kendi tanımladığın ifadelerle) eşleştirir ve en uygun komutu çalıştırır. Sesin bilgisayarından dışarı çıkmaz.

## Nasıl çalışır

1.  Dinlemeyi başlattığında eklenti o an kullanılabilir komutları toplar. Bu, üzerinde çalıştığın uygulamanın komutlarını da kapsar; başka bir uygulamanın komutu yalnızca o uygulama odaktayken sunulur.
2.  Konuşur, sonra dinlemeyi durdurursun. Ses tanıma motoru konuşmanı yazıya çevirir.
3.  Yazı, komut açıklamalarıyla ve kendi ifadelerinle karşılaştırılır. Vosk'ta tanıyıcıya hangi ifadeleri beklemesi gerektiği de söylenir; bu, serbest dikteye göre çok daha doğru sonuç verir. sherpa modelleri bu şekilde kısıtlanamaz: sıradan metin yazarlar, bu yüzden eklenti onu daha sıkı karşılaştırır (bkz. Ne söyleyeceğini seçmek).
4.  Bir komut açıkça uyuyorsa çalışır. Birkaçı hemen hemen eşit uyuyorsa bir liste açılır ve sen seçersin.

## Gereksinimler

- Windows üzerinde NVDA 2026.1 ya da sonrası, 64 bit.
- Windows'ta varsayılan kayıt aygıtı olarak ayarlanmış bir mikrofon.
- Ses tanıma modelini indirmek için bir kez internet bağlantısı (küçük bir Vosk modeli yaklaşık 40 ile 100 MB'tır; sherpa modelleri 24 ile 124 MB'tır ve hepsinin ortak kullandığı 21 MB'lık bir çalışma zamanı gerekir).

## Kurulum ve ilk çalıştırma

1.  `.nvda-addon` dosyasını aç ve kurulumu onayla. İstenince NVDA'yı yeniden başlat.
2.  NVDA açıldıktan birkaç saniye sonra eklenti kurulu bir ses tanıma modeli olmadığını fark eder ve NVDA dilin için bir model indirmesine izin verip vermediğini sorar. Türkçe NVDA'da bu turkish-stt modelidir; diğer dillerde bir Vosk modelidir. **Evet**'i seç. İndirme arka planda yapılır; NVDA ilerlemeyi söyler ve sesli komutların ne zaman hazır olduğunu bildirir.

**Hayır**'ı seçersen eklenti açılışta bir daha sormaz. Dinlemeyi başlattığında ya da konuşma modeli penceresinde kurulu olmayan bir model seçtiğinde (bkz. Ses tanıma modeli) yeniden sorulursun.

## Hızlı başlangıç

Varsayılan olarak hiçbir tuş atanmamıştır, tuşları kendin seç:

1.  NVDA menüsünü, ardından Tercihler ve Girdi hareketleri'ni aç.
2.  **Sesli Komut** kategorisini genişlet ve **Sesli komut dinlemesini başlatır; dinlemeyi durdurup komutu çalıştırmak için tekrar basın ya da konuştuktan sonra bir an sessiz kalın** komutuna bir tuş ata. İstersen oradaki diğer komutlara da tuş atayabilirsin.

Tuş atamadan Araçlar menüsünü de kullanabilirsin (bkz. Araçlar menüsü).

Sonra sesli komut vermek için:

1.  Tuşa bas. Yüksek bir bip dinlemenin başladığını bildirir.
2.  Komutu söyle.
3.  Aynı tuşa tekrar bas ya da konuştuktan sonra bir an (yaklaşık bir saniye) sessiz kal. Alçak bir bip dinlemenin bittiğini bildirir ve komut çalışır.

Sessizlikte durdurma, Girdi Hareketleri'ndeki "Konuştuktan sonra sessiz kalınca dinlemeyi kendiliğinden durdurmayı açar ya da kapatır" komutuyla (ya da Araçlar menüsünden) kapatılabilir. Sessizliğin ne kadar süreceğini değiştirmek için `settings.json` içindeki `silence_seconds` değerini (0,5 ile 5 arası, varsayılan 1,2) ayarla.

Hiçbir şey anlaşılmazsa NVDA "Anlaşılamadı" der. Duyduğu şey hiçbir komuta yeterince uymuyorsa "Eşleşen komut yok" der ve en yakın komutu söyler ya da bir aday listesi açar (bkz. Emin olamadığında).

## Araçlar menüsü

NVDA menüsünü, ardından Araçlar'ı ve **Sesli Komut**'u açarak eklentiyi tuş atamadan kullanabilirsin:

- **Dinlemeyi başlat veya durdur** tuşla aynı çalışır: başlatmak için bir kez, durdurmak için tekrar seç. Menüyü her seferinde açmak gerektiğinden bir tuş atamak daha hızlıdır.
- **Komut ifadeleri düzenleyicisi...** ifade düzenleyiciyi açar.
- **Son söylenen ifadeyi öğret...** tanıyıcının bilmediği adlar için pencereyi açar.
- **Komutlarım...** kendi komutların için iletişim kutusunu açar.
- **Tanıma sırasında ses zayıflamasını aç/kapa** diğer uygulamaların sesini kısmayı açar ya da kapatır.
- **Sessizlikte otomatik durdurmayı aç/kapa** dinlemenin konuştuktan sonraki sessizlikte kendiliğinden durmasını açar ya da kapatır.
- **Konuşma modeli...** konuşma modelini seçip indirebileceğin ve yönetebileceğin pencereyi açar (bkz. Ses tanıma modeli).
- **Komut yazarak çalıştır...** komut cümlesi yazabileceğin kutuyu açar.

Bunlar Girdi Hareketleri'ndeki komutlarla aynı işi yapar (bkz. Komut başvurusu).

## Ne söyleyeceğini seçmek

NVDA'nın açıklamaları çoğu zaman tam cümledir. Hepsini söylemen gerekmez.

| Ne söylersin                                                                               | Ne beklemelisin                                                                     |
|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Girdi Hareketleri'nde komutun yanında görünen açıklamanın ilk cümlesi                      | Genellikle iyi çalışır. Birçok komutta ilk cümle açıklamanın tamamıdır.             |
| [İfade düzenleyicide](#kendi-ifadelerin) tanımladığın kısa bir ifade, örneğin "satırı oku" | Tam eşleşir ve en güvenilir yoldur. **Her gün kullandığın komutlar için önerilir.** |
| Hiçbir yerde tanımlanmamış, kendi kısa yorumun                                             | Daha az güvenilirdir. Liste açılabilir ya da benzer başka bir komutla eşleşebilir.  |

Pratikte iki şey işe yarar. İfadeyi düzenli bir hızla, sessiz bir anda söyle ve ayırt edici sözcükleri atlama. Ayrıca en çok kullandığın komutlar için kısa ifadeler tanımla: bir dakikanı alır ve her şeyi hızlandırır.

**Bir sherpa modeliyle** (bkz. Ses tanıma modeli) komutu daha doğal söyleyebilirsin; çünkü yazı komutla iki yönde karşılaştırılır: söylediğin sözcükler komutta, komutun sözcükleri de söylediklerinde bulunmalıdır. "Lütfen" gibi fazladan sözcükler hoş görülür. Tam olarak tek bir komuta uyan bir parça da o komutu çalıştırır; örneğin başka hiçbir komutta bu sözcük yoksa, "Yukarı çık" komutu için yalnızca "yukarı" demek yeter. Parça birkaç komuta uyuyorsa liste açılır; dört harften kısa parçalar yok sayılır. Modelin farklı yazdığı bir yazım ya da boşluk (örneğin "Masaüstünü göster" yerine "masa üstünü göster") da, tek bir komut sese göre açıkça en yakınsa çalışır. Hiçbir komuta benzemeyen metin için tahmin yürütülmez; bunun yerine NVDA ne duyduğunu söyler, örneğin "Duyulan: teşekkürler. Eşleşen komut yok".

## Kendi ifadelerin

Komutları kendi cümlenle söylemek için ifade düzenleyiciyi kullan. **Komutlar için kullanılan ifadeleri (takma adları) düzenleme penceresini açar** komutuna bir tuş ata ve komutlarını düzenlemek istediğin uygulamadayken aç.

1.  **Komut ara** alanına birkaç sözcük yazarak listeyi süz, sonra **Komutlar** listesinden komutu seç.
2.  **Yeni ifade** alanına ifadeni yaz ve **İfadeyi ekle**'yi seç. Bir komuta birden çok ifade ekleyebilirsin. Birini değiştirmek ya da kaldırmak için **Bu komut için söyleyeceğin ifadeler** listesinde seç ve **Seçili ifadeyi düzenle** ya da **Seçili ifadeyi sil**'i seç.
3.  Komut yalnızca senin ifadelerine yanıt versin istiyorsan **Özgün açıklamayı da kullan** kutusunu temizle.
4.  **Kaydet**'i seç.

**Komuta birden çok kez basan ifadeler.** Bazı komutlar tuşlarına iki ya da üç kez basılınca başka bir şey yapar: saati bildiren komut ikinci basışta tarihi söyler. Bu ikinci işleme kendi ifadesini vermek için ifadeyi yaz, **Komuta kaç kez basılsın** listesinden bir sayı seç, sonra **İfadeyi ekle**'yi seç. Saati bildiren komut için "tarihi söyle" ifadesi 2 ile eklenirse komut tuşuna iki kez basılmış gibi çalışır; yalnızca tarih söylenir. İfade listesinde böyle bir ifade "tarihi söyle (2 kez basılır)" olarak görünür ve **Seçili ifadeyi düzenle** sayıyı listeye geri koyar. Aynı sözcükleri başka bir sayıyla yeniden eklersen öncekinin yerini alır. Sayı 2 ile 5 arasında olabilir; her komut türüne ne yaptığı için bkz. Komutu tekrarlamak.

Sayı ifadenin sonunda " x2" ile " x5" arası olarak saklanır. Onu **Yeni ifade** alanına ya da içe aktardığın bir dosyaya kendin de yazabilirsin. x harfinin yanı sıra çarpı işareti (×), yıldız, x'e benzeyen Kiril ve Yunan harfleri ya da başka yazı sistemlerinin rakamlarıyla da yazılabilir; bu yüzden her klavyede yazılabilir.

İyi ifadeler kısadır, iki ile dört sözcük arasıdır ve birbirinden farklı duyulur. İfadelerin özgün açıklamalara göre önceliklidir; tekrar özelliğiyle ve aday listesiyle diğer komutlar gibi çalışırlar. Düzenleyici açtığın yerde kullanılabilen komutları gösterir; bir uygulamanın komutlarını düzenlemek için pencereyi o uygulamanın içinde aç.

## Tanıyıcının bilmediği adlar

Ses tanıma modelinin sözlüğü sabittir ve yeni sözcük öğrenemez. Bir sanatçı ya da şarkı adı gibi nadir ya da yabancı bir ad içeren komut bu yüzden çoğu zaman kulağa benzeyen başka sözcükler olarak duyulur. Örneğin "Zülfü Livaneli" "gül suyu divane izi" diye yazılabilir. Eklenti bu tür metni ses benzerliğine göre eşleştirmeyi dener; model adı yakın bir yazımla yazdığında ("Inti Illimani" için "inti ilimani") bu işe yarar, ama tamamen farklı sözcükler yazdığında yaramaz. sherpa modellerinin sabit bir sözcük listesi yoktur, ama onlar da bilmedikleri bir adı beklediğinden farklı yazabilir.

Bir komut tanınmadığında eklentiye tanıyıcının ne duyduğunu öğret:

1.  Tanınmayan komutu söyle.
2.  Araçlar menüsünü, ardından Sesli Komut'u aç ve **Son söylenen ifadeyi öğret...**'i seç. İstersen Girdi hareketleri iletişim kutusunda **Tanıyıcının son duyduğunu, seçtiğin bir komutun söylenen ifadesi olarak ekleyen bir pencere açar** komutuna bir tuş da atayabilirsin.
3.  Üstteki listede tanıyıcının ürettiği metinler işaretli olarak gelir. Yanlış görünenlerin işaretini kaldır.
4.  **Komut ara** alanında komutu bul, aşağıdaki listede seç ve **İfadeleri kaydet**'i seç.

İşaretli metinler o komutun ifadeleri olarak, ifade düzenleyicide elle yazmış gibi kaydedilir; sonra orada düzenleyebilir ya da silebilirsin. Bunlar modelin zaten bildiği sözcükler olduğundan aynı söyleyiş bir dahaki sefere doğrudan bulunur. Liste, sesli komutu en son söylediğinde tanıyıcının ne duyduğunu gösterir; komut tanınsın tanınmasın. Bu yüzden pencereyi tanınmayan komuttan hemen sonra aç. Pencere, tanıyıcının konuşmandan ne anladığını NVDA günlüğüne bakmadan görmenin de hızlı bir yoludur. Komut kutusuna yazdığın komutlar listeye girmez.

## İfadelerini paylaşmak ve yedeklemek

İfade düzenleyici ifadelerini bir dosyaya kaydedip yeniden yükleyebilir; böylece onları yedekleyebilir, başka bir bilgisayara taşıyabilir ya da başkalarıyla paylaşabilirsin.

- **İfadeleri dışa aktar...** (Ctrl+E) düzenleyicideki ifadeleri ve özgün açıklamasını kapattığın komutları bir `.json` dosyasına kaydeder. İfadesi olmayan komutlar dosyaya yazılmaz.
- **İfadeleri içe aktar...** (Ctrl+I) böyle bir dosyayı okur ve içindeki ifadeleri düzenleyiciye ekler. Sende zaten olan hiçbir şey silinmez ya da değiştirilmez: zaten sahip olduğun ifadeler atlanır ve ayarı zaten bulunan bir komutta senin **Özgün açıklamayı da kullan** seçimin korunur. NVDA kaç değişikliğin içe aktarıldığını söyler. Komutları metniyle adlandıran bir dosyada, örneğin aşağıdaki Türkçe sette, bu sayı dosyadaki her ifadeyi, zaten sahip olduklarını da, sayar; zaten sahip olduğun ifadeler yine de atlanır. **Kaydet**'i (Ctrl+S) seçene kadar hiçbir şey saklanmaz; bu yüzden sonucu önce gözden geçirebilir, istemezsen İptal'i seçebilirsin.

İfade düzenleyicide bu kısayollar odak nerede olursa olsun çalışır.

Dosya, Sesli Komut ayar klasöründeki `aliases.json` ile aynı biçimdedir (bkz. Ayarlar ve veriler); bu yüzden o dosyanın bir kopyası da içe aktarılabilir. İfadeler komutlara arayüz diline bağlı olmayan bir kimlikle bağlıdır; bu yüzden düzenleyicinin hazırladığı bir dosya her NVDA dilinde çalışır. Bir dosya komutu kimlik yerine düzenleyici listesinde göründüğü gibi metniyle de adlandırabilir: `açıklama - kategori`, örneğin `Masaüstünü göster - Windows komutları`. Böyle bir girdi yalnızca NVDA o metnin dilindeyken eşleşir. Bilgisayarında bulunmayan bir komutun ifadesi, örneğin kurulu olmayan bir uygulamanın komutu, saklanır ama o komut var olana kadar bir işe yaramaz. Düzenleyici yalnızca açtığın yerde kullanılabilen komutları listeler; bu yüzden içe aktarılan ifadelerini görmek için düzenleyiciyi ilgili uygulamanın içinde aç. Kendi komutların (bkz. Kendi komutların) her bilgisayarda farklı bir kimlik alır, bu yüzden onların ifadeleri taşınmaz; aynı ifadeleri diğer bilgisayardaki komutlara kendin ekle.

**Hazır Türkçe set.** Eklenti, `locale\tr\LC_MESSAGES` klasöründe `tr-phrases.json` dosyasıyla gelir: NVDA'nın kendi komutları ve birçok yaygın eklenti için kısa (iki ya da üç sözcüklük) Türkçe ifadeler. Başka bir dosya gibi içe aktar. Komutları metniyle adlandırdığı için (bkz. yukarısı) Türkçe NVDA'da çalışır. Ayarın olmadığı komutlarda uzun özgün açıklamayı da kapatır; böylece o komut yalnızca kısa ifadeye yanıt verir. İkisini de istersen düzenleyicide **Özgün açıklamayı da kullan**'ı yeniden aç. Set, komutların ek basışları için de ifadeler içerir; bunlar sonlarında basış sayısıyla yazılır, örneğin saati bildiren komut için "tarihi söyle x2" (bkz. Kendi ifadelerin).

## Komutları sesli denetimin dışında tutmak

Bazı komutların sesle çalışmasını hiç istemeyebilirsin; örneğin riskli oldukları için ("pencereyi kapat", "bilgisayarı kilitle") ya da diğerlerine çok benzedikleri ve sık sık yanlışlıkla seçildikleri için. Birini dışarıda tutmak için:

1.  İfade düzenleyiciyi aç ve komutu, Kendi ifadelerin bölümünde anlatıldığı gibi seç.
2.  **Özgün açıklamayı da kullan** kutusunu temizle ve kendi ifadelerinden hiçbirini ekleme.
3.  **Kaydet**'i seç.

Komut artık eklentinin dinlediği şeylerin parçası olmaz; yani hiç çalıştırılmaz, aday listesinde sunulmaz ve ses benzerliğiyle de eşleştirilmez. Girdi Hareketleri iletişim kutusundaki kendi tuşuyla çalışmaya devam eder. Bu, NVDA komutları, yerleşik Windows komutları ve kendi komutların için geçerlidir. Bir komutu geri getirmek için yeniden seç ve **Özgün açıklamayı da kullan** kutusunu aç ya da bir ifade ekle. Kendi komutunu iletişim kutusunda silmen de yeterlidir.

Bir komutu dışarıda tutmak tanımayı da daha güvenilir yapar: seçilecek komut ne kadar azsa, benzer bir komutun söylediğin yerine seçilme olasılığı o kadar düşer.

## Komutu tekrarlamak

İfadenin sonuna bir sayı ve "kez" ekle: "satırı oku iki kez", "sonraki satır üç kez". Sayı iki ile beş arasında olabilir, rakamlar da çalışır ("3 kez"). "defa" ve "kere" de kabul edilir. Tekrarı kendi ifadene de yerleştirebilirsin (bkz. Kendi ifadelerin); bir tekrar da söylersen, söylediğin kullanılır.

Ne olacağı komuta bağlıdır. İkinci ya da üçüncü basışta başka bir şey yaptığı için birden çok basışa tepki veren bir komut bir kez çalıştırılır ve NVDA'ya tuşuna o kadar kez basıldığı söylenir. Geçerli satırı bildiren komut bir basışta okur, iki basışta hecelerek okur, üç basışta karakter açıklamalarını verir; bu yüzden "satırı oku üç kez" yalnızca karakter açıklamalarını verir, tuşa üç kez basmak gibi; satırı önce okuyup sonra heceleyerek okumaz. Sonraki satıra gitmek gibi diğer komutlar ise yalnızca art arda o kadar kez çalışır.

Eklenti bir komutun tekrarlanan basışlara tepki verdiğini anlayamazsa, onu diğerleri gibi ele alır ve art arda o kadar kez çalıştırır. Debug günlük düzeyinde günlükteki "Voice command repeat" satırı ne bulduğunu söyler (bkz. Sorun giderme).

## Tuşlara sesle basmak

Girdi Hareketleri'ndeki **Emulated system keyboard keys** (taklit edilen sistem klavye tuşları) kategorisinin komutları senin yerine sistem klavyesinde bir tuşa basar; örneğin bir ok tuşuna, Tab'a ya da Escape'e. Diğer komutlar gibi çalışırlar ve tekrar özelliği burada özellikle işe yarar: "aşağı ok üç kez" tuşa üç kez basar. Tuşun adını Girdi Hareketleri iletişim kutusunda göründüğü gibi söyle. NVDA basışı kendi taklit ettiği tuşlara davrandığı gibi ele alır: önce kendi komutlarının tuşu işlemesine izin verir, aksi halde tuşu sisteme gönderir.

## Yerleşik Windows komutları

NVDA'nın Girdi Hareketleri iletişim kutusu yalnızca NVDA'nın kendi komutlarını listeler. Bu yüzden eklenti, Windows genelinde kullanılan komutlardan oluşan kendi kümesini getirir. Bunları diğer komutlar gibi söylersin; örneğin "masaüstünü göster", "görev çubuğunu göster", "sistem tepsisini göster", "kopyala" ya da "yapıştır". Her biri Windows'un zaten kullandığı kısayola basar, bu yüzden her uygulamada çalışır. Harfle biten kısayollara (örneğin Windows+I) karakterle değil tuşun sanal tuş koduyla basılır; bu yüzden Türkçe dahil her klavye düzeninde çalışırlar.

- **Masaüstü ve kabuk:** masaüstünü göster, görev çubuğunu göster, sistem tepsisini göster, Başlat menüsünü aç, Dosya Gezginini aç, Çalıştır penceresini aç, Windows ayarlarını aç, Windows aramasını aç, hızlı ayarları aç, bildirim merkezini aç, pano geçmişini aç, emoji panelini aç, Windows sesle yazmayı başlat, yansıtma menüsünü aç, ekran görüntüsü al, Görev Yöneticisini aç, bilgisayarı kilitle.
- **Pencereler ve sanal masaüstleri:** tüm pencereleri küçült, küçültülen pencereleri geri yükle, görev görünümünü göster, önceki pencereye geç, pencereyi kapat, pencereyi büyüt, pencereyi küçült, pencereyi sola ya da sağa yasla, sonraki, önceki, yeni sanal masaüstü ve sanal masaüstünü kapat.
- **Ses ve medya:** sesi artır, sesi azalt, sesi kapat veya aç, medyayı oynat veya duraklat, sonraki parça, önceki parça.
- **Düzenleme:** kopyala, kes, yapıştır, tümünü seç, geri al, yinele, kaydet, bul, yazdır, yeni oluştur, dosya aç, yeniden adlandır, özellikler, yenile.
- **Gezinme ve sekmeler:** geri git, ileri git, yeni sekme, sekmeyi kapat, kapatılan sekmeyi yeniden aç, sonraki sekme, önceki sekme.

Tekrarlamanın anlamlı olduğu komutlar "iki kez" gibi ekleri kabul eder; örneğin "sesi artır üç kez" ya da "sonraki sekme iki kez". Bu komutlar ifade düzenleyicide **Windows komutları** kategorisi altında görünür; böylece onlara kendi ifadelerini ekleyebilir ya da özgün ifadelerini kapatabilirsin. Aynı açıklamaya sahip bir NVDA komutu varsa o öncelik alır. Açıklamalar çevrilebilir, bu yüzden söylediğin ifadeler kendi dilindedir.

## Kendi komutların

Kendi komutlarını ekleyebilirsin. Girdi Hareketleri iletişim kutusunun Sesli Komut kategorisinde **Kendi komutlarını eklemek için iletişim kutusunu açar** komutuna bir tuş ata, tuşa bas ve **Ekle**'yi seç. Söyleyeceğin ifadeyi yaz, sonra komutun ne yapacağını seç:

- **Program, dosya, klasör veya web adresi aç:** yaz ya da düğmelerle göz at. Çift tıklamış gibi açılır; yani bir web adresi tarayıcında açılır. `%USERPROFILE%` gibi ortam değişkenleri çalışır; `müzik`, `belgeler`, `indirilenler`, `masaüstü`, `resimler`, `videolar` gibi düz klasör adları (İngilizce adlar da) ve Windows `shell:` adresleri de çalışır. `notepad` gibi sistem yolundaki programlar için klasör yazmak gerekmez.
- **Tuş kombinasyonuna bas:** tuşları NVDA'nın tuş adlarıyla yaz; örneğin `control+shift+n`. `ctrl`, `win`, `esc` ve `left` gibi yaygın yazımlar da anlaşılır. Tuş komutları tekrarlanabilir ("iki kez").

Komutların ifade düzenleyicide **Komutlarım** kategorisi altında listelenir; oradan onlara ek ifadeler verebilirsin. Bir komutunun adı bir NVDA komutuyla aynıysa seninki kullanılır. Burada hiçbir betik ya da kabuk komutu çalışmaz: komut ya hedefini Windows'a verir ya da tuşlara basar. Komutların `userCommands.json` dosyasında saklanır (bkz. Ayarlar ve veriler).

## Emin olamadığında

Birkaç komut hemen hemen eşit uyduğunda ya da hiçbiri kendi başına çalışacak kadar iyi uymadığında en iyi adayların bir listesi açılır. (Bir sherpa modelinde liste yalnızca bir şey bir komuta benzediğinde açılır; aksi halde NVDA yalnızca ne duyduğunu söyler.) Ok tuşlarıyla gezin, istediğini çalıştırmak için Enter'a bas, vazgeçmek için Escape'e bas. Bir tekrar söylediysen, seçtiğin komuta uygulanır.

## Konuşmak yerine yazmak

**Komut cümlesi yazabileceğin bir kutu açar** komutuna bir tuş ata. Yazdığın metin konuşmayla aynı eşleştirmeden geçer; ifadeleri denemek ve konuşamadığın durumlar için kullanışlıdır. Burada da tekrar çalışır: ifadenin sonuna Komutu tekrarlamak bölümündeki gibi "iki kez" ya da "x2" gibi bir basış sayısı ekle (bkz. Kendi ifadelerin).

## Komut başvurusu

Hepsi Girdi Hareketleri iletişim kutusunda, Sesli Komut kategorisindedir.

| Komut                                                                                                                             | Ne yapar                                                                 |
|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Sesli komut dinlemesini başlatır; dinlemeyi durdurup komutu çalıştırmak için tekrar basın ya da konuştuktan sonra bir an sessiz kalın                                             | Ana komuttur. Başlatmak için bir kez, durdurmak için tekrar bas.         |
| Komut cümlesi yazabileceğin bir kutu açar                                                                                         | Yazılan ifadeyi aynı eşleştirmeden geçirir.                              |
| Komutlar için kullanılan ifadeleri (takma adları) düzenleme penceresini açar                                                      | İfade düzenleyiciyi açar.                                                |
| Tanıyıcının son duyduğunu, seçtiğin bir komutun söylenen ifadesi olarak ekleyen bir pencere açar                                  | Tanıyıcının bilmediği bir adı öğretir.                                   |
| Sesli komut dinlenirken diğer uygulamaların sesini kısmayı açar ya da kapatır                                                     | Ses kısmayı açar ya da kapatır.                                          |
| Konuştuktan sonra sessiz kalınca dinlemeyi kendiliğinden durdurmayı açar ya da kapatır                                            | Sessizlikte durdurmayı açar ya da kapatır.                               |
| Konuşma modeli penceresini açar: modeli seç, indir ve yönet                                                                       | Konuşma modelini seçer, sorduktan sonra indirir ve model klasörünü açar. |
| Kendi komutlarını eklemek için iletişim kutusunu açar: program, dosya, klasör ya da web adresi açma veya tuş kombinasyonuna basma | Kendi komutların için iletişim kutusunu açar.                            |

## Diğer uygulamaların sesini kısmak

Müzik ve videolar mikrofona karışır ve tanıyıcıyı şaşırtır. Dinlerken NVDA'nınki dışındaki tüm ses oturumları özgün ses düzeyinin %20'sine indirilir ve durdurduğunda geri getirilir. Bu arada sesini sen değiştirdiysen o oturuma dokunulmaz.

Tarayıcılar ve python.exe üzerinden çalınan medya gibi bazı oynatıcılar, örneğin duraklattığında, parça değiştiğinde ya da söylediğin komut parçayı değiştirdiğinde ses oturumunu kapatıp yenisini açar. Windows yeni oturumu hatırladığı kısık ses düzeyiyle açar. Bu yüzden eklenti böyle oturumları uygulamanın adıyla da arar ve onların sesini de geri getirir: dinleme durduktan hemen sonra, bir de 1,5 ve 4 saniye sonra; çünkü "sonraki parça" gibi bir komut oturumunu ancak dinleme durduktan sonra açar. Hiç geri yüklenemeyen bir oturum hatırlanır ve bir sonraki kısmadan önce düzeltilir; böylece kısık ses özgün ses sanılmaz. Bu kayıtlar en çok 24 saat tutulur.

Windows uygulama başına ses düzeylerini hatırladığı için eklenti küçük bir kurtarma dosyası da kaydeder. Ses kısıkken NVDA kapanırsa, özgün ses düzeyleri NVDA'nın bir sonraki açılışında geri yüklenir.

Bu özellik NVDA ile gelen bir kütüphane kullanır. O yoksa dinleme yine çalışır, yalnızca hiçbir şey kısılmaz. Açıp kapatmak için ilgili komutu kullanabilirsin.

## Ses tanıma modeli

Araçlar menüsünden **Konuşma modeli...**'ni aç ya da **Konuşma modeli penceresini açar: modeli seç, indir ve yönet** komutuna bir tuş ata. Pencere NVDA dilin için kullanılabilen modelleri listeler ve her birinin kullanımda, kurulu ya da kurulu değil olduğunu gösterir.

- **Kullan** seçili modele geçer (bir modele çift tıklamak da aynı işi yapar). Kurulu olmayan model önce indirilir: eklenti boyutunu, nereden geldiğini ve lisansını söyler, ancak sen onay verdikten sonra indirir. Dinlerken ya da bir indirme sürerken model değiştirilemez.
- **Model klasörünü aç** modellerin tutulduğu klasörü açar; bir modeli elle kurmak için.

| Model                                     | Diller                                    | İndirme                  | Lisans                                                              |
|-------------------------------------------|-------------------------------------------|--------------------------|---------------------------------------------------------------------|
| Vosk (küçük model)                        | Resmî listede modeli olan her dil         | Genellikle 40 ile 100 MB | Model listesine bak                                                 |
| turkish-stt (mihu AI)                     | Türkçe                                    | 68 MB                    | mihu Community License (kişisel kullanım için ücretsiz)             |
| Kroko English, Français, Deutsch, Español | İngilizce, Fransızca, Almanca, İspanyolca | 57, 57, 58 ve 124 MB     | Kroko topluluk modeli; koşullar huggingface.co/Banafo/Kroko-ASR     |
| Zipformer ru (Alpha Cephei)               | Rusça                                     | 24 MB                    | huggingface.co/alphacep/vosk-model-small-streaming-ru sayfasına bak |

**Vosk mu, sherpa modeli mi.** Vosk komut listesiyle kısıtlanır; bu kısa komutlara uygundur. sherpa modelleri serbest metin yazar; bu genellikle sıradan konuşmayı ve bilinmeyen sözcükleri daha iyi karşılar ama komutlarla daha sıkı eşleştirilir (bkz. Ne söyleyeceğini seçmek). İkisini de dene ve sesin ile mikrofonunla daha iyi çalışanı bırak. Varsayılan, henüz Vosk modeli kurulu olmayan Türkçe NVDA'da turkish-stt'dir; kurulu bir Vosk modeli sen bilmeden asla değiştirilmez ve diğer tüm diller sen bir sherpa modeli seçene kadar Vosk'ta kalır. Seçimin hatırlanır. NVDA'yı, seçtiğin sherpa modelinin kapsamadığı bir dile geçirirsen eklenti Vosk'a döner.

**Bir sherpa modeli kurmak.** İlk sherpa modeli ayrıca sherpa-onnx çalışma zamanını (üç DLL dosyası, 21 MB) gerektirir. Çalışma zamanı github.com'dan indirilir, her zaman aynı sürümdür ve sabit bir sağlama toplamıyla denetlenir; model dosyaları huggingface.co ya da github.com'dan gelir ve onlar da denetlenir. Çalışma zamanı `voiceCommands\sherpa-runtime` klasöründe, her model de `voiceCommands\model` içinde kendi `sherpa-...` klasöründe tutulur. Çalışma zamanı 64 bit NVDA gerektirir. Windows kullanıcı adında ş, ğ ya da ı gibi harfler varsa eklenti klasörün kısa (8.3) adını kullanır; bazı sürücülerde bu kapalıdır (bkz. Sorun giderme).

**Vosk modelleri.**

- Eklenti modeli NVDA ayar klasörünün içindeki `voiceCommands\model` klasöründe arar, örneğin `%AppData%\nvda\voiceCommands\model`. Penceredeki **Model klasörünü aç** seni oraya götürür.
- Otomatik indirme <https://alphacephei.com/vosk/models> adresindeki resmî model listesini kullanır. NVDA dilin için küçük bir model seçer, sağlama toplamını doğrular ve o klasöre açar.
- Modeli kendin kurmak için o sayfadan bir model indir ve model klasörüne aç. Vosk'un iki model düzeni de tanınır, dosyalar bir alt klasörde de olabilir.
- Büyük modeller daha doğrudur ama çok daha fazla bellek ister ve daha geç yüklenir.
- Dilin için hazır bir model yoksa eklenti model sayfasını açmayı önerir.

## Ayarlar ve veriler

`%AppData%\nvda\voiceCommands` klasöründe ya da taşınabilir NVDA'nın ayar klasöründe saklanır:

| Öğe                     | İçerik                                                                                                                                                                         |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `aliases.json`          | İfade düzenleyicideki ve öğretme penceresinden kaydedilen ifadelerin.                                                                                                          |
| `userCommands.json`     | Kendi komutların.                                                                                                                                                              |
| `settings.json`         | Ses kısmanın açık olup olmadığı, açılışta indirme sorulup sorulmayacağı, dinlemenin sessizlikte durup durmayacağı ve sessizliğin süresi, ve seçtiğin motor ile model.          |
| `ducking-recovery.json` | Geçici: yalnızca diğer uygulamaların sesi kısıkken ve geri yüklenemeyen bir ses düzeyi varken (en çok 24 saat) bulunur; bir çökmeden sonra sesi geri getirmek için kullanılır. |
| `model\`                | Ses tanıma modelleri: Vosk modelleri ve `sherpa-...` klasörleri.                                                                                                               |
| `sherpa-runtime\`       | sherpa-onnx çalışma zamanı; ilk sherpa modeliyle birlikte indirilir.                                                                                                           |

`globalPlugins/voiceCommands/__init__.py` dosyasının başındaki değerler, örneğin eşleştirme eşikleri ve aday listesinin boyutu, davranışı ayarlamak istersen düzenlenebilir.

## Sorun giderme

| Sorun                                                | Neye bakmalı                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Vosk modeli bulunamadı"                             | Yukarıda anlatıldığı gibi bir model kur. Mesaj tam klasörü söyler.                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| "Seçilen konuşma motoru kurulu değil"                | **Konuşma modeli...** penceresini aç ve **Kullan**'ı seç: eklenti yeniden indirmeyi önerir. Bu hâlâ başarısız oluyorsa `model\` altındaki modelin klasörünü ve `sherpa-runtime` klasörünü sil, sonra yeniden indir.                                                                                                                                                                                                                                                                                             |
| Bir sherpa modeliyle "Model yüklenemedi"             | NVDA'nın 64 bit olduğundan emin ol. Windows kullanıcı adında ş, ğ ya da ı gibi harfler varsa, sürücüde kısa klasör adları kapalıysa model yüklenmeyebilir; günlüğe bak (bkz. aşağısı) ve sürekli başarısız oluyorsa Vosk'u kullan.                                                                                                                                                                                                                                                                              |
| "Duyulan: ... Eşleşen komut yok"                     | Bir sherpa modeli sözcükleriyle hiçbir komuta uymayan bir metin yazdı. Metin söylediğinse komutun adı başkadır: kendi kısa ifadeni ekle (bkz. Kendi ifadelerin). Değilse yeniden söyle ya da başka bir model dene.                                                                                                                                                                                                                                                                                              |
| Hiçbir şey tanınmıyor                                | Windows'ta doğru mikrofonun varsayılan olduğundan ve sessize alınmadığından emin ol.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Bir ad hiç tanınmıyor                                | Model adı başka sözcükler olarak yazıyor olabilir. Söyledikten hemen sonra **Son söylenen ifadeyi öğret...** penceresini aç, duyulanı gör ve ifade olarak kaydet (bkz. Tanıyıcının bilmediği adlar).                                                                                                                                                                                                                                                                                                            |
| Yanlış komut çalışıyor                               | O komut için ifade düzenleyicide kendi kısa ifadeni tanımla.                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| "Bu komut şu an kullanılamıyor"                      | Komut başka bir uygulamaya ait. Onu o uygulama odaktayken söyle.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Müzik ya da video hâlâ karışıyor                     | Bazı uygulamalar kısılabilen bir ses oturumu sunmaz. Dinlemeden önce onları duraklat.                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Tekrarlanan komut önceki basışların işini de yapıyor | Eklenti komutun tekrarlanan basışlara tepki verdiğini anlayamadı ve onu art arda o kadar kez çalıştırdı (örneğin "pencere başlığı üç kez" başlığı okudu, hecelerek okudu ve kopyaladı). Debug günlük düzeyinde "Voice command repeat: 3, script counts presses: False" satırı bunu doğrular. Böyle bir komut ancak art arda çalıştırılarak tekrarlanabilir: sesle söylemek yerine tuşuna bas ya da eklentinin yazarına hangi komut olduğunu bildir.                                                             |
| Bir komuttan sonra oynatıcı sessiz kalıyor           | Oynatıcı, ses düzeyi kısıkken ses oturumunu yeniden açtı. Eklenti böyle oturumların sesini dinleme durduktan hemen sonra, bir de 1,5 ve 4 saniye sonra yükseltir. Biri hâlâ sessizse Windows ses karıştırıcısında sesini bir kez yükselt. Debug günlük düzeyinde "Voice command: could not restore ... keeping it pending" satırı uygulamanın adını verir.                                                                                                                                                      |
| Ne duyulduğunu görmek istiyorsun                     | Konuştuktan hemen sonra **Son söylenen ifadeyi öğret...** penceresini aç: listede tanıyıcının ürettiği metinler görünür. Daha fazla ayrıntı için NVDA menüsü, Tercihler, Ayarlar, Gizlilik ve güvenlik bölümündeki günlük düzeyini Debug (hata ayıklama) yap, konuş ve NVDA günlüğünü aç (NVDA+F1). "Voice command recognition" satırları her tanıyıcının ne duyduğunu, "Voice command candidate" satırları en iyi eşleşmelerin ne kadar yakın olduğunu gösterir. Bu satırlar yalnızca Debug düzeyinde yazılır. |

## Gizlilik

Mikrofondan gelen ses bilgisayarında ses tanıma motoru (Vosk ya da sherpa-onnx) tarafından işlenir ve hiçbir yere gönderilmez. Ağ yalnızca bir indirmeye izin verdiğinde ve yalnızca alphacephei.com (Vosk modelleri), huggingface.co (turkish-stt modeli) ve github.com'a (sherpa-onnx çalışma zamanı ile diğer sherpa modelleri) ulaşmak için kullanılır.

## Çeviri

Eklenti İngilizce yazılmıştır ve Türkçe çeviriyle gelir. Çevirmek için `voiceCommands.pot` dosyasını `locale/<dil>/LC_MESSAGES/nvda.po` olarak kopyala ve iletileri çevir; her birinde çevirmenler için bir açıklama vardır. Komutu tekrarlamakta kullanılan sözcükler ("two times") de çevrilebilir, böylece konuşma kendi dilinde doğal olur.

## Lisans

Sesli Komut, GNU Genel Kamu Lisansı sürüm 2 (GPL-2.0) altında lisanslanmıştır. Pakete dahil üçüncü taraf bileşenler ve lisansları [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) dosyasında listelenir.

Eklentinin indirdiği sherpa-onnx çalışma zamanı Apache Lisansı 2.0 ile, içindeki ONNX Runtime kütüphanesi MIT lisansıyla lisanslanmıştır. Her ses tanıma modelinin kendi lisansı vardır (bkz. Ses tanıma modeli).