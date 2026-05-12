# Implementation Plan: Section-Aware NER Extraction

هذه الخطة تهدف إلى تطوير محرك الـ NER ليصبح أكثر دقة من خلال استغلال الهيكل التنظيمي للـ CV (Sections) أثناء عملية الاستخراج، بدلاً من التعامل مع النص ككتلة واحدة صماء.

---

## 1. المشكلة الحالية (Current Problem)
*   **تداخل الكيانات (Entity Overlap):** الموديل قد يستخرج أسماء أشخاص أو مؤسسات ويصنفها كمهارات (Skills) لمجرد أنها ظهرت في سياق مهارات أو مشاريع.
*   **فقدان السياق الهيكلي:** الموديل لا يفرق بين كلمة "Python" الموجودة في سكشن "المهارات" وبين "Python" المذكورة كأداة استخدمت في "مشروع" قديم.
*   **الضوضاء (Noise):** ظهور مخرجات غير منطقية في بعض التصنيفات (مثل ظهور اسم المدرب كمهارة).

---

## 2. مرحلة المعالجة المسبقة (Pre-processing Phase)
قبل إرسال النص لأي عملية تحليل، يجب تنظيفه لضمان عدم تضليل الموديل:
*   **إزالة الرموز الغريبة (Noise Removal):** تنظيف النقاط (Bullets) غير المنتظمة والرموز التي تنتج عن الـ OCR أحياناً.
*   **توحيد المسافات (Whitespace Normalization):** تقليص المسافات المتعددة والأسطر الفارغة الزائدة التي قد تشتت الموديل.
*   **معالجة الرموز الخاصة (Symbol Handling):** التأكد من أن الرموز الهامة مثل `C++` و `C#` و `.NET` يتم التعامل معها ككتلة واحدة ولا يتم فصلها أثناء التنظيف.

---

## 3. الحل المقترح: Section-Aware Extraction
الفكرة هي تحويل عملية الـ Extraction من عملية "عشوائية" على النص الكامل إلى عملية "موجهة" بناءً على الأقسام.

### أ. استراتيجية التقسيم المسبق (Segment-First Strategy)
1.  تشغيل الـ `SectionSegmenter` أولاً لتحديد حدود كل قسم (Skills, Experience, Education, etc.).
2.  بدلاً من تمرير النص الكامل فقط، يتم تمرير "نصوص مخصصة" لكل نوع من الكيانات.

### ب. حقن السياق (Context Injection)
قبل تمرير النص للموديل، يتم إضافة وسم (Tag) يوضح نوع القسم، مما يساعد الـ Transformers على ضبط الـ Attention:
*   `[CONTEXT: SKILLS_SECTION] Python, Java, AWS...`
*   `[CONTEXT: EXPERIENCE_SECTION] Developed a mobile app using Flutter...`

---

## 4. خطوات التنفيذ (Action Plan)

### الخطوة الصفرية: تطوير وحدة الـ Pre-processor
*   بناء دالة `clean_text_for_ner` تقوم بعملية التنظيف قبل البدء في الـ Pipeline.

### الخطوة الأولى: تعديل `AdvancedNEREngine`
*   إضافة بارامتر اختياري `section_context` لوظيفة `extract_entities`.
*   تعديل منطق دمج التوكنز ليعطي ثقة أعلى (Confidence Score) إذا تطابق نوع الكيان مع نوع السكشن (مثلاً مهارة داخل سكشن مهارات).

### الخطوة الثانية: تعديل الـ `Orchestrator` (الـ Refactor الأساسي)
*   تعديل `_run_nlp_pipeline` ليكون الترتيب كالتالي:
    1.  `clean_text = preprocessor.clean(text)`
    2.  `segments = segmenter.segment(clean_text)`
    3.  تشغيل NER مخصص لكل سكشن:
        *   `skills_entities = ner.extract_entities(segments.skills, context="skills")`
        *   `exp_entities = ner.extract_entities(segments.experience, context="experience")`
    4.  دمج النتائج (Merging) مع إعطاء الأولوية للـ NER الموجه.

### الخطوة الثالثة: الفلترة الذكية (Smart Filtering)
*   استخدام نتائج سكشن الـ `Education` لاستبعاد أي "أسماء جامعات" قد تظهر بالخطأ في سكشن المهارات.
*   استخدام سكشن الـ `Experience` لاستبعاد "المسميات الوظيفية" من قائمة المهارات.

---

## 5. الفوائد المتوقعة (Expected Benefits)
1.  **دقة أعلى (Higher Precision):** تقليل الـ False Positives (الأخطاء) بنسبة تتراوح بين 15-20%.
2.  **تنظيف البيانات:** التخلص من الأسماء الغريبة والشهادات التي تظهر كمهارات.
3.  **منطق دفاعي أقوى:** سيكون للمشروع "منطق هندسي" (Architectural Logic) قوي يمكن الدفاع عنه في المناقشة.

---

## 6. خطة التحقق (Verification Plan)
*   مقارنة ملف الـ JSON القديم (`ner_trace_output.json`) بالملف الجديد بعد التعديل.
*   التأكد من أن مهارات مثل "Sarwat Samy" قد اختفت من قائمة الـ Skills.
