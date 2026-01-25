import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, CommonModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  private readonly router = inject(Router);

  constructor(private userService: UserService) { 
    this.loginForm = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [Validators.required, Validators.minLength(6)])
    });
  }

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  login(): void {
    if (this.loginForm.valid) {
      console.log(`Logging in with email: ${this.loginForm.value.email} and password: ${this.loginForm.value.password}`);
      this.userService.authenticate(this.loginForm.value.email, this.loginForm.value.password).subscribe({
        next: (token) => {
          this.router.navigate(['/']);
        },
        error: (error) => {
          alert('Login failed: ' + error);
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }

  backMenu(): void {
    this.router.navigate(['/'], { queryParams: {} });
  }
}
