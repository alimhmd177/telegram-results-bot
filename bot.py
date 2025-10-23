#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تلغرام لاستخراج نتائج الطلاب من بوابة جامعة البحر الأحمر
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from scraper_selenium import StudentPortalScraper

# إعداد السجل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class StudentBot:
    """فئة بوت التلغرام"""
    
    def __init__(self, token):
        self.token = token
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        welcome_message = """
🎓 *مرحباً بك في بوت نتائج الطلاب*

هذا البوت يساعدك في الحصول على نتائجك الدراسية من بوابة جامعة البحر الأحمر.

*الأوامر المتاحة:*
📝 /get_results - للحصول على نتائجك
❓ /help - للمساعدة

*كيفية الاستخدام:*
1️⃣ أرسل الأمر /get_results
2️⃣ أرسل رقمك الجامعي
3️⃣ أرسل كلمة المرور (افتراضياً: 123456)

أو يمكنك إرسال رقمك الجامعي مباشرة!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_text = """
📚 *المساعدة*

*طريقة الاستخدام:*

*الطريقة الأولى (السريعة):*
أرسل رقمك الجامعي مباشرة، وسيتم استخدام كلمة المرور الافتراضية (123456)

مثال:
`1124693617`

*الطريقة الثانية (مع كلمة مرور مخصصة):*
أرسل الرقم الجامعي ثم كلمة المرور مفصولة بمسافة

مثال:
`1124693617 mypassword`

*الأوامر:*
/start - بدء البوت
/get_results - الحصول على النتائج
/help - عرض المساعدة

*ملاحظة:*
كلمة المرور الافتراضية هي: 123456
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def get_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /get_results"""
        instructions = """
📝 *للحصول على نتائجك:*

أرسل رقمك الجامعي الآن.

أو أرسل الرقم الجامعي وكلمة المرور مفصولة بمسافة:
`1124693617 123456`
        """
        await update.message.reply_text(instructions, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        text = update.message.text.strip()
        
        # تجاهل الرسائل الفارغة
        if not text:
            return
        
        # إرسال رسالة انتظار
        wait_msg = await update.message.reply_text("⏳ جاري تسجيل الدخول واستخراج النتائج...\nقد يستغرق هذا بضع ثوانٍ...")
        
        scraper = None
        try:
            # تحليل الرسالة
            parts = text.split()
            
            if len(parts) == 1:
                # رقم جامعي فقط
                student_id = parts[0]
                password = "123456"
            elif len(parts) == 2:
                # رقم جامعي وكلمة مرور
                student_id = parts[0]
                password = parts[1]
            else:
                await wait_msg.edit_text(
                    "❌ تنسيق خاطئ!\n\n"
                    "أرسل رقمك الجامعي فقط، أو:\n"
                    "`رقم_جامعي كلمة_المرور`",
                    parse_mode='Markdown'
                )
                return
            
            # التحقق من صحة الرقم الجامعي
            if not student_id.isdigit():
                await wait_msg.edit_text(
                    "❌ الرقم الجامعي يجب أن يحتوي على أرقام فقط!"
                )
                return
            
            # استخراج البيانات
            scraper = StudentPortalScraper(headless=True)
            data = scraper.get_all_data(student_id, password)
            
            # تنسيق وإرسال النتيجة
            message = scraper.format_results_message(data)
            await wait_msg.edit_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الرسالة: {str(e)}")
            await wait_msg.edit_text(
                f"❌ حدث خطأ أثناء استخراج البيانات:\n{str(e)}\n\n"
                "الرجاء المحاولة مرة أخرى أو التواصل مع الدعم."
            )
        finally:
            # التأكد من إغلاق المتصفح
            if scraper:
                try:
                    scraper.close()
                except:
                    pass
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(self.token).build()
        
        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("get_results", self.get_results))
        
        # إضافة معالج الرسائل النصية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # بدء البوت
        logger.info("بدء تشغيل البوت...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """الدالة الرئيسية"""
    # الحصول على توكن البوت من متغيرات البيئة
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN")
        print("الرجاء تعيين توكن البوت في متغيرات البيئة:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # إنشاء وتشغيل البوت
    bot = StudentBot(token)
    bot.run()


if __name__ == "__main__":
    main()

