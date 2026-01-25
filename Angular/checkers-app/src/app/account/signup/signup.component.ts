import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-signup',
  imports: [ReactiveFormsModule, CommonModule, RouterModule],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.css'
})
export class SignupComponent {
  signupForm: FormGroup;
  private readonly router = inject(Router);

  passwordMatchValidator: ValidatorFn = (control: AbstractControl): { [key: string]: boolean } | null => {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');

    if (!password || !confirmPassword || password.value === confirmPassword.value) {
      return null; // No mismatch
    }
    return { 'passwordMismatch': true }; // Mismatch error
  };

  constructor(private userService: UserService) { 
    this.signupForm = new FormGroup({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', [Validators.required, Validators.minLength(6)]),
      confirmPassword: new FormControl('', [Validators.required]),
      level: new FormControl('beginner'),
    }, { validators: this.passwordMatchValidator });
  }

  get email() {
    return this.signupForm.get('email');
  }

  get password() {
    return this.signupForm.get('password');
  }

  get confirmPassword() {
    return this.signupForm.get('confirmPassword');
  }

  signup(): void {
    if (this.signupForm.valid) {
      console.log(`Signing up with email: ${this.signupForm.value.email} and password: ${this.signupForm.value.password} with level: ${this.signupForm.value.level}`);
      this.userService.register(
        this.signupForm.value.email, 
        this.signupForm.value.password, 
        this.signupForm.value.level).subscribe({
        next: (response) => {
          console.log('Signup successful:', response);
        },
        error: (error) => {
          console.error('Signup failed:', error);
        }
      });
    } else {
      this.signupForm.markAllAsTouched();
    }
  }

  backMenu(): void {
    this.router.navigate(['/'], { queryParams: {} });
  }
}
