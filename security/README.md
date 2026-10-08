# متطلبات الأمان قبل النشر

- لا تخزن مفاتيح API أو GitHub tokens في المستودع.
- استخدم Secrets/Environment Variables في بيئة التشغيل.
- قيد CORS إلى الواجهات المصرح لها.
- أضف Authentication وRate limiting قبل جعل API عامة.
- لا تسجل نصوص القضايا الحساسة في logs إلا عند الضرورة.
- افصل بيانات المستخدم عن corpus القانوني العام.
- راجع صلاحيات GitHub قبل منح أي workflow قدرة كتابة.
