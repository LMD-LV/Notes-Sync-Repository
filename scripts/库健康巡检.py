# -*- coding: utf-8 -*-
"""库健康巡检 —— 笔记库治理成果的常驻守护工具。

用法(在仓库根目录 D:\\Obsidian\\计算机笔记 下运行):
    PYTHONIOENCODING=utf-8 python scripts/库健康巡检.py           # 控制台报告
    PYTHONIOENCODING=utf-8 python scripts/库健康巡检.py --save    # 同时写入 00-收件箱/库健康巡检报告.md

检查项(对应《笔记库规范》的治理不变量):
    1. 断链:指向不存在文件的 [[wikilink]](90 区只读例外与设计内例外单列)
    2. frontmatter:10/20/30 区无 YAML 头的笔记
    3. 超大文件:10/20/30 区 >50KB(规范要求列入拆分计划)
    4. 未登记碎片:10/20/30 区 <500B 且 status 不是 种子/快照 的笔记
    5. 待重组残留:status: 待重组 的笔记(应为 0)

非零告警不代表必须立即处理,报告用于每周分拣时决定动作(见 [[每周分拣工作流]])。
"""
import os
import re
import sys
import datetime

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONES = ["10-学习区", "20-项目与工作", "30-个人区"]
EXCLUDE_DIRS = {".git", ".obsidian", ".claude", "scripts", "Templates"}

# 设计内例外:模板占位符 / 规范文档代码示例 / 90 区只读文件,不计入断链
KNOWN_EXCEPTIONS = {
    ("Templates", "相关技术概念1"), ("Templates", "相关技术概念2"),
    ("笔记库规范.md", "wiki链接"),
}
def is_known_exception(rel, target):
    for prefix, tgt in KNOWN_EXCEPTIONS:
        if tgt == target and (prefix in rel or rel.startswith(prefix)):
            return True
    # 90 区只读:悬空链接只登记不告警
    return rel.startswith("90-外部资料")

WIKILINK = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def collect_files():
    names, mds = set(), []
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            names.add(fn)
            names.add(os.path.splitext(fn)[0])
            if fn.endswith(".md"):
                mds.append(os.path.join(root, fn))
    return names, mds


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def has_frontmatter(text):
    return text.lstrip("\ufeff").lstrip().startswith("---")


def get_status(text):
    m = re.search(r"^status:\s*(\S+)", text, re.M)
    return m.group(1) if m else None


def check_broken(names, mds):
    issues, exceptions = [], []
    for p in mds:
        rel = os.path.relpath(p, VAULT)
        text = read(p)
        for m in WIKILINK.finditer(text):
            tgt = m.group(1).strip().split("/")[-1]
            if not tgt or tgt in names or tgt.endswith(".png"):
                continue
            if is_known_exception(rel, tgt):
                exceptions.append((rel, tgt))
            else:
                issues.append((rel, tgt))
    return issues, exceptions


def check_zone_mds(mds):
    zone_mds = []
    for p in mds:
        rel = os.path.relpath(p, VAULT)
        if rel.split(os.sep)[0] in ZONES:
            zone_mds.append((p, rel))
    return zone_mds


def main():
    names, mds = collect_files()
    report = []
    report.append(f"# 库健康巡检报告 · {datetime.date.today().isoformat()}")
    report.append(f"\n扫描 {len(mds)} 篇 md(排除 {', '.join(sorted(EXCLUDE_DIRS))})。\n")

    broken, exceptions = check_broken(names, mds)
    report.append(f"## 1. 断链: {len(broken)} 处" + (" ✅" if not broken else " ⚠️"))
    for rel, tgt in broken:
        report.append(f"- ⚠️ {rel} → {tgt}")
    if exceptions:
        report.append(f"\n(设计内例外 {len(exceptions)} 处,不处理:模板占位符/规范示例/90 区只读)")

    zone_mds = check_zone_mds(mds)
    no_fm = [(rel, p) for p, rel in zone_mds if not has_frontmatter(read(p))]
    report.append(f"\n## 2. frontmatter 缺失(10/20/30 区): {len(no_fm)} 篇" + (" ✅" if not no_fm else " ⚠️"))
    for rel, _ in no_fm:
        report.append(f"- ⚠️ {rel}")

    big = [(rel, os.path.getsize(p)) for p, rel in zone_mds if os.path.getsize(p) > 50 * 1024]
    report.append(f"\n## 3. 超大文件 >50KB: {len(big)} 篇" + (" ✅" if not big else " ⚠️(按规范列入拆分计划)"))
    for rel, size in big:
        report.append(f"- ⚠️ {rel} ({size // 1024}KB)")

    frag = []
    for p, rel in zone_mds:
        if os.path.getsize(p) >= 500:
            continue
        st = get_status(read(p))
        if st not in ("种子", "快照"):
            frag.append(rel)
    report.append(f"\n## 4. 未登记碎片 <500B(非种子/快照): {len(frag)} 篇" + (" ✅" if not frag else " ⚠️"))
    for rel in frag:
        report.append(f"- ⚠️ {rel}")

    pending = [(rel, p) for p, rel in zone_mds if get_status(read(p)) == "待重组"]
    report.append(f"\n## 5. 待重组残留: {len(pending)} 篇" + (" ✅" if not pending else " ⚠️"))
    for rel, _ in pending:
        report.append(f"- ⚠️ {rel}")

    text = "\n".join(report) + "\n"
    print(text)
    if "--save" in sys.argv:
        out = os.path.join(VAULT, "00-收件箱", "库健康巡检报告.md")
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"[已写入] {out}")


if __name__ == "__main__":
    main()
