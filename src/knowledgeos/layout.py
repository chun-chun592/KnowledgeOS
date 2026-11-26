"""Canonical, locale-independent vault paths and standard layout detection."""
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import os

NAMES = {
    "00_Human": "00_个人知识库", "Inbox": "收件箱", "Daily": "日常笔记",
    "Projects": "项目", "Areas": "长期领域", "Resources": "知识资源",
    "Concepts": "概念笔记", "Literature": "阅读笔记", "Permanent-Notes": "永久笔记",
    "References": "参考资料", "MOCs": "知识地图", "Attachments": "附件",
    "Archive": "归档", "book": "书籍", "Clippings": "剪藏",
    "10_Agent": "10_AI知识库", "raw": "原始资料", "documents": "文档",
    "papers": "学术论文", "websites": "网页文章", "wiki": "整理后的知识",
    "concepts": "概念", "entities": "对象", "topics": "专题", "comparisons": "对比分析",
    "synthesis": "综合研究", "projects": "项目知识", "decisions": "决策记录",
    "15_Shared": "15_公共知识库", "sources": "来源记录",
    "log.md": "知识更新记录.md", "20_Exchange": "20_协作交流",
    "agent-to-agent": "AI之间的交流", "locks": "编辑锁",
    "agent-to-human": "AI提供给人的知识", "human-to-agent": "人提供给AI的知识",
    "write-requests": "笔记修改提案", "30_System": "30_知识库管理",
    "policies": "管理规则", "reports": "检查报告", "schemas": "笔记格式规范",
    "scripts": "辅助脚本", "templates": "笔记模板", "workflows": "知识处理流程",
    "README.md": "使用说明.md", "90_Archive": "90_全库归档",
    "ownership-and-permissions.md": "归属与权限.md", "knowledge-routing.md": "知识工作流程.md",
    "human-change-proposal.md": "个人笔记修改提案.md", "agent-knowledge.md": "AI知识笔记.md",
    "human-note.md": "个人笔记.md", "handoff.md": "任务交接.md",
    "concept.md": "概念.md", "entity.md": "对象.md", "topic.md": "专题.md",
    "comparison.md": "对比分析.md", "synthesis.md": "综合研究.md",
    "project.md": "项目知识.md", "decision.md": "决策记录.md", "source.md": "来源.md",
}
LOCALES = ("en-US", "zh-CN", "zh-en")
REGIONS = ("00_Human", "10_Agent", "15_Shared", "20_Exchange", "30_System", "90_Archive")


@dataclass(frozen=True)
class Layout:
    locale: str = "en-US"

    def path(self, logical: str) -> PurePosixPath:
        parts = PurePosixPath(logical).parts
        result = []
        for i, part in enumerate(parts):
            chinese = NAMES.get(part)
            if part == "index.md":
                chinese = "知识导航.md" if parts[0] == "00_Human" else "知识目录.md"
            if chinese and self.locale != "en-US":
                if self.locale == "zh-CN":
                    part = chinese
                elif part.endswith(".md"):
                    part = f"{part[:-3]}_{chinese[:-3]}.md"
                elif part in REGIONS:
                    part += "_" + chinese.split("_", 1)[1]
                else:
                    part += "_" + chinese
            result.append(part)
        return PurePosixPath(*result)

    @property
    def wiki(self):
        return self.path("10_Agent/wiki")

    @property
    def shared(self):
        return self.path("15_Shared")

    @property
    def human(self):
        return self.path("00_Human")

    @property
    def meta(self):
        return frozenset(self.path(p).name.casefold() for p in (
            "10_Agent/wiki/index.md", "10_Agent/wiki/log.md", "00_Human/index.md",
            "15_Shared/index.md", "15_Shared/log.md", "30_System/README.md")) | {"index.md", "log.md", "readme.md"}


def detect_layout(root: Path) -> Layout:
    """Reject mixed region markers, preserve compatibility with sparse English vaults."""
    matches = [Layout(locale) for locale in LOCALES if any(
        os.path.lexists(root / Layout(locale).path(region)) for region in REGIONS)]
    if len(matches) > 1:
        raise ValueError("Ambiguous vault layout: mixed language region markers")
    return matches[0] if matches else Layout()
