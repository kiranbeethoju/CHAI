// azure-gpt.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AzureGPTService {
  constructor(private http: HttpClient) {}

  callAzureGPT(payload: any, selectedVersion: string): Observable<string> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + sessionStorage.getItem('token')
      }),
      responseType: 'text' as 'json'
    };

    return new Observable<string>(observer => {
      this.http.post(
        environment.CallAzureGPT,
        { Version: selectedVersion, Payload: JSON.stringify(payload) },
        httpOptions
      ).subscribe({
        next: (response: any) => {
          const reader = new Response(response).body?.getReader();
          if (!reader) {
            observer.error('Failed to get response reader');
            return;
          }

          const decoder = new TextDecoder();

          const processStream = ({ done, value }: ReadableStreamReadResult<Uint8Array>): Promise<void> => {
            if (done) {
              observer.complete();
              return Promise.resolve();
            }

            const chunk = decoder.decode(value, { stream: true });
            observer.next(chunk);

            return reader.read().then(processStream);
          };

          reader.read().then(processStream).catch(error => observer.error(error));
        },
        error: (error) => observer.error(error)
      });
    });
  }
}

// azure-gpt.component.ts
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { AzureGPTService } from './azure-gpt.service';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { DatePipe } from '@angular/common';
import { marked } from 'marked';

@Component({
  selector: 'app-azure-gpt',
  template: `
    <div>
      <textarea [(ngModel)]="textPrompt" placeholder="Enter your prompt"></textarea>
      <button (click)="sendRequest()" [disabled]="isLoading">Send</button>
      <div *ngIf="isLoading">Loading...</div>
      <div [innerHTML]="processedResponse"></div>
    </div>
  `
})
export class AzureGPTComponent implements OnInit {
  textPrompt = '';
  streamingResponse = '';
  processedResponse = '';
  isLoading = false;
  selectedVersion = ''; // Set this to your default version

  constructor(
    private azureGPTService: AzureGPTService,
    private router: Router,
    private toastr: ToastrService,
    private datepipe: DatePipe,
    private changeDetectorRef: ChangeDetectorRef
  ) {}

  ngOnInit() {
    // Initialize component
  }

  sendRequest() {
    this.isLoading = true;
    this.streamingResponse = '';
    this.processedResponse = '';

    const payload = {
      // Your payload structure here
      messages: [{ role: 'user', content: this.textPrompt }]
    };

    this.azureGPTService.callAzureGPT(payload, this.selectedVersion).subscribe({
      next: (chunk: string) => {
        this.streamingResponse += chunk;
        this.processedResponse = this.processResponse(this.streamingResponse);
        this.changeDetectorRef.detectChanges();
      },
      error: (error) => {
        console.error('Error:', error);
        this.isLoading = false;
        if (error.status === 401) {
          this.router.navigate(['login']);
        } else {
          this.toastr.warning("AzureGPT is not running or encountered an error");
        }
      },
      complete: () => {
        console.log('Stream complete');
        this.isLoading = false;
        this.saveToHistory();
      }
    });
  }

  processResponse(response: string): string {
    // Process the response (e.g., convert markdown to HTML)
    return marked.parse(response);
  }

  saveToHistory() {
    const item = {
      prompt: this.textPrompt,
      result: this.processedResponse,
      requestedDate: this.datepipe.transform(new Date(), 'yyyy-MM-ddTHH:mm:ss')
    };
    // Save item to history (implement this method based on your app's logic)
  }
}
