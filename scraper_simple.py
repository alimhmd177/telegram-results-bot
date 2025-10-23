#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت بسيط لاستخراج النتائج باستخدام requests فقط (بدون Selenium)
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
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def login(self, student_id, password="123456"):
        """تسجيل الدخول إلى البوابة"""
        try:
            print(f"محاولة تسجيل الدخول للطالب: {student_id}")
            
            # الحصول على صفحة تسجيل الدخول أولاً
            login_page = self.session.get(f"{self.base_url}/", timeout=10)
            print(f"حالة الطلب الأولي: {login_page.status_code}")
            
            # إرسال بيانات تسجيل الدخول
            login_url = f"{self.base_url}/index.php"
            
            # إرسال بيانات تسجيل الدخول مع الحقول الصحيحة
            login_data = {
                'action': 'login',
                'username': student_id,
                'password': password,
                'submit': 'دخول'
            }
            
            response = self.session.post(login_url, data=login_data, allow_redirects=True, timeout=10)
            print(f"حالة تسجيل الدخول: {response.status_code}")
            print(f"URL بعد تسجيل الدخول: {response.url}")
            
            # التحقق من نجاح تسجيل الدخول
            if (response.status_code == 200 and 
                ('Logout' in response.text or 
                 'تسجيل الخروج' in response.text or 
                 student_id in response.text or
                 'البيانات الاساسية' in response.text)):
                print("تم تسجيل الدخول بنجاح")
                return True
            else:
                print("فشل تسجيل الدخول")
                # حفظ محتوى الصفحة للتشخيص
                with open('/tmp/login_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text[:1000])
                return False
                
        except Exception as e:
            print(f"خطأ في تسجيل الدخول: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_student_info(self):
        """استخراج البيانات الأساسية للطالب"""
        try:
            response = self.session.get(f"{self.base_url}/index.php", timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            student_info = {}
            
            # حفظ الصفحة للتشخيص
            with open('/tmp/student_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # استخراج البيانات من الجدول
            tables = soup.find_all('table')
            print(f"عدد الجداول الموجودة: {len(tables)}")
            
            if tables:
                # الجدول الأول يحتوي على البيانات الأساسية
                first_table = tables[0]
                rows = first_table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 4:  # كل صف يحتوي على 4 خلايا
                        # الخلية الأولى: القيمة 1
                        # الخلية الثانية: المفتاح 1
                        # الخلية الثالثة: القيمة 2
                        # الخلية الرابعة: المفتاح 2
                        value1 = cells[0].get_text(strip=True)
                        key1 = cells[1].get_text(strip=True)
                        value2 = cells[2].get_text(strip=True)
                        key2 = cells[3].get_text(strip=True)
                        
                        if key1 and value1:
                            student_info[key1] = value1
                        if key2 and value2:
                            student_info[key2] = value2
            
            print(f"تم استخراج {len(student_info)} حقل من البيانات الأساسية")
            return student_info
            
        except Exception as e:
            print(f"خطأ في استخراج بيانات الطالب: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_results(self):
        """استخراج نتائج الامتحانات"""
        try:
            response = self.session.get(f"{self.base_url}/index.php", timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            results = []
            
            # البحث عن جدول النتائج
            tables = soup.find_all('table')
            print(f"فحص {len(tables)} جدول للبحث عن النتائج")
            
            for idx, table in enumerate(tables):
                headers = table.find_all('th')
                header_text = ' '.join([h.get_text() for h in headers])
                print(f"الجدول {idx}: {header_text[:50]}")
                
                if 'Grade' in header_text or 'Course' in header_text or 'التقدير' in header_text:
                    print(f"تم العثور على جدول النتائج في الجدول {idx}")
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
                                print(f"  - {course}: {grade}")
            
            print(f"تم استخراج {len(results)} نتيجة")
            return results
            
        except Exception as e:
            print(f"خطأ في استخراج النتائج: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_data(self, student_id, password="123456"):
        """استخراج جميع بيانات الطالب"""
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
        """تنسيق البيانات لإرسالها عبر التلغرام"""
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
    scraper = StudentPortalScraper()
    
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

