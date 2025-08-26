export class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }

  size(): number {
    return this.items.length;
  }

  clear(): void {
    this.items = [];
  }

  [Symbol.iterator](): Iterator<T> {
    let index = 0;
    const items = this.items.slice(); // shallow copy
    return {
        next(): IteratorResult<T> {
            if (index < items.length) {
                return { value: items[index++], done: false };
            } else {
                return { value: undefined as any, done: true };
            }
        }
    };
  }
}