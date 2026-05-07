import { bootstrapApplication } from '@angular/platform-browser';
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <main>
      <h1>Angular 19 funcionando</h1>
      <p>Servidor listo en localhost:4200</p>
    </main>
  `,
  styles: [`
    :host { font-family: Arial, sans-serif; display:block; padding:2rem; }
    h1 { color: #0f172a; margin:0 0 1rem; }
    p { color: #334155; }
  `]
})
class AppComponent {}

bootstrapApplication(AppComponent).catch((err) => console.error(err));
