#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لتسجيل الدخول واستخراج النتائج من بوابة الطلاب باستخدام Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


class StudentPortalScraper:
    """فئة للتعامل مع بوابة الطلاب واستخراج البيانات باستخدام Selenium"""
    
    def __init__(self, headless=True):
        self.base_url = "http://212.0.143.242/portal/students"
        self.driver = None
        self.headless = headless
    
    def _init_driver(self):
        """تهيئة متصفح Chrome"""
        chrome_options = Options()
        
        # إعدادات للعمل على Railway
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--lang=ar')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # تثبيت ChromeDriver تلقائياً
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # محاولة بدون webdriver-manager
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.implicitly_wait(10)
    
    def login(self, student_id, password="123456"):
        """
        تسجيل الدخول إلى البوابة
        
        Args:
            student_id: الرقم الجامعي للطالب
            password: كلمة المرور (افتراضياً 123456)
        
        Returns:
            bool: True إذا نجح تسجيل الدخول، False إذا فشل
        """
        try:
            if not self.driver:
                self._init_driver()
            
            # فتح صفحة تسجيل الدخول
            self.driver.get(f"{self.base_url}/")
            time.sleep(2)
            
            # البحث عن حقول الإدخال
            username_field = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="الرقم الجامعي"]')
            password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="كلمة المرور"]')
            
            # إدخال البيانات
            username_field.clear()
            username_field.send_keys(student_id)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # البحث عن زر الدخول والضغط عليه
            login_buttons = self.driver.find_elements(By.TAG_NAME, 'input')
            for btn in login_buttons:
                if btn.get_attribute('type') in ['submit', 'button']:
                    btn.click()
                    break
            
            # الانتظار حتى يتم تحميل الصفحة
            time.sleep(3)
            
            # التحقق من نجاح تسجيل الدخول
            if 'Logout' in self.driver.page_source or student_id in self.driver.page_source:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"خطأ في تسجيل الدخول: {str(e)}")
            return False
    
    def get_student_info(self):
        """
        استخراج البيانات الأساسية للطالب
        
        Returns:
            dict: قاموس يحتوي على بيانات الطالب
        """
        try:
            student_info = {}
            
            # البحث عن جدول البيانات الأساسية
            tables = self.driver.find_elements(By.TAG_NAME, 'table')
            
            if tables:
                # استخراج البيانات من أول جدول
                rows = tables[0].find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 2:
                        for i in range(0, len(cells), 2):
                            if i + 1 < len(cells):
                                value = cells[i].text.strip()
                                key = cells[i+1].text.strip()
                                if key and value:
                                    student_info[key] = value
            
            return student_info
            
        except Exception as e:
            print(f"خطأ في استخراج بيانات الطالب: {str(e)}")
            return {}
    
    def get_results(self):
        """
        استخراج نتائج الامتحانات
        
        Returns:
            list: قائمة تحتوي على النتائج
        """
        try:
            # الضغط على قسم النتيجة
            result_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'النتيجة')
            if result_links:
                result_links[0].click()
                time.sleep(2)
            
            results = []
            
            # البحث عن جدول النتائج
            tables = self.driver.find_elements(By.TAG_NAME, 'table')
            
            for table in tables:
                # البحث عن جدول النتائج
                headers = table.find_elements(By.TAG_NAME, 'th')
                header_text = ' '.join([h.text for h in headers])
                
                if 'Grade' in header_text or 'Course' in header_text or 'التقدير' in header_text:
                    rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # تجاوز صف العناوين
                    
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        if len(cells) >= 2:
                            grade = cells[0].text.strip()
                            course = cells[1].text.strip()
                            
                            if grade and course:
                                results.append({
                                    'التقدير': grade,
                                    'المادة': course
                                })
            
            return results
            
        except Exception as e:
            print(f"خطأ في استخراج النتائج: {str(e)}")
            return []
    
    def get_all_data(self, student_id, password="123456"):
        """
        استخراج جميع بيانات الطالب
        
        Args:
            student_id: الرقم الجامعي
            password: كلمة المرور
        
        Returns:
            dict: جميع بيانات الطالب والنتائج
        """
        try:
            if not self.login(student_id, password):
                return {
                    'success': False,
                    'error': 'فشل تسجيل الدخول. تحقق من الرقم الجامعي وكلمة المرور.'
                }
            
            student_info = self.get_student_info()
            results = self.get_results()
            
            return {
                'success': True,
                'student_id': student_id,
                'student_info': student_info,
                'results': results
            }
        finally:
            self.close()
    
    def close(self):
        """إغلاق المتصفح"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def format_results_message(self, data):
        """
        تنسيق البيانات لإرسالها عبر التلغرام
        
        Args:
            data: البيانات المستخرجة
        
        Returns:
            str: رسالة منسقة
        """
        if not data['success']:
            return f"❌ {data['error']}"
        
        message = "📊 *نتائج الطالب*\n"
        message += "=" * 30 + "\n\n"
        
        # البيانات الأساسية
        if data['student_info']:
            message += "👤 *البيانات الأساسية:*\n"
            for key, value in data['student_info'].items():
                message += f"• {key}: {value}\n"
            message += "\n"
        
        # النتائج
        if data['results']:
            message += "📝 *النتائج الدراسية:*\n"
            message += "─" * 30 + "\n"
            for i, result in enumerate(data['results'], 1):
                message += f"{i}. {result['المادة']}\n"
                message += f"   التقدير: *{result['التقدير']}*\n\n"
        else:
            message += "⚠️ لا توجد نتائج متاحة حالياً\n"
        
        return message


def main():
    """دالة الاختبار"""
    print("جاري تسجيل الدخول واستخراج البيانات...")
    scraper = StudentPortalScraper(headless=True)
    
    # اختبار مع الرقم الجامعي المعطى
    data = scraper.get_all_data("1124693617", "123456")
    
    if data['success']:
        print("\n" + "=" * 50)
        print("البيانات الأساسية:")
        print("=" * 50)
        for key, value in data['student_info'].items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 50)
        print("النتائج:")
        print("=" * 50)
        for result in data['results']:
            print(f"{result['المادة']}: {result['التقدير']}")
        
        print("\n" + "=" * 50)
        print("رسالة التلغرام المنسقة:")
        print("=" * 50)
        print(scraper.format_results_message(data))
    else:
        print(f"❌ خطأ: {data['error']}")


if __name__ == "__main__":
    main()

