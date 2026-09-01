# One-Minute Mastery Snapshot

Use this workflow to capture current ability without blocking urgent study.

## Topic List

Typically extract 8–15 topics from readable materials. In urgent mode, prefer the 8–12 topics with strongest exam-value or prerequisite evidence. If fewer verified topics exist, use only those and state that coverage is incomplete.

Assign stable topic IDs matching `knowledge_graph.nodes[].id`. The Agent builds this list; the user does not reconstruct the syllabus.

## User Reply

Use the user's language:

```text
用 0–3 回填，不需要先做题：
0 = 完全空白／认不出方法
1 = 看答案能懂，但闭卷不能复现
2 = 能独立完成标准题／说出关键步骤
3 = 能限时完成变式，并解释适用条件

T01 [主题]：
T02 [主题]：

直接回复：T01:2 T02:0
最近相关小测、作业或模考结果可选填。
```

Reuse target score, exam date, and availability already provided. Do not ask for percentages.

## Evidence Strength

From strongest to weakest:

1. recent timed or graded work on the same topic;
2. closed-book micro-probe;
3. behavior-anchored self-report;
4. `unknown`.

Record topic ID, level, evidence type, evidence reference, confidence, observation time, and notes. Do not upgrade self-report into demonstrated mastery.

## Urgent Mode

When three days or less remain or the user says every minute matters:

- keep the reply task near one minute;
- do not require a separate 20–30 minute diagnostic;
- use the first real Session as ongoing calibration;
- update later when performance contradicts self-report.

## Selective Micro-Probe

Use one 2–5 minute answer-hidden probe only when:

1. the topic has high exam-value or prerequisite evidence;
2. the user reports level `2` or `3`;
3. that report would cause the topic to be deferred or skipped;
4. a wrong report could cost meaningful marks;
5. a short representative task can resolve the uncertainty.

Do not probe every topic. If the user declines, keep lower confidence and a reversal condition.

## Missing Response

If the user skips the snapshot, mark mastery `unknown`, issue only a provisional route, and do not justify abandonment from missing mastery evidence.
