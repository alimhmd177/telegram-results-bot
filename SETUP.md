# دليل التثبيت والإعداد

هذا الدليل يشرح بالتفصيل كيفية تثبيت وإعداد بوت نتائج طلاب جامعة البحر الأحمر على خادمك أو جهازك الشخصي.

## المتطلبات الأساسية

قبل البدء، تأكد من توفر المتطلبات التالية:

- نظام تشغيل Linux أو macOS أو Windows
- Python 3.8 أو أحدث
- Google Chrome أو Chromium
- اتصال بالإنترنت

## خطوات التثبيت

### 1. تثبيت Python

تأكد من أن Python 3.8 أو أحدث مثبت على نظامك. يمكنك التحقق من ذلك بتشغيل الأمر التالي:

```bash
python3 --version
```

إذا لم يكن Python مثبتاً، قم بتنزيله وتثبيته من الموقع الرسمي: https://www.python.org/downloads/

### 2. تنزيل المشروع

قم بتنزيل ملفات المشروع من GitHub أو استنساخ المستودع:

```bash
git clone https://github.com/yourusername/telegram-student-bot.git
cd telegram-student-bot
```

أو قم بتنزيل الملفات مباشرة وفك ضغطها.

### 3. إنشاء بيئة افتراضية (اختياري ولكن موصى به)

يُنصح بإنشاء بيئة افتراضية لعزل مكتبات المشروع:

```bash
python3 -m venv venv
source venv/bin/activate  # على Linux/macOS
# أو
venv\Scripts\activate  # على Windows
```

### 4. تثبيت المكتبات المطلوبة

قم بتثبيت جميع المكتبات المطلوبة باستخدام pip:

```bash
pip install -r requirements.txt
```

### 5. تثبيت Google Chrome و ChromeDriver

البوت يستخدم Selenium مع Chrome للتفاعل مع موقع الجامعة.

**على Ubuntu/Debian:**

```bash
# تثبيت Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# تثبيت ChromeDriver
sudo apt-get install chromium-chromedriver
```

**على macOS:**

```bash
brew install --cask google-chrome
brew install chromedriver
```

**على Windows:**

قم بتنزيل Chrome من: https://www.google.com/chrome/
وتنزيل ChromeDriver من: https://chromedriver.chromium.org/

### 6. إنشاء بوت تلغرام

1. افتح تطبيق تلغرام وابحث عن `@BotFather`
2. ابدأ محادثة معه وأرسل الأمر `/newbot`
3. اتبع التعليمات لإعطاء اسم واسم مستخدم لبوتك
4. سيمنحك BotFather توكناً فريداً، احتفظ به بشكل آمن

### 7. تعيين توكن البوت

قم بتعيين توكن البوت كمتغير بيئة:

**على Linux/macOS:**

```bash
export TELEGRAM_BOT_TOKEN="Your-Bot-Token-Here"
```

**على Windows (PowerShell):**

```powershell
$env:TELEGRAM_BOT_TOKEN="Your-Bot-Token-Here"
```

**أو يمكنك إنشاء ملف `.env`:**

```bash
echo "TELEGRAM_BOT_TOKEN=Your-Bot-Token-Here" > .env
```

ثم قم بتحديث ملف `bot.py` لقراءة المتغيرات من ملف `.env` باستخدام مكتبة `python-dotenv`.

## تشغيل البوت

بعد إكمال جميع الخطوات السابقة، قم بتشغيل البوت:

```bash
python bot.py
```

إذا كان كل شيء على ما يرام، سترى رسالة تفيد بأن البوت قد بدأ التشغيل.

## اختبار البوت

1. افتح تطبيق تلغرام
2. ابحث عن اسم مستخدم البوت الذي أنشأته
3. ابدأ محادثة معه وأرسل `/start`
4. اتبع التعليمات لإدخال رقمك الجامعي

## استكشاف الأخطاء

### المشكلة: "chromedriver not found"

**الحل:** تأكد من أن ChromeDriver مثبت وموجود في PATH. يمكنك تحديد المسار مباشرة في `scraper_selenium.py`.

### المشكلة: "TELEGRAM_BOT_TOKEN not found"

**الحل:** تأكد من أنك قمت بتعيين متغير البيئة بشكل صحيح قبل تشغيل البوت.

### المشكلة: البوت لا يستجيب

**الحل:** تحقق من سجلات البوت للبحث عن أخطاء. تأكد من أن التوكن صحيح وأن البوت يعمل.

## تشغيل البوت كخدمة (للخوادم)

لتشغيل البوت بشكل دائم على خادم، يمكنك استخدام `systemd` أو `supervisor` أو `screen`.

**مثال باستخدام screen:**

```bash
screen -S telegram-bot
python bot.py
# اضغط Ctrl+A ثم D للخروج من الجلسة
```

للعودة إلى الجلسة:

```bash
screen -r telegram-bot
```

## الأمان

- **لا تشارك توكن البوت** مع أي شخص
- احتفظ بملف `.env` أو متغيرات البيئة آمنة
- لا ترفع التوكن إلى GitHub أو أي مستودع عام

## الدعم

إذا واجهت أي مشاكل، يمكنك:
- فتح issue على GitHub
- مراجعة الوثائق الرسمية لـ python-telegram-bot
- التحقق من سجلات الأخطاء في الكونسول

