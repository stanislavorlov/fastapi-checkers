import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LocalStorageService {

  public static readonly JWT_ACCESS_TOKEN = 'jwt_access_token';

  setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      // Ignore errors, e.g., on server-side
    }
  }

  getItem(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      // Ignore errors
    }
  }

  clear(): void {
    try {
      localStorage.clear();
    } catch (e) {
      // Ignore errors
    }
  }
}
