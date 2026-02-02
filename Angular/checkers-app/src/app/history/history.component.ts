import { Component, OnInit } from '@angular/core';
import { CheckersService } from '../services/checkers.service';

@Component({
  selector: 'app-history',
  standalone: true,
  templateUrl: './history.component.html',
  styleUrl: './history.component.css',
})
export class HistoryComponent implements OnInit {
  constructor(private checkersService: CheckersService) { }

  ngOnInit(): void {
    this.checkersService.getPlayerGames().subscribe((history) => {
      console.log(history);
    });
  }

  goBack() {
    window.history.back();
  }
}
