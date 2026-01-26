"""
مكون إنشاء PDF للفواتير
"""
import os

# التحقق من توفر مكتبة reportlab
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import black, gray
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass


class InvoicePDF:
    """فئة لإنشاء فواتير PDF (تدعم العربية والطابعات الحرارية والباركود)"""
    
    @staticmethod
    def create_invoice_pdf(invoice_data, output_path):
        """
        إنشاء فاتورة إيصال (Thermal Wrapper 80mm) مع Barcode
        """
        try:
            if not REPORTLAB_AVAILABLE:
                return False, "مكتبة reportlab غير متوفرة"
            
            # استيراد مكتبات Barcode من ReportLab
            from reportlab.graphics.barcode import code128
            from reportlab.graphics.shapes import Drawing
            
            # === إعداد دعم اللغة العربية ===
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import arabic_reshaper
            from bidi.algorithm import get_display

            # تسجيل خط يدعم العربية
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
            if not os.path.exists(font_path):
                font_path = "arial.ttf" 
            
            try:
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                font_name = 'ArabicFont'
            except:
                font_name = 'Helvetica'

            def ar(text):
                """دالة مساعدة لعرض النص العربي بشكل صحيح"""
                if font_name == 'ArabicFont':
                    try:
                        reshaped_text = arabic_reshaper.reshape(str(text))
                        return get_display(reshaped_text)
                    except:
                        return str(text)
                return str(text)

            # === إعداد الصفحة (مقاس إيصال 80mm) ===
            page_width = 80 * mm
            # تقدير الطول
            items_count = len(invoice_data.get('items', []))
            est_height = 60 + 50 + (10 * items_count) + 50 + 30
            page_height = est_height * mm
            
            c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
            
            margin = 2 * mm
            width = page_width
            y = page_height - 10 * mm
            
            # === الترويسة ===
            c.setFont(font_name, 14)
            c.drawCentredString(width/2, y, ar("محل البركة"))
            y -= 6*mm
            
            c.setFont(font_name, 10)
            c.drawCentredString(width/2, y, ar("العنوان: شارع النصر – القاهرة"))
            y -= 5*mm
            c.drawCentredString(width/2, y, ar("الهاتف: 0100-123-4567"))
            
            y -= 5*mm
            c.setLineWidth(1)
            c.setStrokeColor(black)
            c.line(margin, y, width - margin, y)
            y -= 5*mm
            
            # === بيانات الفاتورة ===
            c.setFont(font_name, 9)
            
            # دالة مساعدة لرسم سطر بيانات (مفتاح: قيمة)
            def draw_row(label, value, current_y):
                c.drawRightString(width - margin - 2*mm, current_y, ar(f"{label}:"))
                c.drawString(margin + 2*mm, current_y, ar(str(value)))
                return current_y - 5*mm

            y = draw_row("الاسم", invoice_data.get('customer_name', ''), y)
            y = draw_row("رقم الهاتف", invoice_data.get('customer_phone', ''), y)
            y = draw_row("رقم الفاتورة", invoice_data.get('invoice_id', ''), y)
            y = draw_row("الباركود", invoice_data.get('barcode', ''), y)
            y = draw_row("التاريخ", invoice_data.get('date', ''), y)
            
            y += 2*mm
            c.line(margin, y, width - margin, y)
            y -= 5*mm
            
            # === جدول المنتجات ===
            # العناوين
            c.setFont(font_name, 9)
            col_x_name = width - margin      # يمين
            col_x_qty = margin + 25*mm       # وسط
            col_x_price = margin             # يسار
            
            c.drawRightString(col_x_name - 2*mm, y, ar("الصنف"))
            c.drawCentredString(col_x_qty, y, ar("الكمية"))
            c.drawString(col_x_price, y, ar("الإجمالي"))
            
            y -= 2*mm
            c.line(margin, y, width - margin, y)
            y -= 5*mm
            
            # المنتجات
            items = invoice_data.get('items', [])
            for item in items:
                name = ar(item.get('name', ''))
                qty = str(item.get('quantity', 0))
                total = f"{item.get('total', 0):.2f}"
                
                c.setFont(font_name, 9)
                
                # حساب عدد الأسطر المطلوبة للاسم
                # نفترض أن السطر الواحد يسع حوالي 20 حرف (أو حسب العرض المتاح)
                # العرض المتاح للاسم تقريباً 40 مم
                # سنقوم بتقسيم الاسم يدوياً
                max_chars = 22
                wrapped_lines = []
                if len(name) > max_chars:
                    # تقسيم النص لأجزاء
                    import textwrap
                    wrapped_lines = textwrap.wrap(name, width=max_chars)
                else:
                    wrapped_lines = [name]
                
                # رسم السطر الأول مع الكمية والسعر
                first_line = wrapped_lines[0]
                c.drawRightString(col_x_name - 2*mm, y, first_line)
                c.drawCentredString(col_x_qty, y, qty)
                c.drawString(col_x_price, y, total)
                
                # رسم باقي الأسطر إن وجدت
                for i in range(1, len(wrapped_lines)):
                    y -= 4*mm # مسافة أقل بين أسطر نفس المنتج
                    line = wrapped_lines[i]
                    c.drawRightString(col_x_name - 2*mm, y, line)
                
                y -= 5*mm # مسافة للمنتج التالي
            
            y += 2*mm
            c.line(margin, y, width - margin, y)
            y -= 5*mm
            
            # === الإجماليات ===
            y = draw_row("الإجمالي قبل الخصم", f"{invoice_data.get('subtotal', 0):.2f}", y)
            y = draw_row("الخصم", f"{invoice_data.get('discount', 0):.2f}", y)
            
            c.setFont(font_name, 11) # تكبير الخط للإجمالي النهائي
            y -= 2*mm
            y = draw_row("الإجمالي بعد الخصم", f"{invoice_data.get('total', 0):.2f}", y)
            
            y += 2*mm
            c.line(margin, y, width - margin, y)
            y -= 8*mm
            
            # === Barcode (Code128) ===
            # نستخدم رقم الفاتورة أو الباركود النصي لتوليد الباركود
            barcode_value = str(invoice_data.get('invoice_id', '0000'))
            
            try:
                # إنشاء الباركود
                barcode_drawing = code128.Code128(barcode_value, barHeight=10*mm, barWidth=1.2) # تكبير العرض قليلاً
                
                # رسم الباركود في وسط الصفحة
                # نحتاج لحساب عرض الباركود لتوسطه، لكن code128 معقد قليلاً
                # سنضعه في إحداثيات مقدرة
                barcode_x = (width - barcode_drawing.width) / 2
                
                y -= 5*mm  # مسافة إضافية قبل الباركود
                
                # رسم الباركود مباشرة على الـ Canvas
                barcode_drawing.drawOn(c, barcode_x, y)
                
                y -= 15*mm
            except Exception as e:
                print(f"Barcode Error: {e}")
                c.drawString(margin, y, f"Barcode: {barcode_value}")
                y -= 10*mm

            # === التذييل ===
            c.setFont(font_name, 10)
            c.drawCentredString(width/2, y, ar("شكراً لتعاملكم معنا!"))
            y -= 5*mm
            c.drawCentredString(width/2, y, ar("للاتصال: 0100-123-4567"))
            
            c.save()
            return True, f"تم حفظ الفاتورة: {output_path}"
            
        except Exception as e:
            return False, f"خطأ PDF: {str(e)}"


def print_file(filepath):
    """
    طباعة ملف على الطابعة الافتراضية (Windows فقط)
    
    Args:
        filepath: مسار الملف للطباعة
        
    Returns:
        tuple: (success, message)
    """
    try:
        import win32api
        import win32print
        
        # الحصول على الطابعة الافتراضية
        printer = win32print.GetDefaultPrinter()
        
        # التأكد من أن المسار مطلق
        abs_filepath = os.path.abspath(filepath)
        
        if not os.path.exists(abs_filepath):
            return False, f"الملف غير موجود: {abs_filepath}"
            
        # طباعة الملف
        win32api.ShellExecute(0, "print", abs_filepath, None, ".", 0)
        
        return True, f"تم إرسال الملف للطباعة على: {printer}"
        
    except ImportError:
        return False, "مكتبة pywin32 غير متوفرة"
    except Exception as e:
        return False, f"خطأ في الطباعة: {str(e)}"
