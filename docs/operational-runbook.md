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
    docker run --rm -p 8080:8080 yemeni-legal-assistant

قبل النشر العام يجب إضافة Authentication وRate limiting وCORS مقيد ومراقبة السجلات، وعدم إدخال أسرار في المستودع.
