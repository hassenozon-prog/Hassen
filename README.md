# المساعد القانوني اليمني المتخصص

قاعدة معرفة قانونية يمنية منظمة وقابلة للتوسع، مع محرك استرجاع أولي قابل للدمج مع طبقة الاستدلال.

## المكونات

- laws/ — القوانين والمواد والتعديلات.
- principles/ — مبادئ المحكمة العليا وقواعد النقض.
- cases/ — سجلات القضايا والنماذج.
- fiqh/ — التأصيل والقواعد الفقهية ذات الصلة.
- sources/ — المصادر الرسمية وسجلات التحقق.
- research/ — البحث والربط والتحقق.
- config/ — قواعد الأولوية والاسترجاع والاستشهاد والحالة.
- retrieval/ — محرك الاسترجاع.
- tests/ — اختبارات المحرك.

## تجربة سريعة

    python retrieval/engine.py "دليل لم يطرح في الجلسة"

ولإخراج قابل للربط مع نموذج لغة:

    python retrieval/engine.py "المادة 499 منازعة تنفيذ" --json

المحرك يسترجع المصادر ولا يصدر حكماً قانونياً بذاته. كل إجابة نهائية يجب أن تميز بين النص القانوني والوقائع والتحليل ودرجة التحقق، وأن تتحقق من التعديلات قبل اعتبار النص نافذاً.


## فهرسة قانونية قابلة لإعادة البناء

- إعادة بناء الفهارس بعد تعديل ملفات المعرفة: `python tools/rebuild_indexes.py --write`
- فحص حداثة الفهارس وسلامة المسارات: `python tools/rebuild_indexes.py --check`
- اختبار أداة الفهرسة: `python tests/test_indexes.py`
- دليل التشغيل: [docs/indexing-operations.md](docs/indexing-operations.md)

هذه الأداة تفهرس الملفات والبيانات الوصفية البنيوية فقط؛ ولا تثبت نفاذ تشريع أو صحة سابقة قضائية. تظل حالة النفاذ غير متحققة إلى أن يراجع المصدر الرسمي.


## سجل التحقق من المصادر القانونية
- سجل المصادر الأولي: `research/source-verification-register.csv`
- مخطط السجل: `schemas/source-verification-record.schema.json`
- فحص السجل: `python tools/validate_source_register.py`
- بوابة التحقق لا تقبل مرجعًا بوصفه `verified/current` إلا مع رابط مصدر وتاريخ تحقق واسم المراجع وموضع دليل التحقق.
- وجود رابط إلى فهرس رسمي لا يعني أن كل مادة في القانون أو حالة نفاذها قد تحققت؛ سجل المصدر يميز بين العثور على المصدر والتحقق من محتواه.


## تشغيل الواجهة البرمجية الآمن
- التشغيل المحلي: `python -m api.app` ثم فحص `GET http://127.0.0.1:8080/health`.
- لاستخدام الواجهة خارج الجهاز المحلي، اضبط `API_KEY` بمفتاح قوي قبل تعيين `HOST=0.0.0.0`. أرسل الطلبات مع `Authorization: Bearer <API_KEY>`.
- مثال استعلام: `curl -X POST http://127.0.0.1:8080/query -H 'Content-Type: application/json' -d '{"question":"المادة 499 منازعة تنفيذ"}'`.
- فحص سجل المواد: `python tools/validate_article_register.py`.
- فحص سجل المصادر: `python tools/validate_source_register.py`.
- تشغيل الاختبارات: راجع [دليل التشغيل](docs/operational-runbook.md) أو تابع نتيجة [GitHub Actions](https://github.com/hassenozon-prog/Hassen/actions).
- لا تستخدم الخدمة كمرجع قانوني نهائي قبل التحقق من النص الرسمي والتعديلات والنفاذ؛ نجاح الاختبارات لا يثبت صحة كل مادة.


## دليل الموارد القانونية اليمنية والعربية والرقمية
- فهرس المواقع والمكتبات والمنصات: [sources/resource-catalog.csv](sources/resource-catalog.csv)
- الدليل ومراتب الاستناد وسياسة الخصوصية والتحقق: [docs/legal-resource-directory.md](docs/legal-resource-directory.md)
- مخطط سجل الموارد: [schemas/resource-catalog.schema.json](schemas/resource-catalog.schema.json)
- فحص الفهرس: `python tools/validate_resource_catalog.py`
- اختبارات الفهرس: `python tests/test_resource_catalog.py`

يتضمن السجل مصادر يمنية رسمية، وقواعد قانونية عربية، ومكتبات ومراكز أبحاث، وأدوات ذكاء اصطناعي، وروابط بحث لاكتشاف المحتوى القانوني العام في وسائل التواصل. حالة `seeded_candidate` تعني أن المورد مرشح للمراجعة، ولا تعني أن كل محتواه تحقق. أدوات الذكاء الاصطناعي ومنصات التواصل مصنفة للاكتشاف فقط، ولا تمنح وصولًا إلى المحادثات الخاصة أو المجموعات المغلقة.


## دليل الجهات القضائية والمجلات والأحكام والقنوات
- الجهات القضائية الرسمية في 22 دولة عربية: [sources/judiciary-directory.csv](sources/judiciary-directory.csv)
- بيانات المجلات القانونية المحكمة والمقالات: [sources/legal-journals.csv](sources/legal-journals.csv)
- سجل الأحكام القضائية الأصلية: [sources/case-law-register.csv](sources/case-law-register.csv)
- القنوات القانونية المحددة: [sources/legal-media-channels.csv](sources/legal-media-channels.csv)
- فحص الروابط: `python tools/check_resource_links.py`
- هذه السجلات متاحة لمحرك الاسترجاع للاكتشاف فقط؛ لا تُعامل بيانات الدليل كمرجع قانوني أو سابقة قضائية موثقة.


## استخدام قاعدة Hassen في محادثة «نبراس القانون»
- تعليمات المشروع الجاهزة للنسخ: [docs/nebras-law-project-instructions.md](docs/nebras-law-project-instructions.md)
- مخطط OpenAPI لربط GPT Action بعد نشر الخدمة: [api/openapi.json](api/openapi.json)
- البحث الشامل في مواد المستودع: محرك `retrieval/engine.py` يفهرس ملفات النص المدعومة (بما فيها Python وMarkdown وYAML وJSON وHTML وملفات الإعداد) وملفات CSV وسجلات التحقق، وواجهة API تعيد بناء الفهرس قبل كل استعلام.
- ملاحظة تشغيلية: تحديث ملفات GitHub لا يصل إلى خدمة مستضافة أو نسخة محلية تلقائيًا دون نشر/مزامنة؛ لا يُدّعى اتصال حي غير مختبر.
