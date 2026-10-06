"""Offline analysis for GUIDE 6e; consumes original round 1 and two extra rounds.
Run from repository root: python report/phase6/analyze_noise.py
No model calls, source modifications or result rewrites.
"""
import hashlib
import json
import statistics
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report" / "phase6"
CONDITIONS = ("baseline", "subagents", "skills-auto")
TASKS = ("code-eval", "data-eval", "logs-eval")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    protocol = json.loads((OUT / "protocol.json").read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "report" / "phase4_protocol.json").read_text(encoding="utf-8"))
    for group in ("original_result_sha256", "skill_sha256"):
        for filename, expected in protocol[group].items():
            if digest(ROOT / filename) != expected:
                raise SystemExit("Protected artifact changed: " + filename)
    records = []
    missing = []
    for round_number in (1, 2, 3):
        folder = ROOT / "results" if round_number == 1 else ROOT / "results" / "noise" / f"round-{round_number}"
        for condition in CONDITIONS:
            for task in TASKS:
                path = folder / condition / task / "run.json"
                trace = path.with_name("trace.md")
                if not path.exists() or not trace.exists():
                    missing.append(str(path.relative_to(ROOT)))
                    continue
                record = json.loads(path.read_text(encoding="utf-8"))
                if (record["condition"], record["task"], record["role"]) != (condition, task, "eval"):
                    raise SystemExit("Invalid record identity: " + str(path))
                if record["tokens"]["input"] + record["tokens"]["output"] != record["tokens"]["total"]:
                    raise SystemExit("Invalid token total: " + str(path))
                if record["passed"] != sum(bool(check["passed"]) for check in record["checks"]):
                    raise SystemExit("Invalid check count: " + str(path))
                if abs(record["score"] - record["passed"] / record["total"]) > 1e-12:
                    raise SystemExit("Invalid score: " + str(path))
                if datetime.fromisoformat(record["timestamp"]) <= datetime.fromisoformat(frozen["freeze_time"]):
                    raise SystemExit("Run started before freeze: " + str(path))
                if condition == "skills-auto" and record["skills_sha256"] != frozen["skills_sha256_linux"]:
                    raise SystemExit("Unexpected frozen skills: " + str(path))
                if any(check["detail"] for check in record["checks"]):
                    raise SystemExit("Evaluation feedback is not hidden: " + str(path))
                records.append({"round": round_number, "path": str(path.relative_to(ROOT)), **record})
    if missing:
        raise SystemExit(f"Incomplete experiment: {len(missing)} records missing; no repeated-run statistics written.")

    summaries = {}
    rows = ["| Điều kiện | Tác vụ | Lượt 1 | Lượt 2 | Lượt 3 | Trung bình (%) | Min–max (%) | SD (điểm %) |",
            "|---|---|---:|---:|---:|---:|---:|---:|"]
    for condition in CONDITIONS:
        selected = [r for r in records if r["condition"] == condition]
        task_stats = {}
        for task in TASKS:
            rs = [r for r in selected if r["task"] == task]
            scores = [r["score"] for r in rs]
            stat = {"scores": scores, "passed": [r["passed"] for r in rs], "total": rs[0]["total"],
                    "mean": statistics.mean(scores), "min": min(scores), "max": max(scores),
                    "sample_sd": statistics.stdev(scores)}
            task_stats[task] = stat
            counts = " | ".join(f"{r['passed']}/{r['total']}" for r in rs)
            rows.append(f"| {condition} | {task} | {counts} | {stat['mean']*100:.2f} | "
                        f"{stat['min']*100:.2f}–{stat['max']*100:.2f} | {stat['sample_sd']*100:.2f} |")
        round_means = [statistics.mean(r["score"] for r in selected if r["round"] == n) for n in (1, 2, 3)]
        summaries[condition] = {
            "tasks": task_stats, "round_means": round_means, "mean_score": statistics.mean(round_means),
            "round_min": min(round_means), "round_max": max(round_means), "round_sample_sd": statistics.stdev(round_means),
            "mean_tokens": statistics.mean(r["tokens"]["total"] for r in selected),
            "mean_seconds": statistics.mean(r["seconds"] for r in selected),
            "total_tokens": sum(r["tokens"]["total"] for r in selected),
            "runs_reading_skills": sum(r["skills_read"] > 0 for r in selected),
            "total_subagent_calls": sum(r["subagent_calls"] for r in selected),
            "technical_passed": sum(check["passed"] for r in selected for check in r["checks"] if not check["name"].startswith("rule_")),
            "technical_total": sum(1 for r in selected for check in r["checks"] if not check["name"].startswith("rule_")),
            "rules_passed": sum(check["passed"] for r in selected for check in r["checks"] if check["name"].startswith("rule_")),
            "rules_total": sum(1 for r in selected for check in r["checks"] if check["name"].startswith("rule_")),
        }
    failures = [{"path": r["path"], "error": r["error"], "skills_modified": r["skills_modified"]}
                for r in records if r["error"] is not None or r["skills_modified"]]
    summary = {"records": len(records), "additional_records": 18, "conditions": summaries,
               "additional_tokens": sum(r["tokens"]["total"] for r in records if r["round"] > 1),
               "failures": failures, "protected_artifacts_unchanged": True}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "table.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    aggregate = ["| Điều kiện | Trung bình (%) | Min–max trung bình lượt (%) | SD giữa lượt (điểm %) | Token/lần | Giây/lần | Lần đọc skill |",
                 "|---|---:|---:|---:|---:|---:|---:|"]
    for condition, stat in summaries.items():
        aggregate.append(f"| {condition} | {stat['mean_score']*100:.2f} | "
                         f"{stat['round_min']*100:.2f}–{stat['round_max']*100:.2f} | "
                         f"{stat['round_sample_sd']*100:.2f} | {stat['mean_tokens']:,.2f} | "
                         f"{stat['mean_seconds']:.2f} | {stat['runs_reading_skills']}/9 |")
    (OUT / "aggregate.md").write_text("\n".join(aggregate) + "\n", encoding="utf-8")
    print(f"NOISE_ANALYSIS_OK: {len(records)} records, {len(failures)} flagged runs; original results and skills unchanged")


if __name__ == "__main__":
    main()
