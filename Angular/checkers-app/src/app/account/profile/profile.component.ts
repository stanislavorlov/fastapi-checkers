import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { ProfileDto } from '../../models/profile-dto';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private router = inject(Router);

  profileForm: FormGroup;
  loading = true;
  saving = false;
  message = '';

  constructor() {
    this.profileForm = this.fb.group({
      email: [{ value: '', disabled: true }, [Validators.required, Validators.email]],
      username: ['', [Validators.required, Validators.minLength(3)]],
      first_name: [''],
      last_name: [''],
      language: [''],
      bio: [''],
      country: [''],
      avatar_url: ['']
    });
  }

  ngOnInit(): void {
    this.userService.getProfile().subscribe({
      next: (profile) => {
        this.profileForm.patchValue(profile);
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load profile', err);
        this.message = 'Failed to load profile data.';
        this.loading = false;
      }
    });
  }

  save(): void {
    if (this.profileForm.invalid) return;

    this.saving = true;
    this.message = '';

    const updatedProfile = this.profileForm.getRawValue() as ProfileDto;

    this.userService.updateProfile(updatedProfile).subscribe({
      next: () => {
        this.message = 'Profile updated successfully!';
        this.saving = false;
        setTimeout(() => this.message = '', 3000);
      },
      error: (err) => {
        console.error('Failed to update profile', err);
        this.message = 'Failed to update profile. Please try again.';
        this.saving = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/']);
  }
}
