import cv2
import numpy as np
import dlib
import winsound
import pygame
from scipy.spatial import distance as dist #? Uzaklık hesaplamak için kullandık.  SciPy, bilimsel hesaplamalar için kullanılan çok güçlü bir kütüphanedir. spatial modülü ise uzaysal (mesafe, alan, hacim) hesaplamalar için kullanılır.  eğer bilgisayarında yüklü değilse terminale şunu yazmalısın: pip install scipy
import time



# Ayarlar
EAR_THRESHOLD = 0.25 # Gözün kapalı sayılması için gereken eşik değer
CONSEC_FRAMES = 30   # Alarm çalmadan önce gözün kaç kare kapalı kalması gerektiği
COUNTER = 0
ALARM_ON = False

MAR_THRESHOLD = 0.3 # # Ağzın 'esniyor' sayılması için gereken açıklık (Deneyerek ayarlanır)
YAWN_FRAMES = 15
YAWN_COUNTER = 0
is_yawning = False
yawn_alarm = False

YAWN_CLOCKS = []  #  Her esnenen anın süresini saniye cinsinden tutacak
TIME_LIMIT = 600 #  10 dakika (saniye cinsinden)
YAWN_LIMIT = 4   # Kaç esnemede uyarı verilecek?
yazi_bitis_zamani = 0

DISTRACT_FRAMES = 40
DISTRACT_COUNTER = 0
distract_alarm = False

pygame.mixer.init()

try:
    #pygame.mixer.music.load("alarm.mp3")  #? mp3 dosyayı yüklüyor, yükliyemezse veya böyle dosya yoksa except'deki hatayı yazar.
    eye_alarm = pygame.mixer.Sound("assets/alarm.mp3")
    yawn_warning_1 = pygame.mixer.Sound("assets/yawning1.mp3")
    distract_warning = pygame.mixer.Sound("assets/distract_warning.mp3")
except:
    print("Uyarı: Belirtilen ses dosyası bulunamadı. Lütfen yolu kontrol edin.")



def calculate_mar(mouth): # 60, 61 ,62, 63, 64, 65, 66, 67
    A = dist.euclidean(mouth[1], mouth[7]) # Dikey Mesafeler (Üst ve alt dudak noktaları arası)   61 - 67
    B = dist.euclidean(mouth[2], mouth[6]) # 62 - 66 (Tam orta)
    C = dist.euclidean(mouth[3], mouth[5]) # 63 - 65

    D = dist.euclidean(mouth[0], mouth[4]) # Yatay Mesafe (Dudak köşeleri)

    mar = (A + B + C) / (3.0 * D)

    return mar

def calculate_ear(eye):  #? eye parametresi önce leftEye değişkenini alacak. Bu değişkende 36,37,38,39,40,41  noktalarının (x,y) kordinatlarını tutacak. Yani 6 tane kordinat değeri tutacak çünkü sol gözü çevreleyen noktaların kordinat sayısı bu kadar.  Aşağıya bakıcak olursan eye[1]  demişiz, bu 37. noktanın kordinatına karşılık geliyor. Çünkü 36 noktası, sıfırıncı index olur eye değişkeninde. eye[1] ise 37 olur çünkü eye parametresi 6 kordinatı tutuyor. Eğer opencv projelerinden 8. projem olan FacialLandmarks.py projesine bakarsan orada bu göz çevrelerini noktalar halinde gösteren kodum var ve orada baktığında 37. noktanın kordinatı gözün sol üst kapağının kordinatı. eye[5] ise yani 41. noktanın kordinatı ise gözün sol alt kapağının kordinatı. Yani biz gözün sol üst ve sol alt kapağının kordinatlarını tutan iki noktanın dikey mesafesini öklidyen formülü ile piksel cinsinden uzaklığını buluyoruz.

    # Gözün dikey işaret noktaları arasındaki mesafeyi hesapla
    A = dist.euclidean(eye[1], eye[5])  #? dist.euclidean() Nedir?  Euclidean (Öklid) Mesafesi, iki nokta arasındaki  en kısa mesafeyi hesaplayan matematiksel bir formüldür ve bu solda bu iki nokta arasındaki mesafeyi buluyoruz.  Neden dist. dedik? Çünkü yukarıda from scipy.spatial import distance as dist satırı ile distance kütüphanesini dist adıyla kısalttık.
    B = dist.euclidean(eye[2], eye[4])  #? eye[2] = 38. noktanın kordinatı yani gözün sağ üst kapağının kordinatı ile eye[4] = 40. noktanın kordinatı yani gözün sağ alt kapağının kordinatı arasındaki dikey mesafeyi öklidyen formülü ile piksel cinsinden uzaklığını buluyoruz.

    # Gözün yatay işaret noktaları arasındaki mesafeyi hesapla
    C = dist.euclidean(eye[0], eye[3])  #? eye[0] = Gözün sol köşesinin kordinatı  ve eye[3] = Gözün sağ köşesinin kordinatının arasındaki mesafeyide yine öklidyen formülü ile piksel cinsinden bulduk. 

    # EAR Formülü
    ear = (A + B) / (2.0 * C)  #? Sonra, gözün İki dikey mesafesini topluyoruz çünkü. Tek bir dikey mesafe üzerinden işlem yapmak istemiyoruz bunun nedeni bazen model 1,2 piksel yanlış oynamalar yapabilir böyle yaparsa aradaki göz açıklığı mesafesi doğru sonuç vermez. Biz garanti olsun diye iki dikey mesafeyi topluyoruz ki, olur da göz seğirmesi olur veya yanlış hesaplama olduğunda göz açıklığını kapalı sanmasın. Bu yüzden iki dikey mesafeyi aldık ve topladık.  
                               #? Sonra dikkat edersen 2.0 ile C'yi çarpmış. Aslında biz burada iki dikey mesafenin ortalamasını almak için  (A+B) / 2  yapıyoruz. Bu iki dikey mesafenin ortalamasını almak istememiz yukarıda anlattığım nedenden dolayı hata durumu olmasın daha kesin sonuç versin diye iki dikey mesafenin ortalamasını ikiye bölerek alıyoruz.Ama formüle dikkat edersen soldaki formül biraz farklı fakat dediğim formülle aslında aynı => (A+B/2)/C   ile   (A+B)/2*C  arasında hiç fark yok çünkü   (A+B)/2 /C  formülündeki 2 aşağıya gider çünkü onu 1/2 şeklinde düşün. Yani A+B,  1/2 ile çarpılıp C'ye bölünmüş yani C'de yukarı çıkar  A+B / 2*C olur. Yani 2 ile çarpılma nedeni tamamen A ve B'nin ortalamasının alınmasından dolayı  
                               #? Peki neden 2.0 ile çarptık 2 ile çarpmadık ? çünkü ikiye bölünce çıkan değer float olarak kalmaya devam etsin diye böyle yaptık. Hassas ölçüm için yani. 
                               #? Peki neden C 'ye böldük A ve B'nin ortalamasını ?  Çünkü şöyle düşün eğer kameraya yakın olsaydık göz açıklığımız örneğin 30 piksel gözükecekti ama kameradan uzaklaşınca göz açıklığım uzaklaştığım için 10 piksel olarak gözükecek.  Böyle bi durumda, program yanlış düşünerek, benim gözümü kıstığımı veya uykumun geldiğini düşünebilir. Fakat ben eğer, göz açıklığımın mesafesini gözümün yatay mesafesine oranlarsam şöyle olur,  Örneğin kameraya yakınken 30 piksel iken göz dikey açıklık mesafem, yan açıklık mesafem ise kameraya yakın olduğum için 60 piksel olsun. Yani, kameraya yakınken  Dikey mesafe'nin yatay mesafeye oranı => 30 / 60 = 1/2.  Eğer kameradan uzaklaşırsam dikey açıklık mesafesi diyelim ki  10 piksel olsun fakat kameradan uzaklaşınca yatay mesafemde kameradan uzaklaştığı için aynı oranda küçük çıkacak diyelim ki yatay mesafemde 20 piksel olacak yani kameradan uzaklaşınca dikey mesafenin yatay mesafeye oranı => 10 / 20 = 1/2 . Yani gözümün arasındaki mesafe açıklığı yaklaşsamda uzaklaşsamda aynı oldu gördün mü.
                               #? İşte yukarda açıkladığım nedenden dolayı yatay mesafeye bölüyoruz yani C'ye.   Yani, gözün açıklık oranını kameraya olan uzaklığımıza bağlı olarak değişmesin gözümüzü kapalı zannetmesin diye gözün yatay uzunluğuna bölüyoruz. Böylece   ear   değişkeni doğru bir mesafe tutacak. Bu mesafe fakat piksel veya inch veya santim gibi bir şey değil. Evet öklidyen mesafeleri piksle cinsindendi fakat bu oran piksel cinsinden bir uzunluk değil bu bir oran.  Dikey göz açıklığının / yatay göz açıklığına oranı.  Yani kolunun boyuna oranı gibi düşün. Santim veya piksel cinsinden değil, büyüklük cinsinden.

    return ear   #? Buradaki EAR kelimesinin "kulak" (ear) ile hiçbir ilgisi yok. Bu bir kısaltmadır: Eye (Göz),  Aspect (En-Boy), Ratio (Oranı).  Göz En-Boy Oranı anlamına gelir. Literatürde bu isimle geçtiği için fonksiyon adı genellikle böyle kurulur.



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("assets/shape_predictor_68_face_landmarks.dat")


use_video = False
if  use_video:
    cap = cv2.VideoCapture("sleep2.mp4")
else:
    cap = cv2.VideoCapture(0) 

while True:
    success, img = cap.read()
    
    if not success: 
        if use_video:
            print("Video bitti veya dosya bulunamadı.")
        break
    
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    isik_seviyesi = np.mean(imgGray)  #? # Görüntüdeki tüm piksellerin ortalama parlaklığını hesapla (0-255 arası)

    # Eğer ışık seviyesi 100'ün altındaysa (Ortam karanlıksa)
    if isik_seviyesi < 100: 
        # Karanlıkta yüz hatlarını belirginleştir (CLAHE)
        if isik_seviyesi < 50:  # Çok zifiri karanlıksa
            limit = 7.0
        else: # Orta karanlıksa
            limit = 3.0

        clahe = cv2.createCLAHE(clipLimit= limit, tileGridSize=(8, 8))  #? CLAHE (Contrast Limited Adaptive Histogram Equalization) Bu yöntem, görüntünün karanlık bölgelerindeki piksellerin parlaklığını dengeli bir şekilde artırır ve yüz hatlarını belirginleştirir. Sadece resmi düz bir şekilde aydınlatmaktan (ki bu çok fazla kumlama/noise yapar) çok daha zekice çalışır.  clipLimit: Kontrastın ne kadar artırılacağı (Genelde 2.0 veya 3.0 iyidir)   .  tileGridSize: Görüntüyü 8x8'lik karelere bölerek bölgesel aydınlatma yapar
        imgGray = clahe.apply(imgGray)
        cv2.putText(img, f"GECE MODU AKTIF, Aydinlatma {limit}", (10, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    else:
        # Ortam yeterince aydınlıksa hiçbir şey yapma, orijinal gri tonu kullan
        cv2.putText(img, "AYDINLIK MOD", (10, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        

    faces = detector(imgGray)

    for face in faces:  # kameradaki yüzleri buldu
        landmarks = predictor(imgGray, face) 
        myPoints = []
        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            myPoints.append((x, y))  # yüzdeki landmarkları myPoints içinde tuttu

        # Sol Göz (36-41) ve Sağ Göz (42-47) noktaları. Dikkat et ikisinde de toplam 6 nokta var. 36,37,38,39,40,41  noktaları. Ve 42 dahil, 48 dahil olmayan arası noktalar.
        leftEye = np.array(myPoints[36:42])  #? Önce tabiki iki göz kordinatınıda numpy arraye çevirmek zorundasın çünkü kural bu.
        rightEye = np.array(myPoints[42:48])
        

        leftEAR = calculate_ear(leftEye)  #? yukarıda bizim yazdığımız calculate_ear() fonksiyonuna önce sol gözü çevreleyen noktaların kordinatlarını yolladık ve sonucu leftEar'a aldık. Sonra ise aynısını sağ göz içinde yaptık.
        rightEAR = calculate_ear(rightEye)  #? Sol göz için ear bulduk oran bulduk sonra ise sağ göz için bulduk.  eye[1], eye[2]  gibi şeyler sağ ve sol göz içinde aynı yerleri tutar merak etme. Yani eye[1] hep gözün sol üst köşesini tutar eğer sol göz kordinatını verirsen sol gözün üst köşesini tutar eğer sağ göz kordinat verirsen sağ gözün üst köşesini tutar çünkü sol ve sağ göz ikiside 6 kordinatlı noktadan oluşuyor ve her ikisinin noktalarıda aynı şekilde gözü çevreliyor. Bu yüzden, yanlışlık olmaz merak etme.
        
        # İki gözün ortalamasını al
        ear = (leftEAR + rightEAR) / 2.0  #?  Neden Sol ve Sağ Gözü Ayrı Hesaplayıp Ortalamasını Alıyoruz?  Hata Payını Azaltmak: Bazen kamera açısı yüzünden bir gözümüz diğerinden daha küçük görünebilir veya bir gözümüzün üzerine gölge düşebilir. İki gözün ortalamasını almak, tek bir gözdeki anlık veri bozulmalarının (titreme veya yanlış okuma) sistemi yanıltmasını engeller. Doğal Hareketler: İnsanlar bazen tek gözünü kısabilir veya göz kırpma hızı iki gözde milisaniyelik farklar gösterebilir. İkisini toplayıp ikiye bölerek ($(left + right) / 2$) daha dengeli ve "kararlı" bir EAR değeri elde ederiz. Eğer değer çok düşükse, bu iki gözün de kapandığına dair çok daha güçlü bir kanıttır. 

        # Gözleri ekranda çizerek takip et (Opsiyonel)
        cv2.polylines(img, [leftEye], True, (0, 255, 0), 1)  #? bir dizi noktayı birbirine bağlayarak bir çokgen (şekil) çizmemizi sağlar. Gözlerin etrafına bir çerçeve çizmek için kullanıyoruz. Detaylar opencv notlarda
        cv2.polylines(img, [rightEye], True, (0, 255, 0), 1)


        # Uyku Kontrolü.
        if ear < EAR_THRESHOLD:  #?  Eğer tespit ettiğmiz ear değişkeni, yukarıda verdiğim EAR_Threshold'dan küçükse sayaç başlıyor yani her frame'de counter bir artacak
            COUNTER += 1
            if COUNTER >= CONSEC_FRAMES:  #? Eğer Consec_Frames değerini geçerse bu sefer uyarı yazacak.
                cv2.putText(img, "UYARI: UYUYORSUN!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                #winsound.Beep(2500, 500) #? # Biip sesi çıkar (2500 Hz frekansında, 500 ms süreyle)
                
                if not ALARM_ON:  #? Eğer alarm_on değeri false ise mp3 sesi sonsuza kadar çalıştıracak ve alarm_on'u true yapacak bu sayede else kısmına girdiğinde alarm durdurulacak.
                    eye_alarm.play(-1) # Sonsuz döngüde çal
                    ALARM_ON = True

        else:
            COUNTER = 0  #? Eğer counter consec_frames değerini geçmeden göz açılırsa counter sıfırlanacak.

            if ALARM_ON:  #? Eğer yukarıda 
                eye_alarm.stop()
                ALARM_ON = False



        #ESNEME HESAPLAMA
        innerMouth = np.array(myPoints[60:68]) # Önce numpy array çevirdik
        mar = calculate_mar(innerMouth) # Ağız için mar bulucak.

        if mar > MAR_THRESHOLD:  #?  Ağız Açıldı: mar değeri, MAR_THRESHOLD'dan yüksek bu yüzden if bloğu çalışıyor. yawn_counter artıyor. 
            YAWN_COUNTER += 1
            cv2.fillPoly(img, [innerMouth], (0,0,255))

            if YAWN_COUNTER >= YAWN_FRAMES and not is_yawning:  #? Sonra ağız açıkken YAWN_FRAMES kadar sürede ve fazlası geçtiği için  ve ayrıca programın başında yukarıda default olarak is_yawning = False demiştik.  Burada   not False => True demek olduğu için soldaki if içine girecek.  
                #total_yawns += 1                        #? if içine girince solda total_yawns 1 kere artacak ve altında  is_yawning=True olacak ve print yazısı yazacak sonra tekrar aynı if koşuluna gelecek ağız hala açık olsa bile bu sefer if koşuluna girmicek çünkü  is_yawning=True demiştik  ve  not True => False olacağı için if'in sağ tarafı false olacak ve bu yüzden if içine giremicek. 
                right_now = time.time()  
                YAWN_CLOCKS.append(right_now)

                YAWN_CLOCKS = [t for t in YAWN_CLOCKS if right_now - t < TIME_LIMIT]
                
                
                                                        #? Yani bu sayede sadece total_yawns,  1 kere artmış olacak. Yani her esnediğinde sadece 1 kere artmış oluyor bu sayede. Sonra adam ağzı açık olsa bile bu if koşuluna girmicek ama adam ağzını kapattığı anda  mar < MAR_THRESHOLD olacağı için else durumuna gidiyor.  Biz az önce is_yawning = True yapmıştık fakat bu else durumunda tekrar False yapıyoruz böylece. Eğer olurda adam tekrar esnemeye kalkarsa ağzı thresholddan fazla açılmışsa ve belli sürenin üstünde ağzı açık kalmışsa  is_yawning = False  olduğu için    not False => True   yapacağı için  tekrar if içine girip tekrar esneme sayısını 1 daha arttıracak ve yine total_yawns sayısı 1'den fazla artmıcak ve is_yawning = True olacağı için tekrar if içine girmicek. Yani günün sonunda her esnediğinde esnemesini bir kere sayıyoruz doğru işlem yapıyoruz.
                print(f"Toplam Esneme: {len(YAWN_CLOCKS)}")  #? YAWN_COUNTER ile aklın karışmasın bu sadece geçen süreyi (yani aslında frame'i) tutuyordu ve ağzını kapattığında da bu süreyi sıfırlıyorduk else durumunda.
                is_yawning = True
                yawn_alarm = False
        else:
            YAWN_COUNTER = 0
            is_yawning = False



        total_yawn = len(YAWN_CLOCKS)        

        # ESNEME UYARISI
        if total_yawn >= YAWN_LIMIT and  total_yawn % 2 == 0:  #? Eğer adam 4 kere esneme yaparsa uyarı mesajı verecek.

            if not yawn_alarm:
                yawn_warning_1.play()
                yawn_alarm = True

                yazi_bitis_zamani = time.time() + 3

        if time.time() < yazi_bitis_zamani:
            cv2.putText(img, "COK ESNIYORSUN: DINLENMELISIN!", (10, 420),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)




        # --- DİKKAT DAĞINIKLIĞI KONTROLÜ (HEAD POSE) ---

        nose = myPoints[30]           #? Burnun ucu
        left_eye_out = myPoints[36]   #? Karşıdan baktığımızda sol gözün sol üst köşesi
        right_eye_out = myPoints[45]  #? Karşıdan baktığımızda sağ gözün sağ üst köşesi
        chin = myPoints[8]            #? tam ortadaki çene altı kordinatları

        dist_left  = abs(left_eye_out[0] - nose[0])
        dist_right = abs(right_eye_out[0] - nose[0])
        is_distracted = False

        yatay_oran = dist_left / dist_right if dist_right != 0 else 0

        if yatay_oran > 2.5 or yatay_oran < 0.4:
            is_distracted = True

        eye_y_avg = (left_eye_out[1] + right_eye_out[1]) / 2.0 
        upper_dist = abs(eye_y_avg - nose[1])
        lower_dist = abs(chin[1] - nose[1])

        dikey_oran = upper_dist / lower_dist if lower_dist != 0 else 0

        if dikey_oran > 0.4:
            is_distracted = True

        # Uyarı Sistemi
        if is_distracted:
            DISTRACT_COUNTER += 1  

            if DISTRACT_COUNTER > DISTRACT_FRAMES:
                cv2.putText(img, "YOLA ODAKLAN", (10, 150), 
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0,165,255), 3)

                if not distract_alarm:    
                    distract_warning.play()
                    distract_alarm = True
        else:
            DISTRACT_COUNTER = 0
            distract_alarm = False





        # --- EKRAN YAZILARI ---

        cv2.putText(img, f"EAR: {round(ear,2)}", (500, 30),   #?  round(sayı, basamak_sayısı) =>  ear: Yuvarlamak istediğimiz değişken (bizim oranımız).  2: Virgülden sonra kaç basamak kalacağını belirler. 2 yazdığımız için sonuç 0.25, 0.31 gibi kısa ve okunabilir olur.   Ekranda bir köşede sürekli ear ve mar değerleri gözükecek.
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        cv2.putText(img, f"MAR: {round(mar,2)}", (500, 50),   #?  round(sayı, basamak_sayısı) =>  ear: Yuvarlamak istediğimiz değişken (bizim oranımız).  2: Virgülden sonra kaç basamak kalacağını belirler. 2 yazdığımız için sonuç 0.25, 0.31 gibi kısa ve okunabilir olur.   Ekranda bir köşede sürekli ear ve mar değerleri gözükecek.
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        cv2.putText(img, f"Esneme sayisi: {total_yawn}", (420, 70),   #?  round(sayı, basamak_sayısı) =>  ear: Yuvarlamak istediğimiz değişken (bizim oranımız).  2: Virgülden sonra kaç basamak kalacağını belirler. 2 yazdığımız için sonuç 0.25, 0.31 gibi kısa ve okunabilir olur.   Ekranda bir köşede sürekli ear ve mar değerleri gözükecek.
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.putText(img, f"Yatay Oran: {round(yatay_oran, 2)}", (420, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(img, f"Dikey Oran: {round(dikey_oran, 2)}", (420, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow("Yorgunluk Tespit Sistemi", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):  #? waitKey(33) yaklaşık 30 fps yapıyor. Yani saniyede 30 frame olur yani 30 kez başa döner while 1 saniye içinde, eğer gözünü kapatırsan 2 saniyede 60 frame olacağı için uyarı verir. Yani waitkey(33) yaparsan ve consec_frames = 60 değeri olursa iki saniye sonunda uyarı verir. Ama waitKey(1) olursa bilgisayarın gücü en yüksek hızda çalışır eğer bilgisayar güçlüyse 100 kare işler bu durumda 60 kare sadece 0.6 salise eder. Daha göz kırpmadan bile çalabilir. Waitkey ile böyle bir ilişkisi var consec_frames değişkeninin.                               
        break                               #? Fakat şunuda düşün waitkey(33) yapsanda saniye 30 fps demekti yani 30 frame'di fakat cpu farklı davranabilir veya yukarıda hesaplamalar var bunlarda vakit olabilir bu yüzden 60 frame 2 saniyeden uzun sürebilir. Bu durumda fazla gelirse süre düşürmen lazım consec_frames değerini.

cap.release()
cv2.destroyAllWindows() 






    

        