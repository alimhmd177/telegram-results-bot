#!/usr/bin/env python3
"""
بوت تليجرام لمراقبة صفحة نتائج الطلاب
يرسل إشعارات فورية عندما تصبح الصفحة متاحة
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Set
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# إعدادات البوت - يتم قراءتها من متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_URL = os.getenv("TARGET_URL", "http://212.0.143.242/portal/students/index.php")
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
                        f"🕐 الوقت: {current_time}"
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
        "هذا البوت يراقب صفحة نتائج الطلاب ويرسل لك إشعاراً فورياً عندما تصبح متاحة.\n\n"
        "📋 *الأوامر المتاحة:*\n"
        "/start - عرض هذه الرسالة\n"
        "/monitor - بدء المراقبة\n"
        "/stop - إيقاف المراقبة\n"
        "/status - عرض حالة الموقع الحالية\n"
        "/stats - عرض الإحصائيات\n\n"
        f"🔗 *الرابط المراقب:*\n`{TARGET_URL}`\n\n"
        f"⏱️ *فترة الفحص:* كل {CHECK_INTERVAL} ثانية\n\n"
        "استخدم /monitor لبدء المراقبة!"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


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
                f"🔗 يمكنك الوصول إليها الآن:\n{TARGET_URL}"
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


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")


def main() -> None:
    """تشغيل البوت"""
    
    if not BOT_TOKEN:
        logger.error("❌ خطأ: يجب تعيين متغير البيئة BOT_TOKEN!")
        return
    
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monitor", monitor))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stats", stats))
    application.add_error_handler(error_handler)
    
    # بدء حلقة المراقبة في الخلفية
    application.job_queue.run_once(
        lambda context: asyncio.create_task(monitoring_loop(application)),
        when=0
    )
    
    # تشغيل البوت
    logger.info("🤖 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

