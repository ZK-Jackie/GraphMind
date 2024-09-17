import json
import pickle
from typing import List, Iterator, Any

from pydantic import Field, ConfigDict

from graphmind.adapter.engine.base import BaseEntity, BaseRelation
from graphmind.adapter.structure import BaseStructure, BaseTask


class InfoNode:
    title: str
    """Markdown 标题"""

    content: str | None
    """Markdown 正文"""

    level: int
    """标题级别"""

    parent: "InfoNode" = None
    """父节点"""

    children: list
    """子节点列表"""

    entity: list[BaseEntity] | None = None
    """实体信息"""

    relation: list[BaseRelation] | None = None
    """关系信息"""

    entity_task: "BaseTask" = None
    """实体任务信息"""

    relation_task: "BaseTask" = None
    """关系任务信息"""

    def __init__(self,
                 title: str,
                 content: str | None,
                 level: int,
                 parent=None):
        self.title = title
        self.content = content
        self.parent = parent
        self.level = level
        self.children = []  # 问题：为什么必须在这里初始化一个空列表，不能在前面定义的时候初始化一个空列表，否则会出现内存异常

    def add_child(self, node: "InfoNode"):
        node.parent = self
        self.children.append(node)

    def get_title_path(self) -> List[str]:
        # 递归获取从根节点到当前节点的title列表
        if self.parent:
            return self.parent.get_title_path() + [self.title]
        else:
            return [self.title]

    def get_entity_names(self) -> List[str]:
        if self.entity:
            return [entity.name for entity in self.entity]
        return []

    def __iter__(self) -> "InfoNode":
        # 生成器，用于遍历当前节点及其所有子节点
        yield self
        for child in self.children:
            yield from child

    def dump_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level,
            "children": [child.dump_dict() for child in self.children]
        }

    @staticmethod
    def from_dict(data: dict):
        title = data.get("title")
        content = data.get("content")
        level = data.get("level")
        children = data.get("children")
        node = InfoNode(title=title, content=content, level=level)
        for child in children:
            node.add_child(InfoNode.from_dict(child))
        return node


class InfoTree:
    main_root: InfoNode | None = None
    """根节点"""

    node_cnt: int = 0
    """当前树的总节点数量"""

    def __init__(self):
        self.main_root = None

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

    def dump_dict(self):
        final_dict = {"main_root": self.main_root.dump_dict()}
        return final_dict

    def from_dict(self, data: dict):
        self.main_root = InfoNode.from_dict(data.get("main_root"))
        return self

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

    def __str__(self) -> str:
        return self._print_tree(self.main_root)

    @staticmethod
    def traverse(root: InfoNode) -> Iterator["InfoNode"] | None:
        return iter(root)

    def __iter__(self) -> Iterator["InfoNode"]:
        return self.traverse(self.main_root)


class InfoForest(BaseStructure):
    trees: List[InfoTree] = Field(default=[])
    """树的列表"""

    title: str = Field(description="Title of the forest", default="Info Forest")
    """书本标题"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    """pydantic 配置：允许任意类型"""

    def dump_json(self):
        final_dict = {
            "title": self.title,
            "trees": [tree.dump_dict() for tree in self.trees]
        }
        return final_dict

    @staticmethod
    def from_json(file_path: str):
        raw = json.load(open(file_path, "r"))
        forest = InfoForest()
        for tree in raw:
            forest.trees.append(InfoTree().from_dict(tree))
        return forest

    def dump_pickle(self, file_path: str):
        pickle.dump(self, open(file_path, "wb"))

    @staticmethod
    def from_pickle(file_path: str):
        return pickle.load(open(file_path, "rb"))



    def dump_dict(self):
        return {
            "title": self.title,
            "trees": [tree.dump_dict() for tree in self.trees]
        }

    def add_tree(self, tree: InfoTree):
        self.trees.append(tree)

    def count_node(self) -> int:
        node_cnt = 0
        for tree in self.trees:
            node_cnt += tree.node_cnt
        return node_cnt

    def __str__(self) -> str:
        result = ""
        for tree in self.trees:
            result += str(tree)
        return result

    def __len__(self) -> int:
        return len(self.trees)

    def __iter__(self) -> Iterator[InfoTree]:
        return iter(self.trees)

    def get_index(self) -> str:
        return self.__str__()
