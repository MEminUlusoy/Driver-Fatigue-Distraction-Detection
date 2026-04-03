# Driver Fatigue & Distraction Detection (DMS) 🚗

## 🎯 Proje Hakkında

Bu proje; **bilgisayarlı görü (Computer Vision)** tekniklerini kullanarak sürücü davranışlarını analiz eden bir **Sürücü İzleme Sistemi (DMS)** projesidir. 

Sistem, aşağıdaki durumları gerçek zamanlı olarak tespit ederek sürücüye anlık **sesli ve yazılı uyarılar** gönderir:

* **Yorgunluk:** Esneme sıklığı ve süresine dayalı analiz.
* **Uyku:** Göz kapaklarının kapalılık oranının (EAR) takibi.
* **Dikkat Dağınıklığı:** Baş pozisyonunun yoldan sapma miktarının ölçümü.

Sistem, sürücünün biyometrik verilerini anlık olarak işleyerek güvenli sürüşü desteklemek amacıyla geliştirilmiştir.

---

## 🛠️ Teknik Yetkinlikler

| Teknoloji | Kullanım Amacı |
| :--- | :--- |
| **Python**  | Ana Programlama Dili |
| **OpenCV** | Görüntü İşleme, Video Akışı ve CLAHE Analizi |
| **Dlib** | 68 Noktalı Yüz Landmark (Nirengi Noktası) Tespiti |
| **SciPy** | Öklid Mesafesi ve Matematiksel Oran Hesaplamaları |
| **Pygame** | Düşük Gecikmeli Sesli Uyarı Yönetimi |



## 🚀 Öne Çıkan Özellikler

### 1. Dinamik Yorgunluk Takibi (Fatigue Tracking)
* **MAR (Mouth Aspect Ratio):** Ağız açıklığı üzerinden hassas esneme tespiti yapılır.
* **10 Dakikalık Akıllı Analiz:** Sistem, son 10 dakika içindeki esneme sıklığınızı sürekli takip eder. 
* **Kademeli Uyarı Sistemi:** 10 dakika içinde 4. esnemeye ulaşıldığında "Lütfen dinlenin" uyarısı tetiklenir. Sonraki her esnemede uyarı sayısı artırılarak sürücünün dikkati aktif tutulur.

### 2. Uyku Tespiti (Drowsiness)
* **EAR (Eye Aspect Ratio):** Göz kapaklarının kapalılık oranı milisaniyelik hassasiyetle hesaplanır.
* Belirlenen eşik değerinin altında kalındığında (gözler kapandığında) anında sesli ve görsel alarm verilerek olası kazaların önüne geçilmesi hedeflenir.

### 3. Dikkat Dağınıklığı Analizi (Distraction)
* **Head Pose Estimation:** Sürücünün kafa pozisyonu (sağa, sola veya aşağı/telefona bakma durumları) analiz edilir.
* **Yola Odaklanma Kontrolü:** Sürücü yoldan başka bir yöne uzun süre baktığında sistem bunu "Dikkat Dağınıklığı" olarak algılar ve "Yola Odaklan" uyarısı verir.

### 4. Adaptif Gece ve Aydınlık Modları
* **Parlaklık Ölçümü:** Görüntüdeki ortalama parlaklık değeri sürekli ölçülerek ortam ışığı analiz edilir.
* **CLAHE Algoritması:** Düşük ışık koşullarında sistem otomatik olarak "Gece Modu" kontrast ayarlarını (CLAHE) devreye sokar. Bu sayede zifiri karanlıkta bile yüz nirengi noktalarının (landmarks) tespiti kesintisiz devam eder ve sistemin her türlü ışık koşulunda doğru çalışması sağlanır.

---

