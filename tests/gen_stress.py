#!/usr/bin/env python3
"""生成分页压力测试文档：把第二至七节写满（长段落、图、表、公式、列表、脚注、长网址、22 条文献）。

用法：gen_stress.py 模板目录 输出目录 [第五节段数 第七节表格行数]
从模板目录读取 content.tex 和 references.bib，写入输出目录；所有正文和文献均为虚构。
"""
import re
import sys

backup, project = sys.argv[1], sys.argv[2]
n5, n7 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (6, 14)
TAG = r"【排版测试内容，非正式文本，所列文献均为虚构】"

POOL = [
    r"高校图书馆每天要处理大量的借阅、归还和预约请求，读者关心的不只是能否借到图书，更是查找和取书的效率。传统的管理方式依赖人工登记和定期盘点，难以及时反映馆藏在各个阅览区之间的流动情况，导致热门图书的可借状态经常与实际不符\cite{s1,s2,s3}。",
    r"条码和射频标签的普及为馆藏的自动识别提供了基础，为借阅流程的改造提供了新的技术路径。已有研究表明，把读者的借阅记录与图书的分类信息结合起来分析，可以明显提高采购计划的合理性\cite{s4}；同时，自助借还设备和移动端查询也被用于缓解高峰时段的排队问题\cite{s5,s6}。",
    r"然而，把这些手段整合到一套系统中仍面临三方面的困难：一是历史数据格式不统一，难以直接迁移；二是高峰时段的并发请求集中，会影响查询的响应速度；三是各分馆的业务规则存在差异，统一的流程无法直接套用。文献\parencite{s7}从系统角度讨论了业务处理与数据存储分离的思路，文献\parencite{s8}则关注数据更新的及时性对读者体验的影响。",
    r"Recent work on library management systems shows that circulation services benefit from combining automation, structured records and regular auditing. Long English sentences are included here on purpose so that inter-word spacing, hyphenation and mixed-language line breaking can be examined inside the framed box, for example internationalization, disproportionately and characteristically\cite{s9,s10}.",
    r"从工程实现看，馆藏数据的维护需要兼顾批量导入与日常更新。批量导入负责历史记录的整理和分类规则调整后的重新归类，日常更新负责每一笔借还操作的即时登记。两类操作共用同一套数据格式和校验规则，通过版本号进行区分，从而保证各分馆之间的数据一致\footnote{这里的一致指相同的图书在不同分馆的系统中显示相同的状态，脚注用于测试边框内脚注的编号与输出位置。}。",
    r"在服务侧，系统以数据库承载日常查询，以缓存和限流策略保障高峰时段的响应速度。当某项数据缺失或过期时，页面显示默认的提示信息，避免整个页面无法打开。相关的接口规范可参见公开文档 \url{https://example.com/docs/library-system/circulation/api/v2/reference/overview?section=latency-and-degradation&lang=zh-CN}，这里用超长网址测试断行效果。",
    r"评估方面，本课题同时考察功能指标与运行指标。功能指标包括查询的准确率、预约的成功率和盘点的差错率，运行指标包括平均响应时间、高峰时段的吞吐量和系统可用性。通过分阶段试运行比较不同方案的效果，并对长期使用情况进行持续观测\cite{s11,s12,s13,s14}。",
    r"技术难度主要体现在历史数据的清洗与迁移、高峰时段的性能保障以及多分馆业务规则的统一。工作量包括数据整理、功能设计、系统开发、试运行和效果分析，预计需要持续一年以上的工程投入\footnote{本段第二条脚注，用于测试同一节内多条脚注连续编号。}。",
    r"为便于后续功能扩展，系统把借阅记录定义为带时间戳的结构化数据，并提供统一的查询与导出接口。管理人员可以按学科、馆区和时间段筛选记录，也可以基于统计结果调整各类图书的复本数量，使馆藏结构与读者需求保持匹配\cite{s15,s16}。",
    r"此外，读者信息的保护是图书馆业务的重要约束。借阅记录在用于统计之前需要去除身份标识，统计结果只保留业务所需的汇总数据，原始记录按规定期限保存。操作日志记录每一次查询的时间和操作人员，便于问题回溯和定期检查\cite{s17,s18,s19,s20,s21,s22}。",
]


def paras(*idx):
    return "\n  \\par\n  ".join(POOL[i % len(POOL)] for i in idx)


def figure(height, caption):
    return (r"\begin{figure}\centering\fbox{\parbox[c][" + height + r"]{0.8\linewidth}{\centering "
            + caption + "占位图（高 " + height + r"）}}\caption{" + caption + r"}\end{figure}")


def table(rows, caption):
    body = "".join(rf"第 {i} 项 & 这一列用于测试较长的单元格文字在固定列宽内的自动换行效果 & {i}.0 \\\hline " for i in range(1, rows + 1))
    return (r"\begin{table}\caption{" + caption + r"}\begin{tabular}{|l|p{90mm}|c|}\hline 项目 & 说明 & 权重\\\hline "
            + body + r"\end{tabular}\end{table}")


EQ = r"\begin{equation}p(y\mid x)=\frac{\exp\left(f_\theta(x,y)/\tau\right)}{\sum_{y'}\exp\left(f_\theta(x,y')/\tau\right)}\end{equation}"

S2 = TAG + "\n  \\par\n  " + paras(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 4, 6, 7, 8, 9)
S3 = TAG + "\n  \\par\n  " + paras(8)

S4 = "\n  \\par\n  ".join([
    TAG,
    r"\textbf{（一）总体技术路线}",
    paras(4, 5, 8),
    figure("95mm", "系统总体架构"),
    paras(0, 1),
    r"\textbf{（二）关键方法}\par 检索结果的排序得分按式(1)归一化：" + EQ + "其中 $\\tau$ 为调节参数，$f_\\theta$ 为打分函数。",
    r"本课题的主要工作分为以下几点：\begin{enumerate}\item 设计面向多分馆的馆藏数据格式，这一条故意写得比较长，用于测试列表项目折行时的悬挂缩进效果和跨行对齐情况；\item 构建业务处理与数据存储分离的系统架构；\item 建立数据质量的持续检查与监控机制。\end{enumerate}",
    paras(2, 6, 7),
    table(9, "技术方案对比"),
    paras(3, 9, 4),
    figure("150mm", "借阅业务流程（超过当前页剩余空间）"),
    paras(5, 6, 8, 0, 1, 2, 7),
    table(16, "实验设计（较长表格，放不下时整表换页）"),
    paras(9, 4, 3),
])

S5 = "\n  \\par\n  ".join([TAG] + [paras(i) for i in range(n5)])

S6 = TAG + r"""
  \par
  已发表或接收的成果如下（均为虚构示例）：
  \begin{enumerate}
  \item 作者甲，作者乙。面向多分馆的图书借阅管理方法研究，排版示例学报，2025 年 6 月，已录用。这一条故意写长，用于测试列表项在边框内折行。
  \item Author A, Author B. An Example Paper Title for Testing Long Bibliographic Items Inside the Framed Box, Example Conference, 2025.
  \item 发明专利：一种图书馆馆藏数据的校验方法，申请号 CN000000000000.0，实审中。
  \end{enumerate}
  软件著作权和项目获奖等其他成果可按相同方式列出。
"""

rows = "".join(rf"2026 年 {1 + i % 12} 月 & 第 {i + 1} 阶段工作内容，包括文献调研、系统设计、开发联调、试运行、数据分析与论文撰写 \\\hline " for i in range(n7))
S7 = TAG + r"""
  \par
  研究计划按阶段推进，具体安排见表格。
  \begin{table}\caption{研究进度安排}\begin{tabular}{|l|p{118mm}|}\hline 时间 & 内容\\\hline """ + rows + r"""\end{tabular}\end{table}
  各阶段结束时组织一次导师审查，并根据审查意见调整下一阶段的工作内容。
"""

content = open(f"{backup}/content.tex", encoding="utf8").read()
for name, body in [("topicbasis", S2), ("innovation", S3), ("methodroute", S4),
                   ("expectedresults", S5), ("existingresults", S6), ("researchplan", S7)]:
    pattern = re.compile(r"\\newcommand\{\\" + name + r"\}\{%\n.*?\n\}\n", re.S)
    assert len(pattern.findall(content)) == 1, name
    content = pattern.sub(lambda _: "\\newcommand{\\" + name + "}{%\n  " + body.strip() + "\n}\n", content)
open(f"{project}/content.tex", "w", encoding="utf8").write(content)

bib = open(f"{backup}/references.bib", encoding="utf8").read() + "\n% 以下条目均为虚构，仅用于分页压力测试。\n"
for i in range(1, 23):
    if i % 5 == 0:
        bib += f"@inproceedings{{s{i},\n  author = {{Example, Author and Sample, Writer and Test, Person and Demo, User}},\n  title = {{A Fictional Study Number {i} on Library Systems for Testing Hanging Indentation in Long Bibliography Entries}},\n  booktitle = {{Proceedings of the Fictional Conference on Layout Testing}},\n  year = {{2024}},\n  pages = {{{100 + i}--{120 + i}}},\n}}\n\n"
    elif i % 7 == 0:
        bib += f"@online{{s{i},\n  author = {{示例机构}},\n  title = {{虚构技术报告第 {i} 号}},\n  url = {{https://example.com/reports/fictional/library-system-layout-test-number-{i}/full-text.html}},\n  year = {{2025}},\n  urldate = {{2026-11-01}},\n}}\n\n"
    else:
        bib += f"@article{{s{i},\n  author = {{作者甲 and 作者乙 and 作者丙 and 作者丁}},\n  title = {{虚构论文第 {i} 号：用于测试参考文献跨页与折行的较长中文题目}},\n  journal = {{排版示例学报}},\n  year = {{2025}},\n  volume = {{{i}}},\n  number = {{{1 + i % 6}}},\n  pages = {{{10 + i}--{30 + i}}},\n  language = {{chinese}},\n}}\n\n"
open(f"{project}/references.bib", "w", encoding="utf8").write(bib)
