export class GameId {
    id: string;

    constructor(id: string) {
        this.id = id;

        if (!this.validate(id)) {
            throw new Error('Invalid Game ID format');
        }
    }

    get value(): string {
        return this.id;
    }

    public static tryParse(id: string): GameId | null {
        try {
            return new GameId(id);
        } catch {
            return null;
        }
    }

    private validate(id: string): boolean {
        const regex = /^[a-fA-F0-9]{24}$/;
        return regex.test(id);
    }
}