import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { UserService } from './services/user.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {

  private readonly router = inject(Router);

  constructor(private userService: UserService) {

  }

  async ngOnInit(): Promise<void> {
    await this.userService.init();
  }

  backMenu(): void {
    this.router.navigate(['/'], { queryParams: {} });
  }
}
