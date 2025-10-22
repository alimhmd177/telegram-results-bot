# 🤖 بوت تليجرام لمراقبة صفحة النتائج

بوت تليجرام ذكي يراقب صفحة نتائج الطلاب تلقائياً ويرسل إشعارات فورية عندما تصبح متاحة.

## ✨ المميزات

- ✅ مراقبة تلقائية 24/7
- ✅ إشعارات فورية على تليجرام
- ✅ لا يحتاج هاتفك مفتوحاً
- ✅ سهل الاستخدام
- ✅ يدعم عدة مستخدمين
- ✅ مجاني تماماً

---

## 🚀 النشر على Railway (الطريقة الأسهل)

### الخطوة 1: إنشاء البوت على تليجرام

1. افتح تليجرام وابحث عن: **@BotFather**
2. أرسل: `/newbot`
3. اختر اسماً للبوت (مثل: مراقب النتائج)
4. اختر اسم مستخدم ينتهي بـ `bot` (مثل: `my_results_bot`)
5. **احفظ التوكن** الذي سيرسله لك

### الخطوة 2: رفع الكود إلى GitHub

#### الطريقة الأولى: باستخدام GitHub Desktop

1. حمّل [GitHub Desktop](https://desktop.github.com/)
2. سجّل دخول بحسابك على GitHub
3. اضغط **File** → **New Repository**
4. سمّه: `telegram-results-bot`
5. اضغط **Create Repository**
6. اضغط **Show in Explorer** (Windows) أو **Show in Finder** (Mac)
7. انسخ جميع الملفات من مجلد `telegram-bot-deploy` إلى المجلد الذي فتح
8. ارجع إلى GitHub Desktop
9. اكتب رسالة في خانة **Summary**: `Initial commit`
10. اضغط **Commit to main**
11. اضغط **Publish repository**
12. تأكد من إلغاء تحديد **Keep this code private** إذا كنت تريد المستودع عاماً
13. اضغط **Publish Repository**

#### الطريقة الثانية: باستخدام سطر الأوامر

```bash
# انتقل إلى مجلد المشروع
cd telegram-bot-deploy

# ابدأ Git
git init

# أضف الملفات
git add .

# أنشئ commit
git commit -m "Initial commit"

# أنشئ مستودعاً على GitHub من الموقع
# ثم اربطه وارفع الكود
git remote add origin https://github.com/YOUR_USERNAME/telegram-results-bot.git
git branch -M main
git push -u origin main
```

#### الطريقة الثالثة: رفع مباشر على GitHub

1. اذهب إلى https://github.com/new
2. سمّ المستودع: `telegram-results-bot`
3. اضغط **Create repository**
4. اضغط **uploading an existing file**
5. اسحب جميع الملفات من مجلد `telegram-bot-deploy`
6. اضغط **Commit changes**

### الخطوة 3: النشر على Railway

1. اذهب إلى https://railway.app
2. اضغط **Start a New Project**
3. اختر **Deploy from GitHub repo**
4. سجّل دخول بحساب GitHub
5. اختر المستودع `telegram-results-bot`
6. بعد أن يبدأ النشر، اضغط على المشروع
7. اذهب إلى **Variables**
8. أضف متغير جديد:
   - **Key**: `BOT_TOKEN`
   - **Value**: التوكن الذي حصلت عليه من @BotFather
9. اضغط **Add**
10. سيعيد Railway تشغيل البوت تلقائياً

### الخطوة 4: استخدام البوت

1. افتح تليجرام
2. ابحث عن البوت (بالاسم الذي اخترته)
3. اضغط **Start**
4. أرسل: `/monitor`
5. انتظر الإشعار! 🎉

---

## 🌐 طرق نشر بديلة

### Heroku

1. سجّل في https://heroku.com
2. أنشئ تطبيقاً جديداً
3. اربطه بمستودع GitHub
4. أضف `BOT_TOKEN` في **Config Vars**
5. انشر التطبيق

### Render

1. سجّل في https://render.com
2. أنشئ **Web Service** جديد
3. اربطه بمستودع GitHub
4. أضف `BOT_TOKEN` في **Environment Variables**
5. انشر الخدمة

### PythonAnywhere

1. سجّل في https://www.pythonanywhere.com
2. ارفع الملفات
3. ثبّت المكتبات: `pip install -r requirements.txt`
4. أضف `BOT_TOKEN` في ملف `.env`
5. شغّل: `python bot.py`

---

## 📱 الأوامر المتاحة

| الأمر | الوظيفة |
|-------|---------|
| `/start` | عرض رسالة الترحيب |
| `/monitor` | بدء المراقبة 🔔 |
| `/stop` | إيقاف المراقبة |
| `/status` | فحص الحالة الحالية |
| `/stats` | عرض الإحصائيات |

---

## ⚙️ الإعدادات المتقدمة

يمكنك تخصيص البوت عبر متغيرات البيئة:

| المتغير | الوصف | الافتراضي |
|---------|--------|-----------|
| `BOT_TOKEN` | توكن البوت من @BotFather | **مطلوب** |
| `TARGET_URL` | الرابط المراقب | `http://212.0.143.242/portal/students/index.php` |
| `CHECK_INTERVAL` | فترة الفحص (بالثواني) | `30` |
| `TIMEOUT` | مهلة الاتصال (بالثواني) | `10` |

---

## 🔧 استكشاف الأخطاء

### البوت لا يستجيب

- تأكد من صحة `BOT_TOKEN`
- تحقق من السجلات (Logs) في Railway
- أعد تشغيل البوت

### لا تصل الإشعارات

- تأكد من إرسال `/monitor`
- تحقق من أن البوت يعمل
- تأكد من تفعيل الإشعارات في تليجرام

---

## 📄 الترخيص

هذا المشروع مفتوح المصدر ومتاح للاستخدام الحر.

---

## 💡 الدعم

إذا واجهت أي مشاكل، تحقق من:
- السجلات (Logs) في منصة الاستضافة
- صحة التوكن
- الاتصال بالإنترنت

---

**تم التطوير بواسطة Manus AI** 🚀

