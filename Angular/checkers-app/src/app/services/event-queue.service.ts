import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EventQueueService {
  private eventSubject = new Subject<any>();    // ToDo: checkersEvent

  constructor() { }

  emitEvent(event: any): void {   // ToDo: checkersEvent
    this.eventSubject.next(event);
  }

  subscribeToEvents() {
    return this.eventSubject.asObservable();
  }
}
