# AI-Powered User Interview Pipeline on Dify

> 端到端的 AI 用户访谈流水线：问卷招募 → AI 初筛 → 筛选邀请 → AI 语音访谈 → 单场分析 → 综合报告。
> An end-to-end, LLM-driven user research pipeline: survey recruitment → AI screening → invitation → AI voice interview → per-interview analysis → synthesis report.

## 背景 | Background

一家头戴式耳机公司计划开拓北美市场，需要对北美用户做「健身房佩戴头戴式耳机」的访谈研究。北美真人访谈招募与执行成本高（单场激励约 $100 级），本项目验证：**用 LLM + Dify 工作流替代/加速访谈流水线中的标准化环节**，把研究员的时间留给判断与决策。

A headphone company entering the North American market needed user interviews about wearing over-ear headphones at the gym. Real interviews in NA are expensive (~$100/incentive per session). This project validates replacing the *standardizable* parts of the pipeline with LLM workflows, so researchers can focus on judgment.

## 架构 | Architecture (5 stages)

```
[Stage 1] 问卷收集 + AI 初筛          [Stage 2] 条件筛选 + 分批邀请
  Web 表单 → LLM 按硬性标准打分  ──►   研究员给筛选条件 → LLM 排序
  → 写入飞书问卷池（500人）           → 生成个性化邀请邮件（演示模式）
                                              │
[Stage 5] 综合报告                    [Stage 3] AI 语音访谈
  拉取全部分析记录 → 归一化聚合  ◄──    Chatflow 访谈员（大纲驱动、英文、
  → LLM 生成综合研究报告               一次一问、自动追问）
              ▲                        浏览器页面：Web Speech API 语音识别+朗读
              │                        → 导出逐字稿
[Stage 4] 单场访谈分析                  │
  逐字稿 → 高频词统计 + 画像提取  ──────┘
  + 关键词情感分析 + 强弱信号归类
  → 回写飞书「访谈分析库」
```

技术栈：Dify 1.17.0（自部署）· 通义千问 qwen-max · 飞书开放平台 OpenAPI（多维表格作为数据底座）· Web Speech API（浏览器原生 ASR/TTS，零额外成本）

## 各阶段设计要点 | Key Design Decisions

| Stage | 文件 | 要点 |
|---|---|---|
| 1 问卷初筛 | `dsl/stage1_survey_collection_screening.yml` | 表单提交触发 workflow；LLM 按硬性标准（拥有大耳罩、训练频率等）输出 达标/不达标 + 匹配分 + 标签 + 理由；HTTP 节点先取 tenant_access_token 再写飞书 |
| 2 筛选邀请 | `dsl/stage2_screening_invitation.yml` | 读问卷池 → 代码节点按 AI 分排序截取（规避 qwen-max 30720 输入上限）→ LLM 生成个性化邀请邮件；**演示模式**不发真邮件 |
| 3 语音访谈 | `dsl/stage3_ai_interviewer_chatflow.yml` + `demo/interview.html` | Chatflow 访谈员：大纲驱动、英文口语、一次一问、模糊回答自动追问、12-18 轮主动收尾；前端用浏览器原生 Web Speech API 做 ASR+TTS，逐字稿一键导出 |
| 4 单场分析 | `dsl/stage4_single_interview_analysis.yml` | 四路并行：代码节点高频词统计（含停用词表）、LLM 画像提取、关键词情感分析、6 项强弱信号归类（强信号/弱信号/混合/不足）；结果回写飞书分析库 |
| 5 综合报告 | `dsl/stage5_synthesis_report.yml` | 拉取全部分析记录 → 代码节点做枚举归一化（中英文漂移）、分布统计、全局高频词合并、信号强度汇总 → LLM 按固定结构出报告 |

## 验证结果 | Validation Highlights

- **6 份人格化合成逐字稿**（`demo/sample_transcripts/`）全部通过 Stage 4 分析并回写：沉浸训练型、风格展示型、音质优先型、不想塞耳型、办公通勤顺带型、偶发替代型均被正确归类
- **弱信号样本检测**：故意设计的 Tyler（US-DEN-016，耳机换来换去无忠诚度）被正确判为「偶发替代型 + 行为不稳定」，并在 Stage 5 综合报告的机会排序中被降权至末位
- **真实闭环**：Stage 3 语音页面实跑产出 `demo/live_demo_transcript.txt`（浏览器 ASR 转写 + AI 追问均正常）
- **已知局限（诚实记录）**：LLM 在综合归纳时出现过一次数值张冠李戴（把某受访者 3/7 的闷热分归入 5/7 档）——说明 AI 归纳需要人工复核，这也是方法论层面的重要发现

## 如何运行 | How to Run

1. 自部署 Dify（≥1.17），配置通义千问模型
2. 飞书开放平台创建自建应用（权限：`bitable:app`），建两张多维表格：问卷池、访谈分析库
3. 依次导入 `dsl/` 下 5 个 DSL，每个应用的环境变量填自己的 `FEISHU_APP_ID / FEISHU_APP_SECRET / FEISHU_BASE_TOKEN / FEISHU_*_TABLE_ID`
4. 每个 LLM 节点导入后需重新选择模型（DSL 不携带模型配置）
5. Stage 3：发布 Chatflow → 创建 API Key → 用 Chrome/Edge 打开 `demo/interview.html`

## 数据说明 | Data Disclaimer

仓库内**全部为合成数据**：500 份问卷由 `data/generate_synthetic_data.py` 生成，6 份逐字稿为按人格设定撰写的合成文本。不包含任何真实用户数据与原公司内部资料。

All data in this repo is **synthetic**. No real user data or proprietary company materials are included.

## 文档 | Docs

- `docs/requirements.md` — 需求确认书（5 环节原始需求）
- `docs/stage4_rebuild_tutorial.md` — Stage 4 手搓教程（可独立复现）
- `docs/interview_talking_points.md` — 项目复盘与面试叙事
