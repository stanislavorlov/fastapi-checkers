export class Stack<T> {
    private _items: T[] = [];

    constructor(initialItems?: T[]) {
        if (initialItems) {
            this._items = initialItems;
        }
    }

    get items(): T[] {
        return [...this._items];
    }

    push(item: T): void {
        this._items.push(item);
    }

    pop(): T | undefined {
        return this._items.pop();
    }

    peek(): T | undefined {
        return this._items[this._items.length - 1];
    }

    isEmpty(): boolean {
        return this._items.length === 0;
    }

    clear(): void {
        this._items = [];
    }

    print(): void {
        console.log(this.items.join(", "));
    }
}