# Exam Hacker 使用说明

`exam-hacker` 是一个期末速通 Skill，用来把零散复习资料转成目标分数导向的复习作战包。它不追求“把一门课学完整”，而是帮助你判断：剩下的时间里，哪些内容必须拿下，哪些内容应该放弃，哪些知识点会被综合题串起来考。

## 适用场景

- 期末前 2-14 天，需要快速制定复习路线。
- 手里有教材、PPT、老师划重点、作业、真题、答案、学长笔记等资料。
- 资料不完整，最差情况只有教材和几张复习课 PPT 拍照。
- 想生成 `生存大纲`、`概念压缩`、`真题逆向拆解`、`知识连接图`、`A4 小抄`。
- 理工科综合题总是会单个知识点，但不会把知识点串起来。

## 本地安装

把 skill 文件夹放到 Codex 的 skills 目录：

```powershell
$src = "C:\Users\ASUS\Documents\New project 2\exam-hacker"
$dst = "C:\Users\ASUS\.codex\skills\exam-hacker"

New-Item -ItemType Directory -Force -Path "$dst\agents" | Out-Null
Copy-Item -LiteralPath "$src\SKILL.md" -Destination "$dst\SKILL.md" -Force
Copy-Item -LiteralPath "$src\agents\openai.yaml" -Destination "$dst\agents\openai.yaml" -Force
```

安装后重启 Codex。重启后可用：

```text
$exam-hacker
```

## GitHub 安装

如果仓库结构是：

```text
skills-by-Wh1te/
  exam-hacker/
    SKILL.md
    agents/
      openai.yaml
```

则安装命令应为：

```powershell
python C:\Users\ASUS\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --url "https://github.com/Wh1te358/skills-by-Wh1te/tree/main/exam-hacker"
```

如果当前 skill 还在旧路径：

```text
skills-by-Wh1te/
  skills/
    exam-hacker/
      SKILL.md
```

则安装命令是：

```powershell
python C:\Users\ASUS\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --url "https://github.com/Wh1te358/skills-by-Wh1te/tree/codex/exam-hacker-skill/skills/exam-hacker"
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
