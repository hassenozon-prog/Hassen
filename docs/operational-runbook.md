# دليل التشغيل

## محلياً

    python -m api.app

ثم:

    GET /health

واستعلام:

    POST /query

## فحص corpus

    python ingestion/corpus_manifest.py --output corpus-manifest.json

## الاختبارات

    python tests/test_retrieval.py
    python tests/test_reasoning.py
    python tests/test_verification.py
    python tests/test_drafting.py
    python tests/test_case_engine.py
    python tests/test_manifest.py
    python tests/test_api.py

## Docker

    docker build -t yemeni-legal-assistant .
    export API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
    docker run --rm -p 8080:8080 -e API_KEY="$API_KEY" yemeni-legal-assistant

لا تشغّل Docker مع `0.0.0.0` دون `API_KEY`. يلزم للنشر العام TLS وreverse proxy مع Rate limiting ومراقبة آمنة للسجلات؛ لا تضع الأسرار في المستودع.


## ضوابط تشغيل الواجهة (الإصدار 1.3)

- للتشغيل المحلي فقط: `python -m api.app` ويستمع افتراضيًا على `127.0.0.1:8080`.
- لا تربط الخدمة بعنوان عام أو `0.0.0.0` دون تعيين متغير بيئة قوي `API_KEY`. الطلبات إلى `/query` و`/case` تتطلب `Authorization: Bearer <API_KEY>` عند تعيين المفتاح.
- فحص الصحة `GET /health` عام ولا يعرض نصوص القضايا أو بياناتها.
- الحد الأقصى لجسم الطلب 1,000,000 بايت؛ وحد الاسترجاع من 1 إلى 20، وتُرفض قيم limit غير الرقمية بدل إسقاط الخدمة.
- الخدمة لا تستبدل مراجعة المحامي؛ النصوص ذات حالة نفاذ `unknown` لا يجوز اعتمادها كنصوص نافذة.
- لا توجد في هذه النسخة قاعدة بيانات قضايا دائمة ولا تسجيل دخول للمستخدمين ولا تحديد معدل طلبات متقدم؛ يلزم وضعها خلف reverse proxy آمن عند النشر متعدد المستخدمين.
- اختبارات الانحدار: `python tests/test_api.py`, `python tests/test_retrieval.py`, `python tests/test_reasoning.py`, ثم جميع خطوات CI.


## الإصدار 1.4 — فهرسة شاملة
- يعاد بناء الفهرس قبل كل طلب `POST /query`، بما في ذلك جميع سجلات CSV في نسخة المستودع المحلية.
- بعد تحديث GitHub، حدّث نسخة العمل/صورة النشر قبل استخدام API حتى تظهر الالتزامات الجديدة.
- شغّل `python tests/test_retrieval.py` للتأكد من أن سجل المواد قابل للبحث ولا يتحول إلى نص نافذ دون دليل.
- للحصول على اتصال ChatGPT مباشر، اتبع `docs/nebras-law-project-instructions.md` و`api/openapi.json`; لا تُدخل مفتاح API في مستودع Git.
