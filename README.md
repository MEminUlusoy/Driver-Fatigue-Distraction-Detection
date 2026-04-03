# Driver Fatigue and Distraction Detection (DMS) 🚗💤

Bu proje, bilgisayarlı görü (Computer Vision) ve derin öğrenme tabanlı yüz nirengi noktaları (Facial Landmarks) tekniklerini kullanarak sürücü güvenliğini en üst düzeye çıkarmayı hedefleyen bir **Sürücü İzleme Sistemi (Driver Monitoring System - DMS)** yazılımıdır.

Sistem; uykusuzluk, yorgunluk ve dikkat dağınıklığı gibi kritik risk faktörlerini gerçek zamanlı olarak analiz eder ve hiyerarşik bir uyarı mekanizması ile sürücüyü hem görsel hem de sesli olarak uyarır.

---

## ✨ Öne Çıkan Özellikler

### 1. Uyku Tespiti (Drowsiness Detection)
* **EAR (Eye Aspect Ratio):** Gözlerin dikey ve yatay açıklık oranları milisaniyelik hassasiyetle hesaplanır.
* **Akıllı Sayaç:** Gözlerin belirli bir kare (frame) sayısı boyunca kapalı kalması durumunda sistem "UYKU" durumunu saptar.
* **Yüksek Öncelik:** Uyku durumu saptandığı an diğer tüm uyarılar susturulur ve en yüksek seviyeli alarm devreye girer.

### 2. Yorgunluk ve Esneme Analizi (Fatigue Analysis)
* **MAR (Mouth Aspect Ratio):** Ağız içindeki nirengi noktaları üzerinden esneme tespiti yapılır.
* **Zaman Bazlı Takip:** 10 dakika (600 saniye) içerisinde 4 veya daha fazla kez esneme yapıldığında sistem sürücüye "Dinlenmelisiniz" uyarısı verir.
* **İlerleyici Uyarı Sistemi:** Esneme sayısı arttıkça uyarıların sıklığı ve şiddeti dinamik olarak güncellenir.

### 3. Dikkat Dağınıklığı ve Baş Pozisyonu (Distraction Detection)
* **Head Pose Estimation:** Sürücünün başının yatay (sağa/sola) ve dikey (aşağı/telefona bakma) açıları analiz edilir.
* **Yola Odaklanma Kontrolü:** Sürücü yoldan başka bir yöne (örneğin telefonuna veya yan koltuğa) uzun süre baktığında "YOLA ODAKLAN" uyarısı tetiklenir.

### 4. Adaptif Gece ve Aydınlık Modları
* **LDR Sensör Simülasyonu:** Görüntüdeki piksellerin ortalama parlaklığı anlık olarak ölçülür.
* **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Ortam karanlıklaştığında sistem otomatik olarak "Gece Modu"na geçer. Görüntü kontrastını bölgesel olarak artırarak zifiri karanlıkta bile yüz hatlarının (landmark) eksiksiz tespit edilmesini sağlar.

### 5. Hiyerarşik Uyarı Mekanizması
Sistem, birden fazla riskin aynı anda oluşması durumunda şu öncelik sırasına göre tepki verir:
1. **KRİTİK:** Uyku Alarmı (En yüksek ses ve kırmızı uyarı)
2. **YÜKSEK:** Esneme/Yorgunluk Uyarısı
3. **ORTA:** Dikkat Dağınıklığı Uyarısı

---

## 🛠️ Teknik Altyapı ve Kütüphaneler

* **Python 3.11:** Projenin çekirdek dili.
* **OpenCV:** Görüntü işleme, video akışı ve görsel uyarıların ekrana basılması.
* **Dlib (68 Landmarks):** Yüz tespiti ve nirengi noktalarının (göz, ağız, burun) koordinat hesaplamaları.
* **Pygame:** Düşük gecikmeli, gerçek zamanlı sesli uyarı sistemi.
* **SciPy:** Öklid mesafesi tabanlı geometrik oran hesaplamaları (EAR & MAR).
* **NumPy:** Matris operasyonları ve parlaklık analizi.


