#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لتسجيل الدخول واستخراج النتائج من بوابة الطلاب
"""

import requests
from bs4 import BeautifulSoup
import re


class StudentPortalScraper:
    """فئة للتعامل مع بوابة الطلاب واستخراج البيانات"""
    
    def __init__(self):
        self.base_url = "http://212.0.143.242/portal/students"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://212.0.143.242',
            'Referer': 'http://212.0.143.242/portal/students/'
        })
    
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
            # أولاً، الحصول على صفحة تسجيل الدخول لأخذ أي cookies
            login_page = self.session.get(f"{self.base_url}/")
            
            # إرسال بيانات تسجيل الدخول
            login_url = f"{self.base_url}/index.php"
            
            # محاولة مع أسماء حقول مختلفة
            login_data = {
                'user': student_id,
                'pass': password,
                'submit': 'دخول'
            }
            
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            
            # التحقق من نجاح تسجيل الدخول
            if 'Logout' in response.text or 'تسجيل الخروج' in response.text or student_id in response.text:
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
            response = self.session.get(f"{self.base_url}/index.php")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            student_info = {}
            
            # استخراج البيانات من الجدول
            tables = soup.find_all('table')
            if tables:
                # البحث في أول جدول (البيانات الأساسية)
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # استخراج العنوان والقيمة
                            for i in range(0, len(cells), 2):
                                if i + 1 < len(cells):
                                    value = cells[i].get_text(strip=True)
                                    key = cells[i+1].get_text(strip=True)
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
            response = self.session.get(f"{self.base_url}/index.php")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # البحث عن جدول النتائج
            tables = soup.find_all('table')
            for table in tables:
                # البحث عن جدول النتائج بناءً على العناوين
                headers = table.find_all('th')
                header_text = ' '.join([h.get_text() for h in headers])
                
                if 'Grade' in header_text or 'Course' in header_text or 'التقدير' in header_text:
                    rows = table.find_all('tr')[1:]  # تجاوز صف العناوين
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            grade = cells[0].get_text(strip=True)
                            course = cells[1].get_text(strip=True)
                            
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
    scraper = StudentPortalScraper()
    
    # اختبار مع الرقم الجامعي المعطى
    print("جاري تسجيل الدخول واستخراج البيانات...")
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

