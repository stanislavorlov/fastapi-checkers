import { Component } from '@angular/core';

@Component({
    selector: 'app-history',
    standalone: true,
    template: `
    <div style="padding: 2rem; color: white;">
      <h1>Game History</h1>
      <p>This is where your past games will be displayed.</p>
      <button (click)="goBack()" class="button-9 blue">Back</button>
    </div>
  `,
    styles: [`
    .button-9 {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      background-color: #3b82f6;
      color: white;
    }
  `]
})
export class HistoryComponent {
    constructor() { }
    goBack() {
        window.history.back();
    }
}
