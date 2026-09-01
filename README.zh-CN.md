# Exam Hacker

[English](README.md) | 简体中文

一套面向算法型理工科期末考试、以证据为约束的生存型 Skill 合集。

Exam Hacker 不是摘要生成器，也不假装每个知识点都值得平均用力。它把真实课程资料、用户当前掌握状态和剩余时间，压成一个可以执行、可以观测、可以重规划的小闭环。优先级、战略放弃、评分和改计划都必须能回到证据。

## 为什么拆成 Skill 合集

旧版大杂烩把六种不同决策揉在一起。现在每个状态转换只有一个负责人：

| Skill | 职责 |
|---|---|
| `exam-hacker` | 读取状态，只选择一个专家，并传递已经知道的信息 |
| `exam-hacker-triage` | 审计资料、收集一分钟掌握快照、创建策略第 1 版、选择最先执行的 1–3 个 Session |
| `exam-hacker-compress` | 压缩一条算法型知识链，或用户明确指出的单个断点 |
| `exam-hacker-solve` | 完整求解一道题，或逆向还原一条可复现的解题链 |
| `exam-hacker-drill` | 执行一次隐藏答案的 Session、批改真实作答、追加掌握证据 |
| `exam-hacker-replan` | 消费新证据或可用时间变化，生成下一版策略，并选择接下来的 1–3 个 Session |

```text
triage -> [compress | solve] -> drill -> replan -> drill
```

`compress` 和 `solve` 是可选的备战操作。只有 `drill` 能把用户真实表现变成掌握证据；只有 `replan` 能修改已经存在的策略。

## 安装

### 给检测到的所有 Agent 安装完整合集

需要已经安装 Node.js，并能使用 `npx`。

```bash
npx -y skills add Wh1te358/skills-by-Wh1te -g --all
```

当前仓库只包含上面六个 Exam Hacker Skill。这里的 `--all` 是故意的：只安装 `exam-hacker` 会得到一个找不到五个下游专家的空壳路由器。

### 只安装到 Codex

如果你只需要全局安装到 Codex，或者以后仓库中出现了无关 Skill，使用显式清单：

```bash
npx -y skills add Wh1te358/skills-by-Wh1te -g -y --agent codex --skill exam-hacker exam-hacker-triage exam-hacker-compress exam-hacker-solve exam-hacker-drill exam-hacker-replan
```

只查看安装器识别到了什么，不执行安装：

```bash
npx -y skills add Wh1te358/skills-by-Wh1te --list
```

### Codex Python 备用安装

如果没有 `npx`，但 Codex 内置 Skill installer 存在，可以在一条命令中安装六个目录。不要只安装路由器。

```bash
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path exam-hacker exam-hacker-triage exam-hacker-compress exam-hacker-solve exam-hacker-drill exam-hacker-replan
```

### 从本地 clone 安装

在仓库根目录运行：

```bash
npx -y skills add . -g --all
```

安装后重启 Agent，或开启一个新会话，然后调用：

```text
$exam-hacker
```

路由器在读取课程状态前会严格检查五个专家是否安装完整。遇到缺失、格式错误或重复冲突，它会报告具体问题，不会偷偷退回已经停用的旧版大杂烩。

## 推荐课程目录

把原始证据和生成状态分开：

```text
course-root/
  reference/
    textbook/
    slides/
    review-sheet/
    homework/
    past-papers/
    answer-keys/
  progress/
    00_survival-outline.md
    strategy.json
    mastery-evidence.jsonl
    artifacts/
    drills/
    history/
```

- `reference/` 只放预先存在的原始资料。
- `progress/` 只放 Agent 生成的策略、产物、练习和追加式证据。
- 文件存在，或者 PDF 有这个文件名，不代表 Agent 已经读过它。

## 使用示例

第一次分诊：

```text
$exam-hacker
我还有 5 天考结构力学，目标 80 分，真正可用时间是 18 小时。资料都在 reference/。请先审计证据，让我输入一分钟掌握快照，然后只生成最先执行的几个 Session。
```

开始下一个 Session：

```text
$exam-hacker
开始我的下一个 Session。在我提交作答前隐藏答案。
```

直接完整解一道题：

```text
$exam-hacker-solve
把这道超静定梁题完整解成一条可复现链。引用题目、理论和答案对应的位置，并区分哪些步骤经过参考答案验证，哪些只是 Agent 推导。
```

压缩一条知识链：

```text
$exam-hacker-compress
把力法从选择基本未知量到最终内力的链条压缩出来。每一步都必须能复现，最后给一个隐藏答案的主动提取题。
```

## 证据规则

- 没有考试价值证据，就不能给出确定优先级，更不能直接战略放弃。
- 战略放弃必须同时有直接证据、容量不足、放弃代价和反转条件。
- 掌握快照是行为锚定的 `0–3` 快速自报，不是强迫用户完成一套冗长基线测试。
- 看过答案和例题只能算 `practice_only`，不能证明掌握。
- 只有用户在隐藏答案条件下的真实表现，才能进入 `mastery-evidence.jsonl`。
- OCR 和缩略图只能定位页面，不能作为公式、图表、答案或评分标记的最终证据。
- 扫描版或纯图片 PDF 会触发页面渲染和视觉读取。结论只能引用真正看过的页面；局部抽查不能冒充全文审计。

## 当前边界

当前版本专门优化计算、推导、证明和其他确定性理工科知识链。整门课 A4 小抄、泛化知识图谱、大规模题库和非算法型记忆课程压缩暂时不在范围内。宁可明确不做，也不把旧版大杂烩偷偷塞回路由器。

## 仓库内验证资产

仓库包含：

- 覆盖分诊、压缩、解题、训练和重规划的结构力学夹具；
- 策略状态、压缩产物、完整解题产物、掌握事件和重规划转换验证器；
- 闭环集成测试结果；
- 能区分文本型、混合型、扫描型和无可读信号 PDF 的检测器。
