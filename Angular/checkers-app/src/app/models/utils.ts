export class Utils {
    public static parsePDN(pdn: string): string[] {
        const sep = pdn.includes("x") ? "x" : "-";

        try {
            return pdn
                .split(sep)
                .map(x => x.trim().replace(/"/g, ""))
                .filter(n => !isNaN(parseInt(n, 10))); // drop non-numeric parts
        } catch {
            return [];
        }
    }

    public static pairwise<T>(arr: T[]): [T, T][] {
        const result: [T, T][] = [];
        for (let i = 0; i < arr.length - 1; i++) {
            result.push([arr[i], arr[i + 1]]);
        }
        return result;
    }
}