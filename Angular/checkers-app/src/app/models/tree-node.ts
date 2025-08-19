import { Square } from "./square";

export class TreeNode {
    value: Square;
    left?: TreeNode | null;
    right?: TreeNode | null;

    constructor(value: Square, left: TreeNode | null = null, right: TreeNode | null = null) {
        this.value = value;
        this.left = left;
        this.right = right;
    }

    addLeft(node: TreeNode): void {
        this.left = node;
    }

    addRight(node: TreeNode): void {
        this.right = node;
    }

    select() {
        this.value.select();
        this.left?.select();
        this.right?.select();
    }

    unselect() {
        this.value.unselect();
        this.left?.unselect();
        this.right?.unselect();
    }

    toList() {
        const list: Square[] = [];
        if (this.left) {
            list.push(...this.left.toList());
        }
        list.push(this.value);
        if (this.right) {
            list.push(...this.right.toList());
        }
        return list;
    }
}