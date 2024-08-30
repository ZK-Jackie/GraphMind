from typing import List
from chatkg.adapter.database.GraphNeo4j import CypherNodeState, CypherRelationState
import warnings


class InfoNode:
    title: str
    content: str | None
    level: int
    struct_info: dict | None = None
    parent: "InfoNode" = None
    children: list

    def __init__(self, title: str, content: str, level: int, parent=None):
        self.title = title
        self.content = content
        self.parent = parent
        self.children = []
        self.level = level

    def add_child(self, node: "InfoNode"):
        node.parent = self
        self.children.append(node)

    def get_title_path(self):
        # 递归获取从根节点到当前节点的title列表
        if self.parent:
            return self.parent.get_title_path() + [self.title]
        else:
            return [self.title]

    def to_cypher_obj(self):
        # 生成cypher语句
        cypherStates = []
        # 节点信息
        if "知识实体" not in self.struct_info or "实体关系" not in self.struct_info:
            warnings.warn(f"unprocessed struct info is found, titled {self.title}, please build struct info first")
            return cypherStates
        try:
            for entity_name in self.struct_info["知识实体"]:
                node_state = CypherNodeState(
                    node_type="知识实体",
                    node_attr=self.struct_info["知识实体"][entity_name]["属性"]
                )
                node_state.node_attr["name"] = entity_name
                cypherStates.append(node_state)
            # 关系信息
            for node1_name in self.struct_info["实体关系"]:
                relationships = self.struct_info["实体关系"][node1_name]
                for relation in relationships:
                    node2_list = self.struct_info["实体关系"][node1_name][relation]
                    for node2_name in node2_list:
                        relation_state = CypherRelationState(
                            node1_name=node1_name,
                            node1_type="知识实体",
                            relation_name=relation,
                            node2_name=node2_name,
                            node2_type="知识实体",
                        )
                        cypherStates.append(relation_state)
        except Exception:
            warnings.warn(f"improper struct info is found, titled {self.title}, please fix struct info first")
            return cypherStates
        return cypherStates

    def __iter__(self):
        # 生成器，用于遍历当前节点及其所有子节点
        yield self.get_title_path(), self.content
        for child in self.children:
            yield from child


class InfoTree:
    main_root: InfoNode
    node_cnt: int = 0

    def __init__(self, node: InfoNode):
        self.main_root = node

    def insert_node(self, root: InfoNode, node: InfoNode, node_level: int):
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

    def _is_dup_children(self, root: InfoNode, node: InfoNode):
        for child in root.children:
            if child.title == node.title:
                return True, child
        return False, None

    def _print_tree(self, root: InfoNode, depth=0):
        if not root:
            return ""
        result = "  " * depth + f"{root.title}\n"
        for child in root.children:
            result += self._print_tree(child, depth + 1)
        return result

    def __str__(self):
        return self._print_tree(self.main_root)

    def traverse(self, root: InfoNode):
        return iter(root)

    def __iter__(self):
        return self.traverse(self.main_root)


class InfoForest:
    trees: List[InfoTree]

    def __init__(self):
        self.trees = []

    def add_tree(self, tree: InfoTree):
        self.trees.append(tree)

    def count_node(self):
        node_cnt = 0
        for tree in self.trees:
            node_cnt += tree.node_cnt
        return node_cnt

    def __str__(self):
        result = ""
        for tree in self.trees:
            result += str(tree)
        return result

    def __len__(self):
        return len(self.trees)

    def __iter__(self):
        return iter(self.trees)


class InfoTreeTaskResult:
    source: list | None
    entity: list | None
    relation: list | None
    others: dict | None

    def __init__(self,
                 source: list | None,
                 entity: list | None,
                 relation: list | None,
                 others: dict | None = None):
        self.source = source
        self.entity = entity
        self.relation = relation
        self.others = others

    def dump_dict(self):
        return {
            "source": self.source,
            "entity": self.entity,
            "relation": self.relation,
            "others": self.others
        }


class InfoTreeTask:
    task_id: str | None
    task_prompt: str | None
    task_result: InfoTreeTaskResult | None
    task_status: int | None     # 三种任务状态：失败、完成、待修正（0,1,2）

    def __init__(self,
                 task_id: str | None = None,
                 task_prompt: str | None = None,
                 task_result: InfoTreeTaskResult | None = None,
                 task_status: int | None = None):
        self.task_id = task_id
        self.task_prompt = task_prompt
        self.task_result = task_result
        self.task_status = task_status

    def dump_dict(self):
        return {
            "task_id": self.task_id,
            "task_prompt": self.task_prompt,
            "task_response": self.task_result.dump_dict(),
            "task_status": self.task_status
        }

    @staticmethod
    def load_dict(task_dict: dict):
        return InfoTreeTask(
            task_id=task_dict["task_id"],
            task_prompt=task_dict["task_prompt"],
            task_result=InfoTreeTaskResult(
                source=task_dict["task_response"]["source"],
                entity=task_dict["task_response"]["entity"],
                relation=task_dict["task_response"]["relation"],
                others=task_dict["task_response"]["others"]
            ),
            task_status=task_dict["task_status"]
        )