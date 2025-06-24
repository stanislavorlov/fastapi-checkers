import { TestBed } from '@angular/core/testing';

import { CheckersService } from './checkers.service';

describe('CheckersService', () => {
  let service: CheckersService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CheckersService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
