# دليل النشر السريع على Railway ⚡

## الخطوات (5 دقائق فقط!)

### 1️⃣ إنشاء بوت تلغرام

- افتح تلغرام وابحث عن `@BotFather`
- أرسل `/newbot`
- اتبع التعليمات واحصل على التوكن

### 2️⃣ رفع المشروع إلى GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/telegram-student-bot.git
git push -u origin main
```

### 3️⃣ النشر على Railway

1. افتح [railway.app](https://railway.app)
2. سجل دخول بحساب GitHub
3. اضغط "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر مستودع `telegram-student-bot`

### 4️⃣ إضافة التوكن

1. في لوحة Railway، اذهب إلى "Variables"
2. أضف متغير جديد:
   - **Key**: `TELEGRAM_BOT_TOKEN`
   - **Value**: التوكن من BotFather

### 5️⃣ انتهى! 🎉

- انتظر 2-3 دقائق حتى يكتمل النشر
- افتح تلغرام وابحث عن بوتك
- أرسل `/start` وجرب البوت!

## استكشاف الأخطاء السريع

**البوت لا يعمل؟**
- تحقق من "Logs" في Railway
- تأكد من التوكن صحيح
- تأكد من وجود ملف `nixpacks.toml`

**خطأ في ChromeDriver؟**
- تأكد من وجود `chromium` في `nixpacks.toml`
- راجع السجلات للتفاصيل

## ملاحظات

- Railway مجاني لـ 500 ساعة/شهر
- البوت سيعمل 24/7
- لا تشارك التوكن مع أحد!

للمزيد من التفاصيل، راجع `RAILWAY_DEPLOYMENT.md`

