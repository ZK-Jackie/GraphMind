class InfoNode:
    title: str
    content: str | None
    level: int
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

    def __iter__(self):
        # 生成器，用于遍历当前节点及其所有子节点
        yield self.get_title_path(), self.content
        for child in self.children:
            yield from child


class InfoTree:
    main_root: InfoNode

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
    trees: list

    def __init__(self):
        self.trees = []

    def add_tree(self, tree: InfoTree):
        self.trees.append(tree)

    def __str__(self):
        result = ""
        for tree in self.trees:
            result += str(tree)
        return result

    def __len__(self):
        return len(self.trees)

    def __iter__(self):
        return iter(self.trees)
