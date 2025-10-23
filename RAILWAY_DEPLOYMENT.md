# دليل النشر على Railway

هذا الدليل يشرح كيفية نشر بوت التلغرام على منصة Railway خطوة بخطوة.

## المتطلبات

قبل البدء، تأكد من أن لديك:

1. حساب على [Railway.app](https://railway.app)
2. حساب على [GitHub](https://github.com) (اختياري ولكن موصى به)
3. توكن بوت التلغرام من @BotFather

## الطريقة الأولى: النشر من GitHub (موصى بها)

### الخطوة 1: رفع المشروع إلى GitHub

قم برفع ملفات المشروع إلى مستودع GitHub جديد:

```bash
cd telegram-student-bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/telegram-student-bot.git
git push -u origin main
```

### الخطوة 2: إنشاء مشروع جديد على Railway

1. افتح [Railway.app](https://railway.app) وسجل الدخول
2. اضغط على "New Project"
3. اختر "Deploy from GitHub repo"
4. اختر المستودع الذي رفعت عليه المشروع
5. انتظر حتى يتم اكتشاف المشروع تلقائياً

### الخطوة 3: إضافة متغيرات البيئة

1. في لوحة تحكم Railway، اذهب إلى تبويب "Variables"
2. أضف المتغير التالي:
   - **Key**: `TELEGRAM_BOT_TOKEN`
   - **Value**: التوكن الذي حصلت عليه من @BotFather

### الخطوة 4: النشر

1. Railway سيبدأ النشر تلقائياً
2. انتظر حتى يكتمل النشر (عادة يستغرق 2-5 دقائق)
3. تحقق من السجلات للتأكد من أن البوت يعمل بشكل صحيح

## الطريقة الثانية: النشر المباشر من CLI

### الخطوة 1: تثبيت Railway CLI

```bash
npm install -g @railway/cli
```

أو باستخدام Homebrew على macOS:

```bash
brew install railway
```

### الخطوة 2: تسجيل الدخول

```bash
railway login
```

### الخطوة 3: إنشاء مشروع جديد

```bash
cd telegram-student-bot
railway init
```

### الخطوة 4: إضافة متغيرات البيئة

```bash
railway variables set TELEGRAM_BOT_TOKEN="your-bot-token-here"
```

### الخطوة 5: النشر

```bash
railway up
```

## التحقق من عمل البوت

بعد النشر، يمكنك التحقق من عمل البوت:

1. افتح تطبيق تلغرام
2. ابحث عن اسم مستخدم البوت
3. أرسل `/start`
4. أرسل رقماً جامعياً للاختبار

## عرض السجلات

لعرض سجلات البوت على Railway:

1. في لوحة التحكم، اذهب إلى تبويب "Deployments"
2. اضغط على آخر نشر
3. اضغط على "View Logs"

أو باستخدام CLI:

```bash
railway logs
```

## استكشاف الأخطاء

### المشكلة: البوت لا يعمل بعد النشر

**الحل:**
- تحقق من السجلات للبحث عن أخطاء
- تأكد من أن `TELEGRAM_BOT_TOKEN` تم تعيينه بشكل صحيح
- تأكد من أن جميع الملفات المطلوبة موجودة في المستودع

### المشكلة: خطأ في Selenium/ChromeDriver

**الحل:**
- تأكد من أن ملف `nixpacks.toml` موجود ويحتوي على `chromium` و `chromedriver`
- قد تحتاج إلى إضافة المزيد من الخيارات في `scraper_selenium.py`

### المشكلة: البوت يتوقف بعد فترة

**الحل:**
- Railway يوفر خطة مجانية محدودة، قد تحتاج إلى الترقية للحصول على وقت تشغيل أطول
- تأكد من أن البوت لا يستهلك موارد كثيرة

## الترقية والصيانة

### تحديث البوت

إذا قمت بتحديث الكود:

**باستخدام GitHub:**
```bash
git add .
git commit -m "Update bot"
git push
```
Railway سيقوم بالنشر تلقائياً.

**باستخدام CLI:**
```bash
railway up
```

### مراقبة الأداء

يمكنك مراقبة استخدام الموارد من لوحة تحكم Railway في تبويب "Metrics".

## الملاحظات المهمة

- Railway يوفر خطة مجانية محدودة (500 ساعة شهرياً)
- البوت سيعمل 24/7 طالما لديك رصيد كافٍ
- تأكد من عدم مشاركة توكن البوت مع أي شخص
- احتفظ بنسخة احتياطية من الكود

## الدعم

إذا واجهت أي مشاكل:
- راجع [وثائق Railway](https://docs.railway.app)
- راجع [وثائق python-telegram-bot](https://docs.python-telegram-bot.org)
- تحقق من السجلات للبحث عن أخطاء مفصلة

