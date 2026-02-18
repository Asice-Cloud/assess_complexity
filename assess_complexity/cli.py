import argparse
import json
from .analyzer import analyze_file


def _format_table(results):
    headers = ["Function", "Complexity", "Loops", "Calls", "Self", "Callees"]
    rows = []
    for name, info in results.items():
        callees = ", ".join(info.get("callees", []))
        rows.append([
            name,
            info.get("complexity", "" ).replace("\n", " "),
            str(info.get("loop_nesting", "")),
            str(info.get("calls", "")),
            str(info.get("self_calls", "")),
            callees,
        ])

    cols = list(zip(*([headers] + rows))) if rows else [[h] for h in headers]
    widths = [max(len(str(x)) for x in col) for col in cols]

    sep = " | "
    line_hdr = sep.join(h.ljust(w) for h, w in zip(headers, widths))
    line_sep = "-+-".join("-" * w for w in widths)
    lines = [line_hdr, line_sep]
    for r in rows:
        lines.append(sep.join(str(c).ljust(w) for c, w in zip(r, widths)))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Assess complexity for C/C++ source file")
    p.add_argument("file", help="C/C++ source file to analyze")
    p.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = p.parse_args()
    res = analyze_file(args.file)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(_format_table(res))


if __name__ == "__main__":
    main()
