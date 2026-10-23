# NVDA için Sesli Komut

NVDA komutlarını tuşlara basmak yerine konuşarak çalıştır.

NVDA'nın Girdi Hareketleri iletişim kutusunda her komut için bir açıklama vardır. Sesli Komut, mikrofonundan seni dinler, konuşmanı çevrimdışı çalışan [Vosk](https://alphacephei.com/vosk/) motoruyla yazıya çevirir, bu yazıyı o açıklamalarla (ve kendi tanımladığın ifadelerle) eşleştirir ve en uygun komutu çalıştırır. Sesin bilgisayarından dışarı çıkmaz.

## Nasıl çalışır

1.  Dinlemeyi başlattığında eklenti o an kullanılabilir komutları toplar. Bu, üzerinde çalıştığın uygulamanın komutlarını da kapsar; başka bir uygulamanın komutu yalnızca o uygulama odaktayken sunulur.
2.  Konuşur, sonra dinlemeyi durdurursun. Vosk konuşmanı yazıya çevirir.
3.  Yazı, komut açıklamalarıyla ve kendi ifadelerinle karşılaştırılır. Tanıyıcıya hangi ifadeleri beklemesi gerektiği de söylenir; bu, serbest dikteye göre çok daha doğru sonuç verir.
4.  Bir komut açıkça uyuyorsa çalışır. Birkaçı hemen hemen eşit uyuyorsa bir liste açılır ve sen seçersin.

## Gereksinimler

- Windows üzerinde NVDA 2026.1 ya da sonrası, 64 bit.
- Windows'ta varsayılan kayıt aygıtı olarak ayarlanmış bir mikrofon.
- Ses tanıma modelini indirmek için bir kez internet bağlantısı (küçük bir model yaklaşık 40 ile 100 MB'tır).

## Kurulum ve ilk çalıştırma

1.  `.nvda-addon` dosyasını aç ve kurulumu onayla. İstenince NVDA'yı yeniden başlat.
2.  NVDA açıldıktan birkaç saniye sonra eklenti kurulu bir ses tanıma modeli olmadığını fark eder ve NVDA dilin için bir model indirmesine izin verip vermediğini sorar. **Evet**'i seç. İndirme arka planda yapılır; NVDA ilerlemeyi söyler ve sesli komutların ne zaman hazır olduğunu bildirir.

**Hayır**'ı seçersen eklenti açılışta bir daha sormaz. Dinlemeyi başlattığında ya da "Ses tanıma modelini NVDA diline göre indirir" komutunu kullandığında yeniden sorulursun.

## Hızlı başlangıç

Varsayılan olarak hiçbir tuş atanmamıştır, tuşları kendin seç:

1.  NVDA menüsünü, ardından Tercihler ve Girdi hareketleri'ni aç.
2.  **Sesli Komut** kategorisini genişlet ve **Sesli komut dinlemesini başlatır; tekrar basınca dinlemeyi durdurup komutu çalıştırır** komutuna bir tuş ata. İstersen oradaki diğer komutlara da tuş atayabilirsin.

Sonra sesli komut vermek için:

1.  Tuşa bas. Yüksek bir bip dinlemenin başladığını bildirir.
2.  Komutu söyle.
3.  Aynı tuşa tekrar bas. Alçak bir bip dinlemenin bittiğini bildirir ve komut çalışır.

Hiçbir şey tanınmazsa NVDA "Anlaşılamadı" der.

## Ne söyleyeceğini seçmek

NVDA'nın açıklamaları çoğu zaman tam cümledir. Hepsini söylemen gerekmez.

| Ne söylersin                                                                               | Ne beklemelisin                                                                     |
|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Girdi Hareketleri'nde komutun yanında görünen açıklamanın ilk cümlesi                      | Genellikle iyi çalışır. Birçok komutta ilk cümle açıklamanın tamamıdır.             |
| [İfade düzenleyicide](#kendi-ifadelerin) tanımladığın kısa bir ifade, örneğin "satırı oku" | Tam eşleşir ve en güvenilir yoldur. **Her gün kullandığın komutlar için önerilir.** |
| Hiçbir yerde tanımlanmamış, kendi kısa yorumun                                             | Daha az güvenilirdir. Liste açılabilir ya da benzer başka bir komutla eşleşebilir.  |

Pratikte iki şey işe yarar. İfadeyi düzenli bir hızla, sessiz bir anda söyle ve ayırt edici sözcükleri atlama. Ayrıca en çok kullandığın komutlar için kısa ifadeler tanımla: bir dakikanı alır ve her şeyi hızlandırır.

## Kendi ifadelerin

Komutları kendi cümlenle söylemek için ifade düzenleyiciyi kullan. **Komutlar için kullanılan ifadeleri (takma adları) düzenleme penceresini açar** komutuna bir tuş ata ve komutlarını düzenlemek istediğin uygulamadayken aç.

1.  **Komut ara** alanına birkaç sözcük yazarak listeyi süz, sonra **Komutlar** listesinden komutu seç.
2.  **Yeni ifade** alanına ifadeni yaz ve **İfadeyi ekle**'yi seç. Bir komuta birden çok ifade ekleyebilirsin. Birini değiştirmek ya da kaldırmak için **Bu komut için söyleyeceğin ifadeler** listesinde seç ve **Seçili ifadeyi düzenle** ya da **Seçili ifadeyi sil**'i seç.
3.  Komut yalnızca senin ifadelerine yanıt versin istiyorsan **Özgün açıklamayı da kullan** kutusunu temizle.
4.  **Kaydet**'i seç.

İyi ifadeler kısadır, iki ile dört sözcük arasıdır ve birbirinden farklı duyulur. İfadelerin özgün açıklamalara göre önceliklidir; tekrar özelliğiyle ve aday listesiyle diğer komutlar gibi çalışırlar. Düzenleyici açtığın yerde kullanılabilen komutları gösterir; bir uygulamanın komutlarını düzenlemek için pencereyi o uygulamanın içinde aç.

## Komutları sesli denetimin dışında tutmak

Bazı komutların sesle çalışmasını hiç istemeyebilirsin; örneğin riskli oldukları için ("pencereyi kapat", "bilgisayarı kilitle") ya da diğerlerine çok benzedikleri ve sık sık yanlışlıkla seçildikleri için. Birini dışarıda tutmak için:

1.  İfade düzenleyiciyi aç ve komutu, Kendi ifadelerin bölümünde anlatıldığı gibi seç.
2.  **Özgün açıklamayı da kullan** kutusunu temizle ve kendi ifadelerinden hiçbirini ekleme.
3.  **Kaydet**'i seç.

Komut artık eklentinin dinlediği şeylerin parçası olmaz; yani hiç çalıştırılmaz, aday listesinde sunulmaz ve ses benzerliğiyle de eşleştirilmez. Girdi Hareketleri iletişim kutusundaki kendi tuşuyla çalışmaya devam eder. Bu, NVDA komutları, yerleşik Windows komutları ve kendi komutların için geçerlidir. Bir komutu geri getirmek için yeniden seç ve **Özgün açıklamayı da kullan** kutusunu aç ya da bir ifade ekle. Kendi komutunu iletişim kutusunda silmen de yeterlidir.

Bir komutu dışarıda tutmak tanımayı da daha güvenilir yapar: seçilecek komut ne kadar azsa, benzer bir komutun söylediğin yerine seçilme olasılığı o kadar düşer.

## Komutu tekrarlamak

İfadenin sonuna bir sayı ve "kez" ekle: "satırı oku iki kez", "sonraki satır üç kez". Sayı iki ile beş arasında olabilir, rakamlar da çalışır ("3 kez"). "defa" ve "kere" de kabul edilir. Komut o kadar kez art arda çalışır.

Birden çok basışa tepki veren komutlarda NVDA bunu tekrarlanan tuş basışı sayar. Örneğin geçerli satırı bildiren komut bir kez okur, iki kez hecelerek okur, üç kez karakter açıklamalarını verir. Sonraki satıra gitmek gibi diğer komutlarda ise etki yalnızca birkaç kez gerçekleşmesidir.

## Tuşlara sesle basmak

Girdi Hareketleri'ndeki **Emulated system keyboard keys** (taklit edilen sistem klavye tuşları) kategorisinin komutları senin yerine sistem klavyesinde bir tuşa basar; örneğin bir ok tuşuna, Tab'a ya da Escape'e. Diğer komutlar gibi çalışırlar ve tekrar özelliği burada özellikle işe yarar: "aşağı ok üç kez" tuşa üç kez basar. Tuşun adını Girdi Hareketleri iletişim kutusunda göründüğü gibi söyle. NVDA basışı kendi taklit ettiği tuşlara davrandığı gibi ele alır: önce kendi komutlarının tuşu işlemesine izin verir, aksi halde tuşu sisteme gönderir.

## Yerleşik Windows komutları

NVDA'nın Girdi Hareketleri iletişim kutusu yalnızca NVDA'nın kendi komutlarını listeler. Bu yüzden eklenti, Windows genelinde kullanılan komutlardan oluşan kendi kümesini getirir. Bunları diğer komutlar gibi söylersin; örneğin "masaüstünü göster", "görev çubuğunu göster", "sistem tepsisini göster", "kopyala" ya da "yapıştır". Her biri Windows'un zaten kullandığı kısayola basar, bu yüzden her uygulamada çalışır.

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

Birkaç komut hemen hemen eşit uyduğunda ya da hiçbiri kendi başına çalışacak kadar iyi uymadığında en iyi adayların bir listesi açılır. Ok tuşlarıyla gezin, istediğini çalıştırmak için Enter'a bas, vazgeçmek için Escape'e bas. Bir tekrar söylediysen, seçtiğin komuta uygulanır.

## Konuşmak yerine yazmak

**Komut cümlesi yazabileceğin bir kutu açar** komutuna bir tuş ata. Yazdığın metin konuşmayla aynı eşleştirmeden geçer; ifadeleri denemek ve konuşamadığın durumlar için kullanışlıdır.

## Komut başvurusu

Hepsi Girdi Hareketleri iletişim kutusunda, Sesli Komut kategorisindedir.

| Komut                                                                                                                             | Ne yapar                                                         |
|-----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Sesli komut dinlemesini başlatır; tekrar basınca dinlemeyi durdurup komutu çalıştırır                                             | Ana komuttur. Başlatmak için bir kez, durdurmak için tekrar bas. |
| Komut cümlesi yazabileceğin bir kutu açar                                                                                         | Yazılan ifadeyi aynı eşleştirmeden geçirir.                      |
| Komutlar için kullanılan ifadeleri (takma adları) düzenleme penceresini açar                                                      | İfade düzenleyiciyi açar.                                        |
| Sesli komut dinlenirken diğer uygulamaların sesini kısmayı açar ya da kapatır                                                     | Ses kısmayı açar ya da kapatır.                                  |
| Ses tanıma modelini NVDA diline göre indirir                                                                                      | Sorduktan sonra model indirmeyi başlatır.                        |
| Kendi komutlarını eklemek için iletişim kutusunu açar: program, dosya, klasör ya da web adresi açma veya tuş kombinasyonuna basma | Kendi komutların için iletişim kutusunu açar.                    |
| Model klasörünü Dosya Gezgini'nde açar                                                                                            | Modeli elle kurmak için.                                         |

## Diğer uygulamaların sesini kısmak

Müzik ve videolar mikrofona karışır ve tanıyıcıyı şaşırtır. Dinlerken NVDA'nınki dışındaki tüm ses oturumları özgün ses düzeyinin %20'sine indirilir ve durdurduğunda geri getirilir. Bu arada sesini sen değiştirdiysen o oturuma dokunulmaz.

Windows uygulama başına ses düzeylerini hatırladığı için eklenti küçük bir kurtarma dosyası da kaydeder. Ses kısıkken NVDA kapanırsa, özgün ses düzeyleri NVDA'nın bir sonraki açılışında geri yüklenir.

Bu özellik NVDA ile gelen bir kütüphane kullanır. O yoksa dinleme yine çalışır, yalnızca hiçbir şey kısılmaz. Açıp kapatmak için ilgili komutu kullanabilirsin.

## Ses tanıma modeli

- Eklenti modeli NVDA ayar klasörünün içindeki `voiceCommands\model` klasöründe arar, örneğin `%AppData%\nvda\voiceCommands\model`. "Model klasörünü Dosya Gezgini'nde açar" komutu seni oraya götürür.
- Otomatik indirme <https://alphacephei.com/vosk/models> adresindeki resmî model listesini kullanır. NVDA dilin için küçük bir model seçer, sağlama toplamını doğrular ve o klasöre açar.
- Modeli kendin kurmak için o sayfadan bir model indir ve model klasörüne aç. Vosk'un iki model düzeni de tanınır, dosyalar bir alt klasörde de olabilir.
- Büyük modeller daha doğrudur ama çok daha fazla bellek ister ve daha geç yüklenir.
- Dilin için hazır bir model yoksa eklenti model sayfasını açmayı önerir.

## Ayarlar ve veriler

`%AppData%\nvda\voiceCommands` klasöründe ya da taşınabilir NVDA'nın ayar klasöründe saklanır:

| Öğe                 | İçerik                                                                     |
|---------------------|----------------------------------------------------------------------------|
| `aliases.json`      | İfade düzenleyicideki ifadelerin.                                          |
| `userCommands.json` | Kendi komutların.                                                          |
| `settings.json`     | Ses kısmanın açık olup olmadığı ve açılışta indirme sorulup sorulmayacağı. |
| `model\`            | Ses tanıma modeli.                                                         |

`globalPlugins/voiceCommands/__init__.py` dosyasının başındaki değerler, örneğin eşleştirme eşikleri ve aday listesinin boyutu, davranışı ayarlamak istersen düzenlenebilir.

## Sorun giderme

| Sorun                            | Neye bakmalı                                                                                                                                                                                                                                                                                                                                             |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Vosk modeli bulunamadı"         | Yukarıda anlatıldığı gibi bir model kur. Mesaj tam klasörü söyler.                                                                                                                                                                                                                                                                                       |
| Hiçbir şey tanınmıyor            | Windows'ta doğru mikrofonun varsayılan olduğundan ve sessize alınmadığından emin ol.                                                                                                                                                                                                                                                                     |
| Yanlış komut çalışıyor           | O komut için ifade düzenleyicide kendi kısa ifadeni tanımla.                                                                                                                                                                                                                                                                                             |
| "Bu komut şu an kullanılamıyor"  | Komut başka bir uygulamaya ait. Onu o uygulama odaktayken söyle.                                                                                                                                                                                                                                                                                         |
| Müzik ya da video hâlâ karışıyor | Bazı uygulamalar kısılabilen bir ses oturumu sunmaz. Dinlemeden önce onları duraklat.                                                                                                                                                                                                                                                                    |
| Ne duyulduğunu görmek istiyorsun | Bu satırlar yalnızca Debug (hata ayıklama) günlük düzeyinde yazılır; önce NVDA menüsü, Tercihler, Ayarlar, Genel bölümündeki günlük düzeyini Debug yap. Sonra NVDA günlüğünü aç (NVDA+F1). "Voice command recognition" satırları her tanıyıcının ne duyduğunu, "Voice command candidate" satırları en iyi eşleşmelerin ne kadar yakın olduğunu gösterir. |

## Gizlilik

Mikrofondan gelen ses bilgisayarında Vosk tarafından işlenir ve hiçbir yere gönderilmez. Ağ yalnızca model indirmesine izin verdiğinde ve yalnızca alphacephei.com'a ulaşmak için kullanılır.

## Çeviri

Eklenti İngilizce yazılmıştır ve Türkçe çeviriyle gelir. Çevirmek için `voiceCommands.pot` dosyasını `locale/<dil>/LC_MESSAGES/nvda.po` olarak kopyala ve iletileri çevir; her birinde çevirmenler için bir açıklama vardır. Komutu tekrarlamakta kullanılan sözcükler ("two times") de çevrilebilir, böylece konuşma kendi dilinde doğal olur.

## Lisans

Sesli Komut, NVDA'nın kendi lisansının eklentilerden istediği gibi, GNU Genel Kamu Lisansı sürüm 2 ya da sonrası (GPL-2.0-or-later) altında lisanslanmıştır. Pakete dahil üçüncü taraf bileşenler ve lisansları [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) dosyasında listelenir.
