#!/usr/bin/env python3
"""
بوت تليجرام لمراقبة صفحة نتائج الطلاب وجلب النتائج
يرسل إشعارات فورية عندما تصبح الصفحة متاحة
يجلب نتيجة الطالب عند إدخال الرقم الجامعي
"""

import asyncio
import logging
import os
import re
from datetime import datetime
from typing import Set, Optional, Tuple
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات البوت - يتم قراءتها من متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_URL = os.getenv("TARGET_URL", "http://212.0.143.242/portal/students/index.php")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "123456")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# تسجيل الأحداث
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قائمة المستخدمين المشتركين في المراقبة
monitoring_users: Set[int] = set()
is_site_available = False
check_count = 0
monitoring_task = None


async def check_website() -> tuple[bool, str, float]:
    """
    فحص حالة الموقع
    Returns: (متاح؟, رسالة, وقت الاستجابة)
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(TARGET_URL, allow_redirects=True) as response:
                response_time = asyncio.get_event_loop().time() - start_time
                
                if response.status < 400:
                    return True, f"✅ الصفحة متاحة! (رمز الحالة: {response.status})", response_time
                else:
                    return False, f"❌ الخادم يستجيب لكن هناك خطأ (رمز: {response.status})", response_time
                    
    except asyncio.TimeoutError:
        response_time = asyncio.get_event_loop().time() - start_time
        return False, "⏱️ انتهت مهلة الاتصال - الخادم لا يستجيب", response_time
        
    except aiohttp.ClientError as e:
        response_time = asyncio.get_event_loop().time() - start_time
        return False, f"❌ خطأ في الاتصال: {type(e).__name__}", response_time
        
    except Exception as e:
        response_time = asyncio.get_event_loop().time() - start_time
        return False, f"❌ خطأ غير متوقع: {str(e)}", response_time


async def fetch_student_result(student_id: str, password: str = DEFAULT_PASSWORD) -> Tuple[bool, str]:
    """
    جلب نتيجة الطالب من الموقع
    Returns: (نجح؟, رسالة النتيجة أو رسالة الخطأ)
    """
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # محاولة تسجيل الدخول
            login_data = {
                'username': student_id,
                'password': password,
                'submit': 'دخول'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ar,en;q=0.9',
            }
            
            # إرسال طلب تسجيل الدخول
            async with session.post(TARGET_URL, data=login_data, headers=headers, allow_redirects=True) as response:
                if response.status != 200:
                    return False, f"❌ خطأ في الاتصال بالخادم (رمز: {response.status})"
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # التحقق من نجاح تسجيل الدخول
                # إذا كانت هناك رسالة خطأ في تسجيل الدخول
                error_messages = soup.find_all(string=re.compile(r'خطأ|غير صحيح|incorrect|error', re.IGNORECASE))
                if error_messages:
                    return False, "❌ الرقم الجامعي أو كلمة المرور غير صحيحة"
                
                # إذا عدنا إلى نفس صفحة تسجيل الدخول
                if 'الرقم الجامعي' in html and 'كلمة المرور' in html and len(html) < 10000:
                    return False, "❌ فشل تسجيل الدخول - تحقق من الرقم الجامعي"
                
                # محاولة استخراج النتائج
                result_text = await extract_results(soup, html)
                
                if result_text:
                    return True, result_text
                else:
                    # إذا لم نجد نتائج، نحاول البحث عن صفحة النتائج
                    results_link = soup.find('a', href=re.compile(r'result|نتيجة|نتائج', re.IGNORECASE))
                    if results_link:
                        results_url = results_link.get('href')
                        if not results_url.startswith('http'):
                            base_url = TARGET_URL.rsplit('/', 1)[0]
                            results_url = f"{base_url}/{results_url}"
                        
                        async with session.get(results_url, headers=headers) as results_response:
                            if results_response.status == 200:
                                results_html = await results_response.text()
                                results_soup = BeautifulSoup(results_html, 'html.parser')
                                result_text = await extract_results(results_soup, results_html)
                                if result_text:
                                    return True, result_text
                    
                    return False, "⚠️ تم تسجيل الدخول بنجاح لكن لم يتم العثور على نتائج.\nقد لا تكون النتائج متاحة بعد."
                    
    except asyncio.TimeoutError:
        return False, "⏱️ انتهت مهلة الاتصال - الخادم لا يستجيب"
    except aiohttp.ClientError as e:
        return False, f"❌ خطأ في الاتصال: {type(e).__name__}"
    except Exception as e:
        logger.error(f"خطأ في جلب النتيجة: {e}")
        return False, f"❌ حدث خطأ: {str(e)}"


async def extract_results(soup: BeautifulSoup, html: str) -> Optional[str]:
    """
    استخراج النتائج من صفحة HTML
    """
    # البحث عن جداول النتائج
    tables = soup.find_all('table')
    
    result_parts = []
    
    # البحث عن معلومات الطالب
    student_info = {}
    info_patterns = {
        'الاسم': r'(الاسم|Name)\s*:?\s*([^\n<]+)',
        'الرقم الجامعي': r'(الرقم الجامعي|Student ID)\s*:?\s*([^\n<]+)',
        'الكلية': r'(الكلية|Faculty|College)\s*:?\s*([^\n<]+)',
        'القسم': r'(القسم|Department)\s*:?\s*([^\n<]+)',
        'المستوى': r'(المستوى|Level|Year)\s*:?\s*([^\n<]+)',
    }
    
    for label, pattern in info_patterns.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            student_info[label] = match.group(2).strip()
    
    if student_info:
        result_parts.append("👤 *معلومات الطالب:*")
        for key, value in student_info.items():
            result_parts.append(f"• {key}: {value}")
        result_parts.append("")
    
    # استخراج النتائج من الجداول
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:  # جدول به بيانات
            # محاولة العثور على عناوين الأعمدة
            headers = []
            first_row = rows[0]
            header_cells = first_row.find_all(['th', 'td'])
            
            for cell in header_cells:
                text = cell.get_text(strip=True)
                if text and any(keyword in text for keyword in ['المادة', 'الدرجة', 'التقدير', 'Subject', 'Grade', 'Mark']):
                    headers.append(text)
            
            if headers and len(headers) >= 2:
                result_parts.append("📊 *النتائج:*")
                result_parts.append("")
                
                # استخراج صفوف البيانات
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        if any(row_data):  # تأكد من أن الصف ليس فارغاً
                            row_text = " | ".join(f"{h}: {d}" for h, d in zip(headers, row_data) if d)
                            if row_text:
                                result_parts.append(f"• {row_text}")
                
                result_parts.append("")
    
    # البحث عن المعدل التراكمي أو المجموع
    gpa_patterns = [
        r'(المعدل التراكمي|GPA|CGPA)\s*:?\s*([0-9.]+)',
        r'(المجموع|Total)\s*:?\s*([0-9.]+)',
        r'(النسبة المئوية|Percentage)\s*:?\s*([0-9.]+)%?',
    ]
    
    for pattern in gpa_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            result_parts.append(f"📈 *{match.group(1)}:* {match.group(2)}")
    
    if result_parts:
        return "\n".join(result_parts)
    
    return None


async def monitoring_loop(application: Application) -> None:
    """حلقة المراقبة الرئيسية"""
    global is_site_available, check_count
    
    logger.info("بدء حلقة المراقبة...")
    
    while True:
        try:
            if monitoring_users:
                check_count += 1
                available, message, response_time = await check_website()
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[{current_time}] الفحص #{check_count}: {message} ({response_time:.2f}s)")
                
                # إذا أصبحت الصفحة متاحة للتو
                if available and not is_site_available:
                    is_site_available = True
                    
                    notification = (
                        "🎉 *صفحة النتائج متاحة الآن!*\n\n"
                        f"✅ {message}\n"
                        f"⏱️ وقت الاستجابة: {response_time:.2f} ثانية\n"
                        f"🔗 الرابط: {TARGET_URL}\n\n"
                        f"📊 عدد المحاولات: {check_count}\n"
                        f"🕐 الوقت: {current_time}\n\n"
                        "💡 يمكنك الآن إرسال رقمك الجامعي للحصول على النتيجة!"
                    )
                    
                    # إرسال الإشعار لجميع المستخدمين المشتركين
                    for user_id in list(monitoring_users):
                        try:
                            await application.bot.send_message(
                                chat_id=user_id,
                                text=notification,
                                parse_mode='Markdown'
                            )
                            logger.info(f"تم إرسال إشعار للمستخدم {user_id}")
                        except Exception as e:
                            logger.error(f"فشل إرسال الإشعار للمستخدم {user_id}: {e}")
                
                # إذا أصبحت الصفحة غير متاحة بعد أن كانت متاحة
                elif not available and is_site_available:
                    is_site_available = False
                    logger.info("الصفحة أصبحت غير متاحة مرة أخرى")
            
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"خطأ في حلقة المراقبة: {e}")
            await asyncio.sleep(CHECK_INTERVAL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    welcome_message = (
        "👋 *مرحباً بك في بوت مراقبة صفحة النتائج!*\n\n"
        "🎯 *وظائف البوت:*\n\n"
        "1️⃣ *مراقبة الموقع:* يراقب صفحة النتائج ويرسل إشعاراً عندما تصبح متاحة\n"
        "2️⃣ *جلب النتيجة:* أرسل رقمك الجامعي للحصول على نتيجتك فوراً\n\n"
        "📋 *الأوامر المتاحة:*\n"
        "/start - عرض هذه الرسالة\n"
        "/monitor - بدء مراقبة الموقع\n"
        "/stop - إيقاف المراقبة\n"
        "/status - فحص حالة الموقع\n"
        "/stats - عرض الإحصائيات\n"
        "/help - المساعدة\n\n"
        f"🔗 *الرابط المراقب:*\n`{TARGET_URL}`\n\n"
        "💡 *للحصول على نتيجتك:*\n"
        "فقط أرسل رقمك الجامعي (مثال: 12345)"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help"""
    help_text = (
        "📖 *دليل الاستخدام*\n\n"
        "*🔍 للحصول على نتيجتك:*\n"
        "1. أرسل رقمك الجامعي فقط (مثال: 12345)\n"
        "2. سيقوم البوت بتسجيل الدخول تلقائياً\n"
        "3. ستحصل على نتيجتك خلال ثوانٍ\n\n"
        "*📡 لمراقبة الموقع:*\n"
        "1. أرسل /monitor لبدء المراقبة\n"
        "2. سيفحص البوت الموقع كل 30 ثانية\n"
        "3. ستتلقى إشعاراً فورياً عند توفر الموقع\n"
        "4. أرسل /stop لإيقاف المراقبة\n\n"
        "*ℹ️ ملاحظات:*\n"
        f"• كلمة المرور المستخدمة: {DEFAULT_PASSWORD}\n"
        "• البوت يعمل 24/7\n"
        "• يمكن لعدة مستخدمين استخدامه\n"
        "• آمن ولا يحفظ بياناتك"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /monitor - بدء المراقبة"""
    user_id = update.effective_user.id
    
    if user_id in monitoring_users:
        await update.message.reply_text(
            "✅ أنت مشترك بالفعل في المراقبة!\n"
            "سأخبرك فوراً عندما تصبح الصفحة متاحة. 🔔"
        )
    else:
        monitoring_users.add(user_id)
        
        # فحص فوري
        available, message, response_time = await check_website()
        
        if available:
            response = (
                "🎉 *الصفحة متاحة الآن!*\n\n"
                f"{message}\n"
                f"⏱️ وقت الاستجابة: {response_time:.2f} ثانية\n\n"
                f"🔗 يمكنك الوصول إليها الآن:\n{TARGET_URL}\n\n"
                "💡 أرسل رقمك الجامعي للحصول على نتيجتك!"
            )
        else:
            response = (
                "✅ *تم تفعيل المراقبة!*\n\n"
                f"الحالة الحالية: {message}\n"
                f"⏱️ وقت الاستجابة: {response_time:.2f} ثانية\n\n"
                f"🔔 سأرسل لك إشعاراً فورياً عندما تصبح الصفحة متاحة.\n"
                f"⏱️ الفحص كل {CHECK_INTERVAL} ثانية.\n\n"
                "استخدم /stop لإيقاف المراقبة."
            )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"المستخدم {user_id} بدأ المراقبة")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /stop - إيقاف المراقبة"""
    user_id = update.effective_user.id
    
    if user_id in monitoring_users:
        monitoring_users.remove(user_id)
        await update.message.reply_text(
            "🛑 *تم إيقاف المراقبة!*\n\n"
            "لن تتلقى إشعارات بعد الآن.\n"
            "استخدم /monitor لإعادة تفعيل المراقبة.",
            parse_mode='Markdown'
        )
        logger.info(f"المستخدم {user_id} أوقف المراقبة")
    else:
        await update.message.reply_text(
            "ℹ️ أنت لست مشتركاً في المراقبة حالياً.\n"
            "استخدم /monitor لبدء المراقبة."
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /status - عرض الحالة الحالية"""
    await update.message.reply_text("🔍 جاري فحص الموقع...")
    
    available, message, response_time = await check_website()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    status_icon = "🟢" if available else "🔴"
    status_text = "متاحة" if available else "غير متاحة"
    
    response = (
        f"{status_icon} *حالة الصفحة: {status_text}*\n\n"
        f"{message}\n"
        f"⏱️ وقت الاستجابة: {response_time:.2f} ثانية\n"
        f"🕐 وقت الفحص: {current_time}\n\n"
        f"🔗 الرابط:\n`{TARGET_URL}`"
    )
    
    if available:
        response += "\n\n💡 يمكنك إرسال رقمك الجامعي للحصول على نتيجتك!"
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /stats - عرض الإحصائيات"""
    user_id = update.effective_user.id
    is_monitoring = "نعم ✅" if user_id in monitoring_users else "لا ❌"
    site_status = "متاحة 🟢" if is_site_available else "غير متاحة 🔴"
    
    stats_message = (
        "📊 *إحصائيات البوت*\n\n"
        f"👥 عدد المستخدمين المشتركين: {len(monitoring_users)}\n"
        f"🔢 عدد الفحوصات: {check_count}\n"
        f"🌐 حالة الموقع: {site_status}\n"
        f"⏱️ فترة الفحص: {CHECK_INTERVAL} ثانية\n"
        f"📡 أنت مشترك في المراقبة: {is_monitoring}\n\n"
        f"🔗 الرابط المراقب:\n`{TARGET_URL}`"
    )
    
    await update.message.reply_text(stats_message, parse_mode='Markdown')


async def handle_student_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الرسائل النصية - للتعامل مع الرقم الجامعي"""
    text = update.message.text.strip()
    
    # التحقق من أن النص يحتوي على أرقام فقط أو أرقام مع أحرف (رقم جامعي)
    if re.match(r'^[a-zA-Z0-9]+$', text) and len(text) >= 3:
        # يبدو أنه رقم جامعي
        await update.message.reply_text(
            f"🔍 جاري البحث عن نتيجة الطالب: `{text}`\n"
            "⏳ الرجاء الانتظار...",
            parse_mode='Markdown'
        )
        
        # جلب النتيجة
        success, result = await fetch_student_result(text)
        
        if success:
            response = (
                f"✅ *تم العثور على النتيجة!*\n"
                f"🎓 الرقم الجامعي: `{text}`\n\n"
                f"{result}\n\n"
                f"🔗 الرابط: {TARGET_URL}"
            )
        else:
            response = (
                f"❌ *لم يتم العثور على النتيجة*\n"
                f"🎓 الرقم الجامعي: `{text}`\n\n"
                f"{result}\n\n"
                "💡 *تأكد من:*\n"
                "• صحة الرقم الجامعي\n"
                "• أن الموقع متاح\n"
                "• أن النتائج منشورة\n\n"
                "استخدم /status للتحقق من حالة الموقع"
            )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"تم طلب نتيجة للطالب {text} من المستخدم {update.effective_user.id}")
    else:
        # رسالة غير مفهومة
        await update.message.reply_text(
            "❓ لم أفهم رسالتك.\n\n"
            "💡 *للحصول على نتيجتك:*\n"
            "أرسل رقمك الجامعي فقط (مثال: 12345)\n\n"
            "📋 *للأوامر:*\n"
            "استخدم /help لعرض دليل الاستخدام"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")


async def post_init(application: Application) -> None:
    """يتم تنفيذه بعد تهيئة البوت"""
    global monitoring_task
    # بدء حلقة المراقبة في الخلفية
    monitoring_task = asyncio.create_task(monitoring_loop(application))
    logger.info("تم بدء حلقة المراقبة")


def main() -> None:
    """تشغيل البوت"""
    
    if not BOT_TOKEN:
        logger.error("❌ خطأ: يجب تعيين متغير البيئة BOT_TOKEN!")
        return
    
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("monitor", monitor))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stats", stats))
    
    # معالج الرسائل النصية (للرقم الجامعي)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_id))
    
    application.add_error_handler(error_handler)
    
    # تشغيل البوت
    logger.info("🤖 البوت يعمل الآن...")
    logger.info("✨ يمكن للمستخدمين إرسال أرقامهم الجامعية للحصول على النتائج")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

