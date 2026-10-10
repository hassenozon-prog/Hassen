#!/usr/bin/env python3
"""Rebuild and validate the repository's CSV indexes without touching source files."""
from __future__ import annotations
import argparse, csv, io, re, sys
from pathlib import Path

ROOTS = ("laws", "principles", "fiqh", "cases", "sources", "research", "schemas", "ingestion")
MASTER = Path("indexes/MASTER_LEGAL_INDEX.csv")
STATUS = Path("indexes/LAW_STATUS_INDEX.csv")
MASTER_HEADER = ["record_id","title","source_type","jurisdiction","law_name","law_number","year","article_number","official_url","repository_path","verification_status","effective_status","last_verified","notes"]
STATUS_HEADER = ["law_key","law_name","law_number","year","repository_paths","repository_record_status","effective_status","official_source_url","last_checked","required_next_action","notes"]
LAWS = [
("civil-procedure","قانون المرافعات والتنفيذ المدني","40","2002","partially-verified (repository metadata only)"),
("criminal-procedure","قانون الإجراءات الجزائية","13","1994","partially-verified (repository metadata only)"),
("penal-code","قانون الجرائم والعقوبات","12","1994","partially-verified (repository metadata only)"),
("commercial","التشريعات التجارية","","","needs-verification"),
("execution","تشريعات التنفيذ","","","needs-verification"),
("judiciary","التشريعات القضائية","","","needs-verification"),
("labor","تشريعات العمل","","","needs-verification"),
("personal-status","تشريعات الأحوال الشخصية","","","needs-verification"),
("water","تشريعات المياه","","","needs-verification")]
NAMES = {x[0]:x[1] for x in LAWS}
UNKNOWN = "فهرسة بنيوية من مسار الملف؛ لا تثبت وحدها صحة المحتوى أو نفاذ التشريع أو حجية السابقة."
PARTIAL = "وصف التحقق الجزئي من بيانات المشروع فقط؛ يلزم الرجوع إلى المصدر الرسمي والتحقق من التعديلات والنفاذ."
PRECEDENT = "لا يعتمد كمبدأ قضائي موثق قبل التحقق من أصل الحكم ورقمه وتاريخه ودائرته ومضمونه."
STATUS_NOTE = "الحالة تعكس بيانات المستودع ومساراته فقط، وليست شهادة مستقلة بنفاذ القانون."

def paths(root: Path) -> list[str]:
    return sorted({p.relative_to(root).as_posix() for top in ROOTS if (root/top).exists() for p in (root/top).rglob("*") if p.is_file()})

def title(path: str) -> str:
    for part in path.split("/"):
        if part in NAMES: return NAMES[part]
    name = Path(path).name
    for suffix in (".md",".yml",".yaml",".json",".py",".csv",".xlsx"):
        if name.lower().endswith(suffix): name = name[:-len(suffix)]; break
    return name.replace("-"," ").replace("_"," ")

def metadata(path: str) -> tuple[str,str,str,str,str,str]:
    root = path.split("/")[0]
    types = {"laws":"ملف تشريع أو سجل تشريعي","principles":"مبدأ/مرجع قضائي يحتاج تحققًا","fiqh":"مرجع فقهي/سجل فقه","cases":"قالب أو سجل قضية","sources":"سجل مصدر","research":"أداة بحث وربط قانوني","schemas":"مخطط بيانات","ingestion":"إعداد جمع المصادر"}
    kind = types.get(root,"سجل/وثيقة مساندة")
    if root == "laws" and "/articles/" in path: kind = "سجل مادة تشريعية"
    law_name = law_number = year = article = ""
    for key,name,num,yr,_ in LAWS[:3]:
        if path.startswith("laws/"+key+"/"): law_name,law_number,year = name,num,yr; break
    match = re.search(r"/articles/(\d+)\.(?:md|yml|yaml)$",path,re.I)
    if match: article = match.group(1)
    status = "partially-verified (repository metadata only)" if any(path.startswith("laws/"+k+"/") for k in ("civil-procedure","criminal-procedure","penal-code")) else "needs-verification"
    note = PARTIAL if status.startswith("partially") else PRECEDENT if root == "principles" else UNKNOWN
    return kind,law_name,law_number,year,article,status,note

def csv_text(rows: list[list[str]]) -> str:
    stream = io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows(rows)
    return "\ufeff"+stream.getvalue()

def build_master(root: Path) -> str:
    rows = [MASTER_HEADER]
    for i,path in enumerate(paths(root),1):
        kind,law,num,year,article,state,note = metadata(path)
        rows.append([f"HASSEN-{i:04d}",title(path),kind,"اليمن",law,num,year,article,"",path,state,"unknown","",note])
    return csv_text(rows)

def build_status(root: Path) -> str:
    all_paths = paths(root)
    rows = [STATUS_HEADER]
    for key,name,num,year,state in LAWS:
        matched = "; ".join(p for p in all_paths if p.startswith("laws/"+key+"/"))
        rows.append([key,name,num,year,matched,state,"unknown","https://www.moj-ye.org/laws.php","","التحقق من النسخة الرسمية وآخر التعديلات وتاريخ النفاذ قبل الاستشهاد",STATUS_NOTE])
    return csv_text(rows)

def validate(root: Path) -> list[str]:
    errors=[]
    for file,expected in ((MASTER,build_master(root)),(STATUS,build_status(root))):
        target=root/file
        if not target.exists(): errors.append("ملف مفقود: "+str(file))
        elif target.read_text(encoding="utf-8-sig") != expected.lstrip("\ufeff"): errors.append("فهرس قديم: "+str(file)+"؛ شغّل python tools/rebuild_indexes.py --write")
    target=root/MASTER
    if target.exists():
        with target.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
        ids=[r.get("record_id","") for r in rows]; filepaths=[r.get("repository_path","") for r in rows]
        if len(ids)!=len(set(ids)): errors.append("معرّفات مكررة")
        if len(filepaths)!=len(set(filepaths)): errors.append("مسارات مكررة")
        for p in filepaths:
            if p and not (root/p).is_file(): errors.append("مسار غير موجود: "+p)
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path("."))
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args(); root=args.root.resolve()
    if args.write:
        (root/MASTER).parent.mkdir(parents=True,exist_ok=True)
        (root/MASTER).write_text(build_master(root),encoding="utf-8")
        (root/STATUS).write_text(build_status(root),encoding="utf-8")
        print("تم تحديث الفهارس دون حذف ملفات المصدر."); return 0
    errors=validate(root)
    if errors: print("\n".join(errors),file=sys.stderr); return 1
    print("OK: الفهارس متزامنة والمسارات والمعرّفات سليمة."); return 0

if __name__ == "__main__":
    raise SystemExit(main())
