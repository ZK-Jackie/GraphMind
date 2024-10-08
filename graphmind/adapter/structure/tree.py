from typing import List, Iterator, Any

from pydantic import Field, ConfigDict, BaseModel

from graphmind.adapter.engine.base import BaseEntity, BaseRelation
from graphmind.adapter.structure import BaseStructure, BaseTask


class InfoNode(BaseModel):
    title: str | None = Field(description="当前文本结点的最近一个 Markdown 标题", default=None)
    """Markdown 标题"""

    content: str | None = Field(description="当前文本结点的正文", default=None)
    """Markdown 正文"""

    level: int = Field(description="当前文本结点标题的标题级别", default=0)
    """标题级别"""

    parent: Any | "InfoNode" | None = Field(default=None, exclude=True)
    """父节点"""

    children: list | None = Field(default_factory=list)
    """子节点列表"""

    entity: list[BaseEntity] | None = Field(description="当前结点提取出的实体信息", default_factory=list)
    """实体信息"""

    relation: list[BaseRelation] | None = Field(description="当前结点提取出的关系信息", default_factory=list)
    """关系信息"""

    entity_level_task: BaseTask | None = Field(description="执行当前结点实体等级划分的任务", default=None)
    """实体等级任务信息"""

    entity_attr_task: list[BaseTask] | None = Field(description="执行当前结点实体属性提取的任务", default_factory=list)
    """实体任务信息"""

    relation_task: BaseTask | None = Field(description="执行当前结点关系提取的任务", default=None)
    """关系任务信息"""


    def add_child(self, node: "InfoNode"):
        node.parent = self
        self.children.append(node)

    def get_title_path(self) -> List[str]:
        # 递归获取从根节点到当前节点的title列表
        if self.parent:
            return self.parent.get_title_path() + [self.title]
        else:
            return [self.title]

    def get_entity_num(self) -> int:
        return len(self.entity) if self.entity else 0

    def get_entity_names(self) -> List[str]:
        if self.entity:
            return [entity.name for entity in self.entity]
        return []

    def iter(self) -> Iterator["InfoNode"] | None:
        # 生成器，用于遍历当前节点及其所有子节点
        yield self
        for child in self.children:
            yield from child.iter()


class InfoTree(BaseModel):
    main_root: InfoNode | None = Field(description="Main root of the tree", default=None)
    """根节点"""

    node_cnt: int = Field(description="Total node count of the tree", default=0)
    """当前树的总节点数量"""

    def insert_node(self, root: InfoNode, node: InfoNode, node_level: int):
        if self.main_root is None:
            self.main_root = node
            return self
        if not root:
            root = self.main_root
        root_level = root.level
        if node_level < 0 or root_level < 0:
            raise ValueError("Info Tree build failed: node level or root level is less than 0")
        if node_level > root_level:
            # 如果当前节点的 level 大于 root 的 level，那么当前节点是 root 的子节点
            if not root.children:
                # 如果没有子节点，直接添加
                root.add_child(node)
                self.node_cnt += 1
            else:
                # 如果有子节点，默认当前 node 是当前 root 最后一个 child 的子节点
                last_child = root.children[-1]
                self.insert_node(last_child, node, node_level)
        elif node_level == root_level:
            # 如果当前节点的 level 等于 root 的 level，那么当前节点是 root 的兄弟节点
            is_dup, dup_node = self._is_dup_children(root, node)
            if is_dup:
                # 如果是重复节点，正文直接在后面追加
                dup_node.content += node.content
            else:
                # 如果不是重复节点，添加到 root.parent 的 children 中
                root.parent.add_child(node)
                self.node_cnt += 1
        else:
            # 如果当前节点的 level 小于 root 的 level，向上回溯
            self.insert_node(root.parent, node, node_level)

    @staticmethod
    def _is_dup_children(root: InfoNode, node: InfoNode) -> (bool, InfoNode | None):
        for child in root.children:
            if child.title == node.title:
                return True, child
        return False, None

    def _print_tree(self, root: InfoNode, depth=0) -> str:
        if not root:
            return ""
        result = "  " * depth + f"{root.title}\n"
        for child in root.children:
            result += self._print_tree(child, depth + 1)
        return result

    def print(self) -> str:
        return self._print_tree(self.main_root)

    def iter(self) -> Iterator["InfoNode"]:
        return self.main_root.iter()


class InfoForest(BaseStructure):
    trees: List[InfoTree] = Field(default=[])
    """树的列表"""

    title: str = Field(description="Title of the forest", default="Info Forest")
    """书本标题"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    def add_tree(self, tree: InfoTree):
        self.trees.append(tree)

    def count_node(self) -> int:
        node_cnt = 0
        for tree in self.trees:
            node_cnt += tree.node_cnt
        return node_cnt

    def print(self) -> str:
        result = ""
        for tree in self.trees:
            result += str(tree)
        return result

    def get_size(self) -> int:
        return len(self.trees)

    def iter(self) -> Iterator[InfoTree]:
        return iter(self.trees)

    def get_index(self) -> str:
        return self.print()
