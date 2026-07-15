# Exam Hacker 使用说明

`exam-hacker` 是一个期末速通 Skill，用来把零散复习资料转成目标分数导向的复习作战包。它不追求“把一门课学完整”，而是帮助你判断：剩下的时间里，哪些内容必须拿下，哪些内容应该放弃，哪些知识点会被综合题串起来考。

## 适用场景

- 期末前 2-14 天，需要快速制定复习路线。
- 手里有教材、PPT、老师划重点、作业、真题、答案、学长笔记等资料。
- 资料不完整，最差情况只有教材和几张复习课 PPT 拍照。
- 想生成 `生存大纲`、`概念压缩`、`真题逆向拆解`、`知识连接图`、`A4 小抄`。
- 理工科综合题总是会单个知识点，但不会把知识点串起来。

## GitHub 安装（推荐）

推荐 GitHub 浏览路径：

```text
https://github.com/Wh1te358/skills-by-Wh1te/tree/codex/exam-hacker-skill/exam-hacker
```

在 Windows PowerShell 里直接运行：

```powershell
py -3 "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path "exam-hacker"
```

如果你的电脑没有 `py`，把命令开头的 `py -3` 换成 `python`。

你也可以直接告诉你的 Agent：帮我安装这个 Skill，GitHub 链接为 `https://github.com/Wh1te358/skills-by-Wh1te/tree/codex/exam-hacker-skill/exam-hacker`。

不要把上面的 GitHub 浏览路径直接传给 `--url`。这个分支名 `codex/exam-hacker-skill` 里带 `/`，部分安装脚本会把 ref 错解析成 `codex`，导致下载失败并回退到 SSH clone。

安装后重启 Codex。重启后调用：

```text
$exam-hacker
```

## macOS / Linux 安装

如果 macOS 用户使用 PowerShell 7（`pwsh`），也可以直接运行上面的 PowerShell 命令。

如果使用普通终端（zsh/bash），运行：

```bash
python3 "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo "Wh1te358/skills-by-Wh1te" \
  --ref "codex/exam-hacker-skill" \
  --path "exam-hacker"
```

安装后重启 Codex。

如果仓库还没有完成目录迁移，旧路径也不要用 `--url`，改用：

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path "skills/exam-hacker"
```

## 本地安装（已下载仓库时）

如果已经把仓库 clone 到本地，并且当前目录就是仓库根目录，可以用下面的 PowerShell 命令安装。

它会自动兼容两种目录：

```text
exam-hacker/
skills/exam-hacker/
```

```powershell
$ErrorActionPreference = "Stop"

$root = Get-Location
$src = Join-Path $root "exam-hacker"
if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
  $src = Join-Path $root "skills/exam-hacker"
}
if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
  throw "没有找到 exam-hacker/SKILL.md 或 skills/exam-hacker/SKILL.md。请先 cd 到仓库根目录。"
}

$dst = Join-Path $HOME ".codex/skills/exam-hacker"
New-Item -ItemType Directory -Force -Path (Join-Path $dst "agents") | Out-Null
Copy-Item -LiteralPath (Join-Path $src "SKILL.md") -Destination (Join-Path $dst "SKILL.md") -Force
Copy-Item -LiteralPath (Join-Path $src "agents/openai.yaml") -Destination (Join-Path $dst "agents/openai.yaml") -Force

Write-Host "Installed exam-hacker to $dst"
Write-Host "Restart Codex, then invoke with: `$exam-hacker"
```

## 推荐资料结构

开始前，把每门课的复习资料单独放一个文件夹：

```text
course-root/
  reference/
    textbook/
    ppt/
    photos/
    homework/
    past-papers/
    answer-keys/
    senior-notes/
  progress/
```

规则：

- `reference/` 只放原始资料。
- `progress/` 只放 Agent 生成的文档。
- 不要把 AI 生成内容和原始证据混在一起。

## 调用方式

示例 1：完整分诊

```text
$exam-hacker
我还有 5 天考结构力学，目标 80+。资料在 reference 文件夹里，有教材、老师划重点 PPT 照片、几套作业，没有真题。请先做考试分诊。
```

示例 2：生成知识连接图

```text
$exam-hacker
根据结构力学 deflection 这一章，生成知识节点表、知识连接图和综合题型地图。重点看综合题怎么把弯矩方程、边界条件、位移计算串起来。
```

示例 3：真题逆向拆解

```text
$exam-hacker
这是一道往年题和参考答案。不要先讲知识点，直接逆向拆解：第一步写什么，公式从哪来，哪里能拿步骤分，哪里最容易断链。
```

示例 4：考前三天保命

```text
$exam-hacker
我只剩 3 天，目标及格。资料只有教材和复习课 PPT 照片。请不要给完整学习计划，只给保命路线、必背公式、战略放弃清单和考场捞分策略。
```

## 输出文件

Skill 默认生成这些 Markdown 产物：

```text
progress/
  00_生存大纲.md
  [章节]_概念压缩.md
  [题型]_逆向拆解.md
  04_知识节点表.md
  05_知识连接图.md
  06_综合题型地图.md
  [章节]_A4小抄.md
```

## 核心阶段

### 阶段 0：资料隔离与考试分诊

确认科目类型、目标分数、剩余时间、资料质量，并判断目标是否现实。

如果只剩 2 天却想考 90+，Skill 应直接提醒目标不合理，而不是陪你做梦。

### 阶段 1：概念压缩

数理型课程用参数测试：

- 归零 / 无穷测试
- 逆向测试
- 极端边界测试

记忆型课程用踩分关键词：

- 剥掉废话
- 保留 3-5 个得分关键词
- 用自己的话扩写

### 阶段 2：真题逆向工程

不从“知识点解释”开始，而从答案和得分点倒推：

- 哪个公式先写能拿步骤分
- 题目触发词对应哪个操作
- 哪一步最容易卡死
- 完全不会时最低限度写什么

### 阶段 3：知识连接图谱

这是 `exam-hacker` 的核心差异。

普通 AI 会列知识点，但理工科考试常考“知识点之间的边”。例如结构力学里，题目可能表面问位移，实际链条是：

```text
荷载识别 -> 支座反力 -> 弯矩方程 -> EI v'' = M -> 边界条件 -> 最大挠度
```

Skill 必须输出：

- `04_知识节点表.md`
- `05_知识连接图.md`
- `06_综合题型地图.md`

如果只输出知识点清单，没有连接关系，本轮任务视为失败。

### 阶段 4：A4 小抄

不是为了作弊，而是强迫大脑压缩。

数理型输出：

- 公式清单
- 第一反应
- 边界条件
- 计算坑点
- 捞分句

记忆型输出：

- 踩分关键词
- 答题骨架
- 语义平替
- 考前触发词

## 使用原则

- 目标分数由用户设定，但 Skill 必须判断现实性。
- 资料越少，预测越保守。
- 没有真题时，不要假装能精准预测。
- 分数导向优先于完整学习。
- 理工科综合题优先画知识连接，不要只背孤立公式。
- 低频高成本内容可以直接放弃。

## 一句话版本

`exam-hacker` 不是学习助手，是期末考试的分数工程师：先分诊，再压缩，再逆向真题，最后把孤立知识点串成能上考场的解题链。

---

# Exam Hacker User Guide

`exam-hacker` is a final-exam cram Skill that turns scattered course materials into a target-score survival package. It does not try to help you "learn the whole course." It helps you decide what must be secured, what should be abandoned, and which concepts are likely to be connected in integrated exam problems.

## When To Use It

- You are 2-14 days away from a final exam and need a fast review route.
- You have materials such as a textbook, PPTs, teacher-highlighted review notes, homework, past papers, answer keys, or senior-student notes.
- Your materials are incomplete. The worst valid case is only a textbook and several photos of a review-session PPT.
- You want to generate a survival outline, concept compression notes, reverse-engineered past-paper breakdowns, knowledge connection maps, or A4 cheat-sheet-style compression notes.
- In STEM subjects, you can understand isolated concepts, but fail when exam problems connect them.

## GitHub Installation (Recommended)

Recommended GitHub browsing path:

```text
https://github.com/Wh1te358/skills-by-Wh1te/tree/codex/exam-hacker-skill/exam-hacker
```

Run this directly in Windows PowerShell:

```powershell
py -3 "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path "exam-hacker"
```

If `py` is not available on your machine, replace `py -3` with `python`.

You can also tell your Agent directly: install this Skill for me. The GitHub link is `https://github.com/Wh1te358/skills-by-Wh1te/tree/codex/exam-hacker-skill/exam-hacker`.

Do not pass the GitHub browsing URL directly to `--url`. The branch name `codex/exam-hacker-skill` contains `/`, and some installer scripts may incorrectly parse the ref as `codex`, which causes download failure and fallback to SSH clone.

Restart Codex after installation. Then invoke:

```text
$exam-hacker
```

## macOS / Linux Installation

If macOS users run PowerShell 7 (`pwsh`), they can use the same PowerShell command above.

If using a normal terminal such as zsh or bash, run:

```bash
python3 "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo "Wh1te358/skills-by-Wh1te" \
  --ref "codex/exam-hacker-skill" \
  --path "exam-hacker"
```

Restart Codex after installation.

If the repository has not completed the directory migration yet, do not use `--url`; use:

```powershell
python "$HOME\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path "skills/exam-hacker"
```

## Local Installation (If The Repo Is Already Downloaded)

If the repository has already been cloned locally and the current directory is the repository root, install with the following PowerShell command.

It supports both possible layouts:

```text
exam-hacker/
skills/exam-hacker/
```

```powershell
$ErrorActionPreference = "Stop"

$root = Get-Location
$src = Join-Path $root "exam-hacker"
if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
  $src = Join-Path $root "skills/exam-hacker"
}
if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
  throw "Could not find exam-hacker/SKILL.md or skills/exam-hacker/SKILL.md. cd to the repository root first."
}

$dst = Join-Path $HOME ".codex/skills/exam-hacker"
New-Item -ItemType Directory -Force -Path (Join-Path $dst "agents") | Out-Null
Copy-Item -LiteralPath (Join-Path $src "SKILL.md") -Destination (Join-Path $dst "SKILL.md") -Force
Copy-Item -LiteralPath (Join-Path $src "agents/openai.yaml") -Destination (Join-Path $dst "agents/openai.yaml") -Force

Write-Host "Installed exam-hacker to $dst"
Write-Host "Restart Codex, then invoke with: `$exam-hacker"
```

## Recommended Material Structure

Before starting, put the review materials for each course into a separate folder:

```text
course-root/
  reference/
    textbook/
    ppt/
    photos/
    homework/
    past-papers/
    answer-keys/
    senior-notes/
  progress/
```

Rules:

- `reference/` contains only raw materials.
- `progress/` contains only Agent-generated documents.
- Do not mix AI-generated content with raw evidence.

## Invocation Examples

Example 1: Full triage

```text
$exam-hacker
I have 5 days before my structural mechanics exam, and my target is 80+. The materials are in the reference folder. I have the textbook, photos of the teacher's highlighted review PPT, and several homework sets, but no past papers. Start with exam triage.
```

Example 2: Generate a knowledge connection map

```text
$exam-hacker
For the deflection chapter in structural mechanics, generate the knowledge node table, knowledge connection graph, and integrated problem map. Focus on how integrated problems connect bending moment equations, boundary conditions, and displacement calculations.
```

Example 3: Reverse-engineer a past-paper problem

```text
$exam-hacker
Here is a past-paper problem and its reference answer. Do not start by explaining concepts. Reverse-engineer it directly: what should be written first, where the formula comes from, where process marks can be secured, and where the reasoning chain usually breaks.
```

Example 4: Three-day survival mode

```text
$exam-hacker
I only have 3 days left, and my target is to pass. My materials are only a textbook and photos of a review-session PPT. Do not give me a complete study plan. Give me a survival route, must-memorize formulas, strategic abandonment list, and exam-room fallback strategy.
```

## Output Files

The Skill commonly generates these Markdown artifacts:

```text
progress/
  00_survival-outline.md
  [chapter]_concept-compression.md
  [problem-type]_reverse-engineering.md
  04_knowledge-node-table.md
  05_knowledge-connection-map.md
  06_integrated-problem-map.md
  [chapter]_a4-compression.md
```

## Core Phases

### Phase 0: Material Isolation And Exam Triage

Confirm the subject type, target score, remaining time, and material quality, then judge whether the target is realistic.

If only 2 days remain and the user wants 90+, the Skill should directly say the target is unreasonable instead of pretending it is feasible.

### Phase 1: Concept Compression

For math/logic-heavy courses, use parameter testing:

- zero / infinity test
- reverse test
- extreme-boundary test

For memorization-heavy courses, use scoring keywords:

- strip away filler
- keep 3-5 scoring keywords
- expand them in the user's own words

### Phase 2: Past-Paper Reverse Engineering

Do not start from concept explanation. Start from the answer and scoring points:

- which formula should be written first to secure process marks
- which problem trigger words map to which operation
- which step is most likely to break
- what to write at minimum if the user blanks out

### Phase 3: Knowledge Connection Map

This is the core difference of `exam-hacker`.

Generic AI can list concepts, but STEM exams often test the edges between concepts. For example, in structural mechanics, a problem may appear to ask for displacement, but the actual chain is:

```text
load identification -> support reactions -> bending moment equation -> EI v'' = M -> boundary conditions -> maximum deflection
```

The Skill must output:

- `04_knowledge-node-table.md`
- `05_knowledge-connection-map.md`
- `06_integrated-problem-map.md`

If it only outputs an isolated knowledge list without connections, the round is considered failed.

### Phase 4: A4 Compression

This is not for cheating. It forces compression.

For math/logic-heavy subjects, output:

- formula list
- first reactions
- boundary conditions
- calculation traps
- fallback scoring lines

For memorization-heavy subjects, output:

- scoring keywords
- answer skeletons
- semantic substitutes
- pre-exam trigger words

## Usage Principles

- The user sets the target score, but the Skill must judge whether it is realistic.
- The weaker the materials, the more conservative the prediction.
- Without past papers, do not pretend to predict the exam precisely.
- Score orientation takes priority over complete learning.
- For STEM integrated problems, prioritize knowledge connections instead of isolated formulas.
- Low-frequency, high-cost content can be abandoned directly.

## One-Sentence Version

`exam-hacker` is not a study assistant. It is a final-exam score engineer: triage first, compress second, reverse-engineer past papers third, then connect isolated concepts into exam-ready solution chains.
