---
layer: mixed
paths:
  - "drafts of outbound WeChat / WeCom / email / messaging content"
applies-to: any AI-drafted outbound message (NOT business docs — those are Register B/C territory, see biz-doc-critic agent)
companion-rules:
  - "[[09 Rules/file-types.md]]"
  - "[[09 Rules/internal-briefing.md]]"  # 内部汇报 archetype, different register
  - "[[MEMORY.md]]"  # base voice principles
created: 2026-05-14
created-by: claude
audit-trace: "{{USER_NAME}} request 2026-05-14 — tone calibration for messaging spectrum (casual WeChat ↔ formal govt WeChat ↔ WeCom middle)"
---

# Message Tone Calibration Rules · 消息语域校准

> **Register A 系列**（messaging）— 与 Register B/C（business document body / executive summary）**互补不重叠**。biz-doc-critic 管 B/C；本规则管 A。Skills 起草 WeChat / WeCom / 邮件 时**先 calibrate register**，再下笔。

## Why this exists

{{USER_NAME}} observation 2026-05-14:
> "WeChat 等即时通讯类消息，通常更随意亲切，even with external partners use actual WeChat messages to analyze tones and understand. But there are cases where being more professional is crucial, with high level execs and government officials, on high urgency and high stakes topics. Wecom is somewhere in between, also generally more casual but clear."

→ Message tone is **not single** — depends on 4 axes：
1. **Medium** (WeChat / WeCom / 邮件)
2. **Relationship intimacy** (peer ↔ 上下级 ↔ 不熟 ↔ 政企 / govt)
3. **Stakes** (low routine ↔ high urgency / high stakes / 战略决定)
4. **Direction** (peer-to-peer / 上行 / 下行 / external partner)

不同 axes 组合产生不同 register。**统一一种 tone 是错的** — {{PERSON_5}}场 WeChat ≠ {{PERSON}}汇报 ≠ 政府副局长邮件。

## Register A 矩阵

### A1 · WeChat 1-on-1 · 熟人 / Peer / 低 stakes (default external partner)

**典型场景**: 跟{{PERSON_4}} / {{PERSON_5}} / 47 / 林芳羽 等已经熟悉的 BD 对接人日常聊节奏 / 顺一件事 / 同步状态。

**特征**:
- 长度: 1-3 行 ideal, 极少 > 6 行
- 称呼: "X 哥" / "X 姐" / "Bubble" / "{{PERSON_4}}哥" / first name + 哥姐 / 极熟可以直 first name
- 抬头/落款: **无**（消息流自带 context）
- emoji: 1-2 个 inline, 不滥用。`👍 / 🙏 / 哈哈` OK；不发整段表情
- 句式: 短句 + 省略主语 ("收到，回头看下" 而不是 "我收到了，回头我会看一下")
- 连接词: "嗯 / 啊 / 哎 / 好嘞"（语气词 OK）
- 时态: 模糊 ("回头 / 一会儿 / 这两天")
- bilingual mix 自然: "概要 / pivot / leverage / OKR" 之类技术词夹中文
- action ask: **一条消息一个 ask** — 多 ask 拆消息
- 商务议题: 直接但留余地 ("看看你方便不")
- 互动信号: "～" 波浪号偶尔 OK (亲切感) · 不长串
- 标点: 中文逗号 / 中文句号 / 问号 mix OK；ellipsis "..." 表 trailing 思绪

**Example**:
```
{{PERSON_4}}哥, 刚才聊到 Tiff 那个口子让我惦记 — 5/19-21 SH 想约你坐下来 1h 聊聊 (
带最新包体). 5/19 PM 16:00 之前我都行, 你看哪个时段
```

**禁忌**:
- ❌ "Dear X, ... Best regards" 式 boilerplate
- ❌ 全 emoji 装可爱 (😄😄😄)
- ❌ 长段落 (≥4 行不分段)
- ❌ 文绉绉书面词 ("此致 / 烦请 / 兹有")
- ❌ "您" 用于 peer (升 register 用 A4)

---

### A2 · WeChat 1-on-1 · 不熟 / 第一次接触

**典型场景**: 经人引荐第一次加微信；通过 conference / 活动加上的 ; cold outreach。

**特征**:
- 长度: 2-4 行 (比 A1 略长 — 需 context)
- 称呼: "X 总好" / "X 老师好" / "X 姐好"（先用尊称，等对方降 register 后再 follow）
- 抬头: 一行身份 + 引荐 source ("XX 介绍过来" / "刚才会议上加的")
- 落款: 无 (消息流) 或 "—— {{USER_NAME}} · {{PROJECT_A}} BD" 一行 if 第一条触达
- emoji: 接近无 (1 个 🙏 OK)
- 句式: 完整句 + 主语 ("我是诗悦/{{PROJECT_A}}的 {{USER_NAME}}" 不是 "诗悦{{PROJECT_A}} {{USER_NAME}}")
- 时态: 具体 ("下周二上午 / 5/20 PM")
- bilingual: 谨慎 — bilingual mix 默认 OK 但避免高频英文
- action ask: 单 ask + 明确价值
- 留余地: "看您方便 / 不勉强"

**Example**:
```
张总好，我是诗悦/{{PROJECT_A}}的 {{USER_NAME}}。{{ORG_B}} 那边 何宗寰 老师转过 contact 给我。

听说您下月会到广州，想约个 30-min 咖啡聊聊 — 我们这边在 M&A 角度
有一个想法可能跟 {{ORG_D}} 的 sourcing 角度对得上。

您方便时回我个时段就行，不急。

—— {{USER_NAME}} · 诗悦网络 / {{ORG_B}} M&A advisor
```

**禁忌**:
- ❌ Cold pitch 直接砸方案 (没建立关系)
- ❌ "我们能给你 X" 客户视角 frame（你给对方 → 对方给你 = 资源 barter，但措辞要客户视角）
- ❌ 时效紧迫 ("速回 / 紧急") 除非真紧急

---

### A3 · WeChat 1-on-1 · 高 stakes (高管 / 政企 / govt / 重大议题)

**典型场景**: 与政府文旅局 / 街道办主任 / 国资委层级 / 国央企 high-level / 外部CEO级人物 / 律师 / 财务总监 等。stakes 高、容错低、措辞 careful。

**特征**:
- 长度: 3-6 行 ideal (相对 A1 长，因为 information density + 礼貌 buffer)
- 称呼: 职位 + 姓 ("张主任 / 李书记 / 周老师") + "您好" / "好"
- 抬头: 短身份 reminder + 议题 anchor ("我是诗悦网络的 {{USER_NAME}}，上次 EPIC 峰会您说过的...")
- 落款: "—— {{USER_NAME}} · 诗悦网络 / {{PROJECT_A}} BD"
- emoji: **极少 (0-1)** — 仅 🙏 用于诚意
- 句式: 完整 + 主语 + 客气词；**"您"替代"你"** throughout
- 礼貌词:
  - "请教" 替代 "问"
  - "麻烦" / "烦请" / "敬请"
  - "向您汇报" / "向您 update"
  - "请您指点"
- 时效: implicit ("方便时" "不急" "您 schedule 允许时")
- 表态: ambiguous on commitments ("初步看 / 大致方向是 / 我们的理解是")
- 拒绝/否定: 不直接 ("可能需要再 align 一下" 替代 "不行 / 不可以")
- bilingual: **大幅缩** — 中文 monolingual 为主，仅在术语必要时插英文（{{ORG_D}} / IPO / etc.）
- bullet/分行: 可以 (帮助阅读) 但每行不超 20 字

**Example**:
```
张主任好，我是诗悦网络的 {{USER_NAME}}。

关于上次您提到的 5/15 文旅局对接事宜，我们这边初步整理了一份背景材料 — 想请教您几个问题：

1. 文旅产业基金对外资 LP 的开放程度，是否有具体的范围限制
2. 我们若以 LP 身份参与，是否需要本地实体落地，还是境内主体即可

如果您 schedule 允许，希望约一次 30-min 当面汇报 — 时点您来定，我们配合您的时间。

—— {{USER_NAME}} · 诗悦网络 / {{PROJECT_A}} BD
```

**禁忌**:
- ❌ "哥/姐" 称呼 (不熟 + 高级别 → 失礼)
- ❌ "嗯 / 啊 / 哎" 语气词
- ❌ "~" 波浪号 / "~呗 / 啊" 等亲昵尾音
- ❌ 直接 "不行 / 没法做"
- ❌ 时间 imperative ("您必须 / 您一定")
- ❌ 多 ask 同消息 (砍到 1-2 个 max, ask 分明)

---

### A4 · WeCom 1-on-1 · 内部 + 跨团队 (default work register)

**典型场景**: 诗悦 / {{ORG_C}}发行内部跨组沟通 ({{USER_NAME}} → 小K / 煎饼 / 一一 / {{PERSON_1}} / 等) · 大客户 enterprise 对接人 · 长期供应商。

**特征**:
- 长度: 2-5 行 (介于 A1 和 A3 之间)
- 称呼: 内部用 "X 姐 / 哥" OR 花名 / first name；跨公司用 "X 总 / 老师"
- 抬头: 通常无 (work 同事 default 知 context)
- 落款: 无
- emoji: 工作 emoji OK (👍🙏👌)，少用 character emoji (😄😎)
- 句式: 工作 voice — 不滥语气词但允许 "顺一下 / 走起 / 搞一下"
- bilingual mix: 自然 (内部默认双语 OK)
- action ask: 可以 2-3 个 if related，但**编号**列清 ("(1) ... (2) ...")
- 时效信号: 明示 ("今天 EOD 前 / 周三前 / 这周")
- 件 / 附件: 显式 ("文件已发, 重点看 § 3" 而不是默认对方会找)
- 流程化: "走 X 流程 / 找 Y 对一下口径"

**Example**:
```
小K，5/14 沪差 Day 1 EPIC 峰会 intake 我抓了 2 个 takeaway，
正在落档 02 Cards/{{PROJECT_A}}/ 下。

烦你看下：
(1) UE 5.8 闭门路线图 — {{PROJECT_A}} Q3 引擎评估输入
(2) 中国 EPIC BD (Tiff / Robin) 已建立 in-person 通道

具体落档完后 @你 review，预计 5/15 下午回穗后。

另：5/19 SH {{PERSON_5}}场 B 站 4 线全口径 lineup，KOL 资源置换议题归你这边
— 我那边带个 talking point 出来，回穗后过你审。
```

**禁忌**:
- ❌ 全英文段 (内部 default CN, EN 是术语层)
- ❌ "Dear" / "Sincerely" 西式 boilerplate
- ❌ 跨 5 行不分段
- ❌ 隐藏 action ask (要明示)

---

### A5 · WeCom 群 / Email · 内部跨组通报 / 外部 enterprise (semi-formal)

**典型场景**: {{PROJECT_A}}项目组 12 人管理层群通报 · 跨部门项目沟通 · 半正式邮件 (中间 stake 客户 / 中级别政企 / 中等 stake 供应商) · 月报 / 阶段性 update。

**特征**:
- 长度: 5-15 行 (允许结构化)
- 称呼: 群 — "各位 / 大家好" · 邮件 — "X 总 / X 老师 / 各位"
- 抬头: 邮件必有 (主题行 + 收件人 cc)；群通报顶部 1 行 概要
- 落款: 邮件 — "{{USER_NAME}} · 诗悦网络 / {{PROJECT_A}} BD"；群 — 无
- emoji: 极少 (0-1) — 群里 emoji 看场合
- 句式: 半正式 — 主语全 / 时态明确 / 礼貌词 occasional
- bilingual: 中文主，英文术语层
- 结构: 允许 / 鼓励 — bullet / 表格 / 标题 (3 行段 OK)
- action ask: 编号 + 责任人 + 截止日 ("请 X 在 5/16 前 review")
- 时效: 明示且 enforceable
- 文件: 显式 frame + 焦点指引

**Example WeCom 群**:
```
各位，关于 5/19 SH 出差 B 站 4 线全口径会面安排，简短同步：

时间: 5/19 14:00-18:00 (4 小时连场 — 14:00 {{PERSON_5}}全口径 + 16:00 47 商业化 deep dive)
对接人: {{PERSON_5}} (B 站游戏合作部 · 联运商务负责人) + 47 (营销中心·直客)
我方阵容: {{USER_NAME}} 单人 (小K / 煎饼 不去 SH, 改 5/25-26 厦门)

{{PERSON}}: 请您 sign-off 73 分谈判 fallback ladder — 推荐 65 floor + 句式见 [[(C) 沪差0518 内部汇报-{{PERSON}}]] § Q2
小K / 煎饼: 5/25-26 厦门 trip 安排，我 5/15 回穗后跟你们对

—— {{USER_NAME}}
```

**禁忌**:
- ❌ 过度 formal ("敬请尊敬的领导阅示" — 太硬)
- ❌ 缺 owner + 截止日 ("请考虑 X" 没人 own)
- ❌ 群内长段无段落

---

### A6 · 邮件 · 高 stakes 外部 / 政企 / govt / 法务

**典型场景**: 政府正式去函 · LP 沟通 · 法务文档转送 · 外部高管邮件 · 跨年合作框架邮件。

**特征**:
- 长度: 8-30 行 (邮件 default 长一些)
- 抬头: "X 主任 / X 总 / 尊敬的 X 老师 您好"
- 落款: 完整 — "祝好 / 此致 / 顺祝商祺" + "{{USER_NAME}} · 诗悦网络 / {{PROJECT_A}} BD · 联系方式"
- 主题行: 等于 概要 ("{{ORG_D}} 基金 IL Profile 转发 + 后续会面建议")
- emoji: **零** (邮件 emoji 不专业)
- 句式: 完整 + 主语 / 时态精确 / 复合句 OK
- 礼貌词: 高密度 — "敬请 / 烦请 / 谨此 / 兹有 / 请教 / 请您审阅"
- "您" throughout
- bilingual: 主体中文 / 邮件主题或附件可英文 (跨境)
- 结构: 标题 / 编号 / 表格充分 (邮件读者 scan)
- 附件: 显式列 ("附件 1: ... · 附件 2: ...")
- 时效: 礼貌包装 ("方便时回复即可 / 期待您的反馈")

**Example**:
```
主题: 关于 5/15 文旅局会面议程的初步思考 + 请教几个问题

张主任：

您好。我是诗悦网络的 {{USER_NAME}}，上周通过 何宗寰 老师 转介绍后与您加上。

关于 5/15 您安排的对接，我们这边初步整理了 3 个主轴议题，
想请教您几点，便于会面时聚焦：

1. **文旅产业基金的开放范围**
   - 是否允许外资 LP 参与，是否有比例限制
   - 我们如以境内母基金 + 境外 GP 配合的结构进入，是否符合监管口径

2. **本地实体落地的预期**
   - 若我们以 LP 身份参与，是否需要广州 / 海珠落地公司
   - 落地后的政策支持范围 (产业基金返投 / 税收 / etc.)

3. **节奏匹配**
   - 您预期的 LP commitment 的时间窗口
   - 我方董事会决策周期约 6 周，是否匹配您的节奏

如果您 schedule 允许，5/15 当天可面谈 30-45 min；
若您时间紧，提前微信 / 邮件简答几行也行，我做好功课再来当面汇报。

附件:
- 附件 1: 诗悦网络背景 1-pager (CN)
- 附件 2: {{ORG_D}} Fund I L.P. Overview (FYI 提交, 非本议题主轴)

期待您的反馈。

此致

{{USER_NAME}}
诗悦网络 / {{PROJECT_A}} BD
联系方式: {{REDACTED}} / {{REDACTED}}
```

**禁忌**:
- ❌ 短消息 voice ("您看下 / 急" — 太 casual)
- ❌ emoji 任何
- ❌ 缺主题行 / 抬头 / 落款 任一
- ❌ 隐藏 ask / 多 ask 不编号
- ❌ "概要" / "leverage" 等英文 jargon 在邮件正文（除非对方英文背景）

---

### A8 · 跨境 JP · 日方对接（专业严谨 · 不过分谦虚）

**典型场景**: {{ORG_B}} M&A 日方 LP / target 公司沟通 · 东京 board 上行 · 日本 vendor / 代理 / 顾问。

**核心张力**: JP biz norm 高自谦 / 高敬语，但 {{USER_NAME}} 不要"过分谦虚"— **专业自信 + 适度礼貌 = 平衡点**。西方人写 JP 邮件常见误区是 over-self-deprecating ("私の浅学にて..." / "ご迷惑をおかけし..." 过度)；{{USER_NAME}} 要避免这种"卑微"调。

**特征**:
- 语言: **日文为主**（如对方明确接受英文，转 EN 但仍守 JP biz norm）
- 长度: 邮件 8-25 行 · WeChat / Slack 不常见，如有则参 A2 + JP 礼貌层
- 称呼:
  - 个人: 姓 + さん (default) / 様 (高级别 + 不熟 + 首次)
  - 公司: 会社名 + 御中
  - 高管: 役職 + 姓 ("代表取締役 山田様")
- 抬头: 邮件 — 「お世話になっております」標準开场（首次接触用「初めまして、〇〇株式会社の〇〇と申します」）
- 落款: 「何卒よろしくお願い申し上げます」/「引き続きどうぞよろしくお願いいたします」
- 句式:
  - 完整 + 主语完整（即使 JP 偏 omit 主语，biz 邮件保留）
  - 时态精确（過去形 / 現在進行形 / 未来形）
  - 敬語 layer: 尊敬語 + 謙譲語 但**不堆 4 重以上**（过堆=不自信 signal）
- 礼貌词:
  - "申し訳ございませんが" 用于真有给对方添麻烦的场合，**不滥用作 filler**
  - "恐れ入りますが" OK 但每信不超 1 次
  - "ご検討いただけますと幸いです" OK
- 自信措辞（关键区别于 over-humble）:
  - "弊社では〇〇を強みとしており、貴社にお役立ちできると考えております" (而不是 "私どもは未熟ですが...")
  - "本件、〇〇の点においては明確にお応えできます" (主动 commit 能 commit 的)
  - "現時点では明確な answer を持っておりませんが、〇〇日までに整理いたします" (不知道时 give 时点而不是 dodge)
- 数字 / 时点: precise（JP biz 重 precision）— "5月下旬" 太模糊，写 "5/20 までに"
- bilingual: JP 主，EN 技术词 OK (LP / IPO / fund / structuring etc.) — 但**不混 CN**（除非对方 bilingual CN-JP）
- emoji: **零**
- 引用 attachment: 显式（"添付資料 1: 〇〇" + "ご一読いただけますと幸いです"）

**Example** ({{ORG_B}} → 日本 LP 候选):
```
件名: {{ORG_B}} 投資機会のご共有 — お時間頂戴できますでしょうか

山田代表

お世話になっております。{{ORG_B}} の 高培尧 ({{USER_NAME}}) です。

先日ご紹介いただいた件、{{ORG_B}} が現在組成中のファンドストラクチャーについて、
資料を整理いたしました。

貴社のポートフォリオ戦略との親和性が高い 3 つの観点について、特にご説明させていただきたく:

1. 中国ブランドの日本市場展開における M&A 機会 (年間 deal flow 8-12 件想定)
2. 弱円環境下での日本側 LP 参入の advantage
3. 弊社の cross-border 実行体制 (CN-JP 双方 in-house)

5月下旬から 6月初頭にかけて東京に出張予定です。30-45 分のお時間頂戴できますと
ありがたく、ご都合の良い日時を 2-3 ご提案いただけますでしょうか。

添付資料 1: {{ORG_B}} Fund I Overview (JP, 12 pages)
添付資料 2: 中国市場 M&A pipeline サマリー (JP, 4 pages)

引き続きどうぞよろしくお願いいたします。

高培尧 ({{USER_NAME}} Gao)
{{ORG_B}} · M&A Advisory
```

**禁忌**:
- ❌ Over-humble filler ("私の浅学にて / 至らぬ点ばかりで / 恐縮ながら..." 堆 3 重以上)
- ❌ 不 commit 含糊 ("検討します" 全用 — 至少标个时点 "5/20 までに")
- ❌ CN 混 JP（除非对方明确接受）
- ❌ 直接 "ダメ / できません" — 用「現状では難しく」「再度検討させていただければ」
- ❌ 紧迫 imperative —用 hedge ("お時間あるときに" "急ぎではございませんので")

---

### A9 · 媒体 / 财经记者 (controlled · 不透露过多)

**典型场景**: 游戏葡萄 / GameLook / 触乐 / 36 氪 / 财新 / Bloomberg / Reuters / 行业 vertical 记者 / 投资 newsletter 作者 · 内部数据外泄 risk 媒介。

**核心张力**: 礼貌 + 配合，**但 information density 严控**。所有 quote 都可能上稿，**默认 on-record**。"off the record" 也未必真 off。

**特征**:
- Medium: WeChat (default) / 邮件 / sometimes 电话约
- 长度: 短 + 模糊 (3-5 行 ideal) — 越长越多 quote 风险
- 称呼: "X 老师好" (default 尊称) / "X 编辑好" / first name + 老师
- 抬头: 短身份 + 议题 anchor ("我是诗悦的 {{USER_NAME}}，上次 EPIC 峰会聊过")
- 落款: 无（消息流）或 "{{USER_NAME}} · {{PROJECT_A}} BD" 一行
- emoji: 极少 (0-1)
- 句式: 完整 + 主语 + careful — 每句问"this on the record would I say"
- 数字: **模糊**化 — "约 / 大致 / 接近" 不给 precise 数 ("我们今年 BD pipeline 大概 20+ 家" 而不是 "23 家")
- 边界词:
  - "目前不方便公开"
  - "暂时无法分享具体口径"
  - "项目还在 evolving 阶段"
  - "等正式发布我们第一时间通知你"
- 已公开口径优先: 引用 已发新闻 / 财报 / 官方信息 — **永远比 internal 安全**
- Off-the-record handling:
  - 真要 off-the-record → 显式 confirm ("这块儿能不能 off the record? 公开口径还没敲定")
  - 但**仍当成 might-on-record 措辞** — 即使口头 off
- 框架性回答优先: 不给细节，给方向 ("我们的整体策略是 X 大方向" 而不是 "我们 Q3 要投 ¥500w 在 Y 区")
- 不主动负面: 不评论竞品 / 不评论行业玩家 / 不预测市场

**Example** (记者询问{{PROJECT_A}}当前 BD 进展):
```
X 老师好，看到你问。

{{PROJECT_A}} BD 当前在 CBT2 节点前的 channel 沟通阶段，
跟主要 ACGN 内容平台都在 align 节奏。

具体平台和数字目前还不方便公开 — 等 CBT2 正式启动我们会发统一口径，
第一时间发你。

如果想聊一下行业趋势我可以 chat — {{PROJECT_A}}具体进展请等官宣。

{{USER_NAME}} · {{PROJECT_A}} BD
```

**禁忌**:
- ❌ 透露具体数据（DAU / 预约 / 投资额 / commitment）哪怕"小道消息"
- ❌ 评论竞品 ("X 项目数据其实不如他们说的好" — 永远不要)
- ❌ 内部决策口径泄露 ("我们{{PERSON}} / 路奇 觉得..." — 高管口径外泄严重)
- ❌ 表态时点 commit ("CBT2 七月一定上" — 实际 push 就 broken promise)
- ❌ 玩笑 / casual ("哈哈这玩意儿" — 记者上稿后失分)
- ❌ 邮件 reply 时把 internal email 转手忘删（最常见 leak）

---

### A10 · 投资人 / 董事会 (谦虚冷静 · 数据驱动)

**典型场景**: {{ORG_D}} GP / 路奇 (诗悦董事长) / 何宗寰 (诗悦研发) / 黄文斌 (诗悦董秘) · {{ORG_B}} 后续 LP / GP · 跨年战略 review 场合。

**核心张力**: 不夸大 + 不慌乱 + 数据 + 风险透明。投资人最讨厌"过度乐观"（暴露经验不足）和"急躁紧张"（暴露管理失控）。

**特征**:
- Medium: 邮件 / 会议 / WeCom / WeChat (取决 intimacy)
- 长度: 邮件 8-20 行 · WeChat 3-6 行
- 称呼: "X 总" (default) / "Ryan" (英文 GP 用 first name) / 路总 / "X 老师" (董事 / 顾问)
- 抬头: 邮件 — "X 总: 您好"；WeChat — "X 总，关于 X 议题简短 update"
- 落款: 邮件 — "祝好, {{USER_NAME}}"；WeChat — 无
- emoji: **零**（除非 board 内已 establish casual culture）
- 句式: 完整 + 完整时态 + careful hedging
- **数据 / 数字 critical**:
  - 准确 to 1 位小数 必要时 (PV/UV/conversion 等)
  - 标 confidence level ("preliminary" "保守口径" "stretch case")
  - 区分实际 vs 预期 ("过去 30d 实测" vs "Q3 预期")
- 礼貌词: 适度 — "向您 update / 请您 sign-off / 提前感谢"
- 谦虚措辞:
  - "目前我们看到的情况是..." (不是"我们已经解决了...")
  - "我们的判断是..." (留余地，不是"事实就是...")
  - "保守预估 / 乐观预估" 两档
- 冷静措辞:
  - 不用 "紧急 / 火烧眉毛 / 必须立刻"
  - 用 "本议题需在 X 日前决策" + 给清楚原因
  - 风险用 "需关注 / 监测" 不是 "出大事了"
- 风险透明:
  - 主动 list 3-5 个 known risk + mitigation
  - 不藏 — 投资人最讨厌后续才发现的 surprise
- Commit 低于交付能力 (under-promise / over-deliver):
  - "Q3 末预期 X" → 实际 Q3 中达成 (over-deliver)
  - 不要 反向 (overpromise then miss)

**Example** (董事会季度 update 邮件):
```
主题: {{PROJECT_A}} Q2 中期 BD 进展 — 关键 milestone update

路总, 何总, 黄秘书:

您好。简短同步{{PROJECT_A}} Q2 BD 中期进展，主轴 3 点 + 关键风险:

**进展**:
1. CBT2 节点 channel 沟通: TapTap ({{PERSON_4}}) / B站 ({{PERSON_5}} / 47) 5/18-19 全口径会面已锁定;
   预估 5/20 后能 lock CBT2 期 A-tier slot 候选。
2. 5/13 完成 B站 / TapTap 组织架构深度 ingest, 校准 4 个认知错位
   (详 02 Cards/{{PROJECT_A}}/C260513-bilibili-org-chart-...). 直接影响 5/19 议程结构。
3. 端午 6/19-21 试玩会准备: 当前 100 用户招募口径已与 4399 Yvonne 对齐,
   预计 5/29 招募开启。

**关键风险 (主动 surface)**:
- B站联运 73 分谈判 — 现 baseline 55, target 73, 我估计现场能聊到的 stretch 是 65;
  低于 65 需要回到您这边对齐口径
- TapTap 评分管理 — 5/19 会面如包体 demo 未到位, 评级议价能力受损 (预计风险中等)
- 5月路演节奏 — 5/18-20 沪差 + 5/25-26 厦差占满, 后续 deal flow 5/27 起恢复

**请您 sign-off**:
- 73 分 fallback 区间下限 — 65 是否可接受? 还是更激进?
- 5/19 14:00 {{PERSON_5}} 4 线会面 — 您是否考虑亲临 (重大 commit 在场更顺)

下次正式 update: 5/22 EOD (5/18-20 沪差回穗后)

祝好,
{{USER_NAME}} · {{PROJECT_A}} BD
```

**禁忌**:
- ❌ 自夸 ("我搞定了" / "这次大获成功") — 总是 understatement
- ❌ "肯定 / 一定 / 必然" 等绝对词
- ❌ 主观情绪词 ("我觉得很 exciting / 很担心 / 很 frustrated")
- ❌ 缺数据的判断 ("整体感觉 OK" — 没数据空泛)
- ❌ 隐藏风险 (永远主动 surface, 不让对方在后续发现)
- ❌ 紧急感操控 ("必须本周决定" 除非真有 hard deadline)
- ❌ Overpromise ("我们 6 月底 X 一定到位" — 后续 push 就是 broken)

---

### A11 · 法务 / 合规 (严谨清晰 · 无歧义)

**典型场景**: 诗悦法务 / 外部律所 / 合规审计 / 合同审稿 / 政府备案文件 / 跨境 legal review。

**核心张力**: 措辞 precision 高于一切 — 每个词都可能影响法律解释。**清晰 ≠ 复杂**, 清晰 = 不歧义。

**特征**:
- Medium: 邮件 / 文档 / 备忘录 (鲜少 WeChat — IM 不留法律级 record)
- 长度: 视议题，一般偏长 (10-40 行) 但 dense — 不水
- 称呼: "X 律师" / "X 总监" / 全名 + 职位 (法务沟通需建立 paper trail)
- 抬头: 邮件 — "X 律师 您好" / WeCom — "X 律, 关于 X 合同的 review"
- 落款: 邮件 — "祝好 / Best regards" + 完整 signature (法务沟通需 contact 留档)
- emoji: **零**
- 句式: 完整 + 准确 + 单一解读
- 词汇 precision:
  - 法律术语用准 (force majeure / 不可抗力 / warranty / 保证 / indemnity / 赔偿)
  - 主体 specific — 用法人单位全称 ("广州栖梧信息科技有限公司") 而非简称 ("诗悦")
  - 时点 specific — "2026 年 5 月 31 日 24:00 (北京时间)" 而非 "5月底"
  - 范围 specific — "限于 [国家 / 区域 / 渠道] 范围内" 不留通用兜底
- 引用 conventions:
  - "依据 X 法 第 X 条" 引用 法律条款
  - "参 X 协议 § X" 引用 已签合同
  - "援引 X 先例" 引用 过往 case
- Hedging where appropriate:
  - "在 [X 条件] 下" — 不给无条件保证
  - "如发生 [Y]，应 [Z]" — 条件式触发
- Disclaim 边界:
  - "本意见 limited to [scope]" — legal opinion 都带 scope limit
  - "依据现有 information 提供; 如新信息出现，结论可能变化"
- 不混 emoji / casual / 主观情绪
- bilingual: CN 主，EN 法律术语保留原文（force majeure / indemnification / arm's length / etc.）— 不机翻
- 表态:
  - 不 commit answer 时直说 "需进一步 review" / "需补充 information"
  - 不模糊 "大概 / 应该"

**Example** (诗悦法务 review 小鹏 MOU):
```
主题: 小鹏 MOU 草案 review 反馈 — 4 个 point 需要进一步明确

X 律师 您好:

您发来的小鹏 MOU 草案 v0.3 我已 review, 4 个 point 需要进一步明确,
按合规风险排序如下:

1. **签约主体不明** (高风险)
   现 § 1.2 提"小鹏一方"但未指明具体法人. 应明确为
   "广州小鹏汽车科技有限公司"或集团内其他主体. 涉及后续违约责任承担范围.

2. **MONA M03 IP 使用范围 (高风险)**
   § 3.1 提及"将提供 MONA 痛车设计相关 IP" 但范围模糊. 建议:
   - 限定用途: 仅用于 2026 BW 展会 + 端午试玩会两场次
   - 限定地理: 中国大陆 only
   - 排除事项: 不含 [汽车实物销售 / 长期商业化使用]

3. **违约责任 (中风险)**
   § 7 通用违约赔偿条款缺失. 应补充:
   - 关键节点延迟的具体补偿机制 (e.g. 试玩会前 14 日内 IP 物料未交付 → ¥X 元罚)
   - 不可抗力 (force majeure) 条款明确范围

4. **争议解决 (中风险)**
   § 10 现"友好协商"为单一机制. 建议补 fallback:
   - 协商不成 → 广州仲裁委 arbitration (诗悦主场)

依据《合同法》第 X 条 + 《公司法》§ XX, 上述 4 点完善后可进入下一轮 redline.

如需 redline 草案 我可以 5/16 EOD 前提供.

祝好,
{{USER_NAME}} · 诗悦网络 BD
广州栖梧信息科技有限公司
```

**禁忌**:
- ❌ 简称代法人主体 ("小鹏" → 必须"广州小鹏汽车科技有限公司")
- ❌ 模糊时点 ("尽快 / 大概 / 5月底") — 必须精确日期 + 时区
- ❌ 法律术语错用 (force majeure vs hardship 不是一回事; indemnify vs warranty 不同)
- ❌ "我觉得 / 我认为" 主观词 (用 "依据 / 根据 / 经审查")
- ❌ 缺 scope limit 的 legal opinion ("本意见 absolute"  — 永远要 limit)
- ❌ casual 措辞 ("这块儿 / 搞 / 大致")
- ❌ emoji / 表情

---

### A7 · 内部团队 · WeChat / WeCom · 同事 peer-to-peer (最 casual)

**典型场景**: 跟一一 / 小K / 煎饼 等已 ID 熟悉的内部同事 quick 沟通。

**特征**:
- 长度: 1-2 行 normal
- 称呼: 花名 / first name only
- 抬头: 无
- 落款: 无
- emoji: 自由 (含 character emoji OK)
- 句式: 极短 + 大量 ellipsis + 中英混
- 语气词: "搞 / 弄 / 走起 / 来一下 / 顺一下" 自由
- action ask: 单条
- bilingual: 自由
- 标点: 中文逗号 / 中文句号 / "~" / "..." 都自由

**Example**:
```
小K, 5/15 飞机上嚼了下 EPIC takeaway，落档完发你 review~
```

**禁忌**:
- ❌ 升级 register (对内同事 default A7, 升 A4 显得疏远)
- ❌ "您" 用于同事

---

## Calibration Decision Tree（draft 前必跑）

**优先级**: 先跑 Step 0（specialized context override），如命中直接 lock register；不命中再走 Step 1-4 的常规 4-axis 矩阵。

```
0. Specialized context overrides (any of these → lock register, skip 1-4):
   - 对方是 日本 / JP 方？ → A8 (跨境 JP) 默认
   - 对方是 媒体 / 财经记者 / newsletter 作者？ → A9 (受控 controlled)
   - 对方是 投资人 / 董事 / 母公司 high-mgmt？ → A10 (谦虚冷静)
   - 对方是 律师 / 法务 / 合规审计？议题是 合同 / 法规？ → A11 (严谨清晰)

1. 关系深度 (intimacy)
   - 第一次接触？ → A2 / A3 (按 stakes)
   - 已熟悉 (≥3 次有效交往)？ → A1 / A4 / A7 (按 medium)
   
2. 议题 stakes
   - 低 routine (节奏 / 信息同步 / 顺一件事)？ → A1 / A4 / A7
   - 中 (合作框架 / 中等量级 commit)？ → A4 / A5
   - 高 (跨年 commit / 政策 / 法律 / 战略决定)？ → A3 / A5 / A6

3. Medium
   - WeChat (微信 1-on-1)？ → A1-A3
   - WeChat 群？ → A2 + 群礼仪
   - WeCom 1-on-1？ → A4
   - WeCom 群？ → A5
   - 邮件？ → A5 (mid-stake) or A6 (high-stake)

4. 对方身份层级
   - Peer / 平级？ → A1 / A4 / A7
   - 上行 (上级 / 客户高管)？ → A2 / A4 / A5 (按 stakes)
   - Govt / 政企 / 高管 (CEO 级)？ → A3 / A5 / A6 默认
```

**Output**: 一段话告诉自己 "我现在 draft register = AX，对方 = X，stakes = X，override = Y/N" — 然后写。

**关键判断点 — specialized context 检测**:
- 对方 affiliation 含 "JP / 日 / Japan / -さん / 株式会社" → A8
- 对方 affiliation 含 "记者 / 编辑 / 媒体 / 主笔 / newsletter / Bloomberg / Reuters / 36Kr / 财新" → A9
- 对方 role 含 "总 / 董事 / Chairman / CEO / Partner / GP / LP / 投资 / 顾问" + 与你是 上行 → A10
- 对方 role 含 "律师 / 法务 / 合规 / counsel" 或议题含"合同 / 法规 / 备案" → A11

## Hard Rules

1. **NEVER 跨 register 混用** — 同一条消息内不混 "您" + "哥/姐" / 不混 emoji + 邮件落款
2. **NEVER assume relationship intimacy** — 第一次或不确定时 default 升 1 级 (A1→A2, A2→A3) — 降级容易，升级失礼难修
3. **NEVER 用 A6 邮件 register 写 WeChat** — 即使 high stakes 在 WeChat 用 A3 (高 stakes WeChat) 而非 A6 (邮件)
4. **NEVER 用 A7 register 跟外部** — 内部同事专用
5. **ALWAYS calibrate before draft** — 跑 Decision Tree → 显式 state register → 再写
6. **ALWAYS reference real prior conversation** if available — 看对方上次怎么称呼你 / 怎么签 / 用不用 emoji → mirror
7. **ALWAYS preserve {{USER_NAME}} voice** within register — 不论 A1-A7 都保持 概要 / 短句 / 中英混 (但密度按 register 调)
8. **WHEN UNCERTAIN about 对方 register**, draft 2 options for {{USER_NAME}} to pick — "draft v1 偏 A1 / draft v2 偏 A3 — 你选"

## Cross-skill integration

| Skill | How it uses this rule |
|---|---|
| `/to-internal-briefing` | Internal briefing 是 Register B/C territory (biz doc), NOT message register. 但 cover letter / 简短引言 用 A4 |
| `/response-draft-loop` | AFK 时 draft 每条 reply 先 identify register → calibrate → write |
| `/source-ingest` (when ingesting WeChat) | Tag conversation by register signature → future tone training data |
| **NEW**: `/draft-message` (future skill) | Explicit draft-with-register skill — invoke 时 ask register 或 auto-detect |

## Examples — register mismatch detection

❌ **Wrong**: 给政府文旅局副局发 "李哥，听说您...嗯..."
✅ **Right**: A3 register — "李局好，我是诗悦的 {{USER_NAME}}..."

❌ **Wrong**: 给{{PERSON_4}}发 "{{PERSON_4}}先生您好,关于 EPIC 议题特此请教..."
✅ **Right**: A1 register — "{{PERSON_4}}哥, 刚才聊到 Tiff 那个口子..."

❌ **Wrong**: 内部 WeCom 群发 "各位，本人现就...特此通知..."
✅ **Right**: A5 register — "各位，5/19 SH 出差 B 站会面 update..."

❌ **Wrong**: 邮件给 LP 写 "Dear X, just FYI on {{ORG_D}} 这块儿..."
✅ **Right**: A6 register — "X 总: 您好。兹将 {{ORG_D}} 基金信息 update..."

## Future expansion (后续 {{USER_NAME}} 补)

**已完成 (5/14)**: A8 跨境 JP / A9 媒体记者 / A10 投资人董事会 / A11 法务合规

**Pending**:
- 时区差导致的紧迫信号校准 (CN-night → JP-morning 怎么写，CN-business-day → EU/US off-hours 怎么写)
- 危机沟通 (crisis comms) — 数据泄露 / PR 危机 / 重大事故 register
- 离职 / 解雇 / 内部冲突 register
- 跨文化 EN register (与新加坡 / 北美 / 欧洲 对接，非 JP)

后续 {{USER_NAME}} 补 → 增加 A12+ 段。

---

*Register A 系列与 biz-doc-critic Register B/C 互补。biz docs (deal memos / biz evals / biweekly reports / board memos) → Register B/C。messaging (WeChat / WeCom / email) → Register A1-A7。Skills 起草前 calibrate 必跑 Decision Tree。*
