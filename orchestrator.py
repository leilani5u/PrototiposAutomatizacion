import os

os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

import subprocess
from pathlib import Path

from agents.cleaning_agent import CleaningAgent
from agents.file_writer_agent import FileWriterAgent
from agents.requirements_agent import RequirementsAgent
from agents.transcription_agent import TranscriptionAgent
from agents.ui_generation_agent import UIGenerationAgent
from agents.ui_improvement_agent import UIImprovementAgent
from agents.validation_agent import ValidationAgent
from models.project_result import ProjectResult


MEDIA_EXTENSIONS = {
    ".aac",
    ".avi",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".webm",
    ".wav",
    ".wma",
}
TRANSCRIPTION_EXTENSIONS = {".txt", ".md", ".srt", ".vtt"}
ANGULAR_REQUIRED_FILES = [
    "angular.json",
    "package.json",
    "tsconfig.json",
    "tsconfig.app.json",
    "src/main.ts",
    "src/index.html",
    "src/app/app.component.ts",
    "src/app/app.component.scss",
    "src/app/app.config.ts",
    "src/app/app.routes.ts",
    "src/styles.scss",
    "src/environments/environment.ts",
    "src/app/layout/shell/shell.component.ts",
    "src/app/pages/dashboard/dashboard.page.ts",
    "src/app/pages/customers/customers.page.ts",
    "src/app/pages/settings/settings.page.ts",
    "REQUERIMIENTOS.md",
    "ARQUITECTURA_PROYECTO.md",
    "BUILD_LOG.md",
]
TREE_EXCLUDED_DIRS = {"node_modules", "dist", ".angular", ".git"}
MODO_TECNICO = False
MAX_BUILD_ATTEMPTS = 3

MODELS_REQUIREMENT = """
export type RequirementStatus = 'nuevo' | 'en_progreso' | 'validado' | 'bloqueado';
export type RequirementPriority = 'alta' | 'media' | 'baja';

export interface Requirement {
  id: string;
  title: string;
  owner: string;
  area: string;
  status: RequirementStatus;
  priority: RequirementPriority;
  dueDate: string;
  progress: number;
}
"""

MODELS_CUSTOMER = """
export interface Customer {
  id: string;
  company: string;
  contact: string;
  plan: 'Growth' | 'Scale' | 'Enterprise';
  health: number;
  revenue: number;
  lastActivity: string;
}
"""

MODELS_KPI = """
export interface Kpi {
  label: string;
  value: string;
  trend: number;
  tone: 'brand' | 'success' | 'warning' | 'danger';
}
"""

PREMIUM_GLOBAL_SCSS = """
:root {
  color-scheme: light;
  --bg: #f6f7fb;
  --panel: #ffffff;
  --panel-strong: #f8fafc;
  --text: #0f172a;
  --muted: #64748b;
  --line: #e2e8f0;
  --brand: #635bff;
  --brand-strong: #4f46e5;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #dc2626;
  --shadow: 0 20px 60px rgba(15, 23, 42, 0.1);
}

* { box-sizing: border-box; }
html, body { height: 100%; }

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: radial-gradient(circle at top left, rgba(99, 91, 255, 0.12), transparent 28rem), var(--bg);
  color: var(--text);
}

button, input, select, textarea { font: inherit; }
button { cursor: pointer; }
a { color: inherit; }

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
"""

DASHBOARD_SERVICE_TS = """
import { Injectable } from '@angular/core';
import { delay, of } from 'rxjs';
import { Customer } from '../models/customer.model';
import { Kpi } from '../models/kpi.model';
import { Requirement } from '../models/requirement.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  getOverview() {
    return of({
      kpis: this.kpis,
      requirements: this.requirements,
      customers: this.customers
    }).pipe(delay(650));
  }

  private readonly kpis: Kpi[] = [
    { label: 'Requisitos activos', value: '128', trend: 18, tone: 'brand' },
    { label: 'Tiempo medio de cierre', value: '4.2 dias', trend: -12, tone: 'success' },
    { label: 'Bloqueos abiertos', value: '9', trend: 6, tone: 'warning' },
    { label: 'Satisfaccion cliente', value: '96%', trend: 4, tone: 'success' }
  ];

  private readonly requirements: Requirement[] = [
    { id: 'REQ-1842', title: 'Flujo de aprobacion multi-area', owner: 'Ana Torres', area: 'Operaciones', status: 'en_progreso', priority: 'alta', dueDate: '2026-05-18', progress: 72 },
    { id: 'REQ-1837', title: 'Panel de evidencias por expediente', owner: 'Luis Medina', area: 'Atencion', status: 'validado', priority: 'media', dueDate: '2026-05-14', progress: 100 },
    { id: 'REQ-1829', title: 'Alertas SLA con escalamiento', owner: 'Mara Leon', area: 'Calidad', status: 'bloqueado', priority: 'alta', dueDate: '2026-05-10', progress: 38 },
    { id: 'REQ-1818', title: 'Reporte ejecutivo mensual', owner: 'Diego Rios', area: 'Direccion', status: 'nuevo', priority: 'baja', dueDate: '2026-05-26', progress: 12 }
  ];

  private readonly customers: Customer[] = [
    { id: 'SEG-001', company: 'Direccion de Planeacion', contact: 'Elena Cruz', plan: 'Enterprise', health: 94, revenue: 186000, lastActivity: '2026-05-04' },
    { id: 'SEG-018', company: 'Coordinacion Regional Norte', contact: 'Mario Vega', plan: 'Scale', health: 81, revenue: 96000, lastActivity: '2026-05-02' },
    { id: 'SEG-024', company: 'Unidad de Seguimiento', contact: 'Paula Ibarra', plan: 'Growth', health: 76, revenue: 54000, lastActivity: '2026-04-29' }
  ];
}
"""

SHELL_COMPONENT_TS = """
import { Component, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="shell" [class.nav-open]="navOpen()">
      <aside class="sidebar">
        <a class="brand" routerLink="/dashboard" aria-label="Inicio"><span>R</span><strong>Requisitos Suite</strong></a>
        <nav aria-label="Principal">
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <a routerLink="/clientes" routerLinkActive="active">Clientes</a>
          <a routerLink="/configuracion" routerLinkActive="active">Configuracion</a>
        </nav>
        <section class="workspace"><small>Workspace</small><strong>Seguimiento SEG</strong><p>96% cumplimiento operativo</p></section>
      </aside>
      <main class="content">
        <header class="topbar">
          <button class="menu" type="button" (click)="navOpen.set(!navOpen())" aria-label="Abrir navegacion">Menu</button>
          <label class="search"><span class="sr-only">Buscar</span><input type="search" placeholder="Buscar requisitos, clientes o responsables" /></label>
          <div class="actions"><button type="button">Invitar</button><span class="avatar" aria-label="Usuario actual">AB</span></div>
        </header>
        <router-outlet />
      </main>
    </div>
  `,
  styles: [`
    .shell{min-height:100vh;display:grid;grid-template-columns:280px 1fr}.sidebar{position:sticky;top:0;height:100vh;padding:24px;border-right:1px solid var(--line);background:rgba(255,255,255,.78);backdrop-filter:blur(20px)}.brand{display:flex;align-items:center;gap:12px;text-decoration:none;margin-bottom:32px}.brand span{display:grid;place-items:center;width:38px;height:38px;border-radius:14px;color:#fff;background:linear-gradient(135deg,var(--brand),#06b6d4);box-shadow:0 12px 28px rgba(99,91,255,.28)}nav{display:grid;gap:8px}nav a{padding:12px 14px;border-radius:14px;color:var(--muted);text-decoration:none;transition:160ms ease}nav a:hover,nav a.active{color:var(--text);background:#eef2ff}.workspace{position:absolute;left:24px;right:24px;bottom:24px;padding:16px;border:1px solid var(--line);border-radius:18px;background:var(--panel)}.workspace small,.workspace p{color:var(--muted)}.workspace p{margin:6px 0 0;font-size:13px}.content{min-width:0;padding:22px}.topbar{display:flex;align-items:center;gap:16px;margin-bottom:22px}.menu{display:none}.search{flex:1}input{width:100%;border:1px solid var(--line);border-radius:16px;background:var(--panel);padding:13px 16px;outline:none;transition:160ms ease}input:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(99,91,255,.12)}.actions{display:flex;align-items:center;gap:10px}.actions button,.menu{border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:11px 14px;font-weight:700}.avatar{display:grid;place-items:center;width:40px;height:40px;border-radius:999px;background:#0f172a;color:white;font-size:13px;font-weight:800}@media (max-width:900px){.shell{grid-template-columns:1fr}.sidebar{position:fixed;z-index:10;width:min(300px,86vw);transform:translateX(-105%);transition:180ms ease}.shell.nav-open .sidebar{transform:translateX(0)}.menu{display:inline-flex}.content{padding:16px}}
  `]
})
export class ShellComponent {
  readonly navOpen = signal(false);
}
"""

SKELETON_COMPONENT_TS = """
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-skeleton',
  standalone: true,
  template: '<div class="skeleton" [style.height.px]="height" [style.border-radius.px]="radius"></div>',
  styles: [`.skeleton{width:100%;background:linear-gradient(90deg,#eef2f7,#f8fafc,#eef2f7);background-size:240% 100%;animation:pulse 1.2s ease-in-out infinite}@keyframes pulse{0%{background-position:100% 0}100%{background-position:-100% 0}}`]
})
export class SkeletonComponent {
  @Input() height = 96;
  @Input() radius = 16;
}
"""

TOAST_COMPONENT_TS = """
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-toast',
  standalone: true,
  template: `<aside class="toast" role="status" aria-live="polite" [class.visible]="visible"><span class="dot"></span><div><strong>{{ title }}</strong><p>{{ message }}</p></div></aside>`,
  styles: [`.toast{position:fixed;right:24px;bottom:24px;display:flex;gap:12px;align-items:flex-start;max-width:360px;padding:16px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.94);box-shadow:var(--shadow);opacity:0;transform:translateY(16px);pointer-events:none;transition:180ms ease;backdrop-filter:blur(18px)}.toast.visible{opacity:1;transform:translateY(0)}.dot{width:10px;height:10px;margin-top:4px;border-radius:999px;background:var(--success)}strong,p{margin:0}p{color:var(--muted);font-size:13px}`]
})
export class ToastComponent {
  @Input() visible = false;
  @Input() title = 'Operacion completada';
  @Input() message = 'Los cambios se guardaron correctamente.';
}
"""

MODAL_COMPONENT_TS = """
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-modal',
  standalone: true,
  template: `@if (open) {<div class="backdrop" (click)="close.emit()" aria-hidden="true"></div><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><header><div><p>Nuevo registro</p><h2 id="modal-title">{{ title }}</h2></div><button type="button" (click)="close.emit()" aria-label="Cerrar">x</button></header><ng-content /></section>}`,
  styles: [`.backdrop{position:fixed;inset:0;z-index:20;background:rgba(15,23,42,.42);backdrop-filter:blur(6px)}.modal{position:fixed;z-index:21;top:50%;left:50%;width:min(560px,calc(100vw - 32px));transform:translate(-50%,-50%);border:1px solid var(--line);border-radius:24px;background:var(--panel);box-shadow:var(--shadow);padding:22px}header{display:flex;justify-content:space-between;gap:16px;margin-bottom:20px}h2,p{margin:0}p{color:var(--brand);font-size:13px;font-weight:700;text-transform:uppercase}button{width:36px;height:36px;border:1px solid var(--line);border-radius:12px;background:var(--panel-strong)}`]
})
export class ModalComponent {
  @Input() open = false;
  @Input() title = 'Crear elemento';
  @Output() close = new EventEmitter<void>();
}
"""

DASHBOARD_PAGE_TS = """
import { CommonModule, CurrencyPipe, DatePipe, NgClass } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Customer } from '../../models/customer.model';
import { Kpi } from '../../models/kpi.model';
import { Requirement } from '../../models/requirement.model';
import { DashboardService } from '../../services/dashboard.service';
import { RequirementsContextService } from '../../services/requirements-context.service';
import { ModalComponent } from '../../shared/components/modal/modal.component';
import { SkeletonComponent } from '../../shared/components/skeleton/skeleton.component';
import { ToastComponent } from '../../shared/components/toast/toast.component';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, CurrencyPipe, DatePipe, NgClass, ReactiveFormsModule, ModalComponent, SkeletonComponent, ToastComponent],
  template: `
    <section class="page">
      <div class="hero"><div><p>Operacion comercial</p><h1>Centro de seguimiento de requisitos</h1><span>Control ejecutivo de solicitudes, clientes, bloqueos y entregables.</span></div><button type="button" (click)="openModal.set(true)">Nuevo requisito</button></div>
      <div class="capabilities">@for (capability of context.detectedCapabilities; track capability) {<span>{{ capability }}</span>}</div>
      @if (loading()) {<div class="kpi-grid"><app-skeleton *ngFor="let item of [1,2,3,4]" [height]="132" /></div>} @else {<div class="kpi-grid">@for (kpi of kpis(); track kpi.label) {<article class="kpi" [class]="kpi.tone"><span>{{ kpi.label }}</span><strong>{{ kpi.value }}</strong><small [class.down]="kpi.trend < 0">{{ kpi.trend > 0 ? '+' : '' }}{{ kpi.trend }}% vs. mes anterior</small></article>}</div>}
      <section class="panel">
        <header class="panel-header"><div><p>Pipeline</p><h2>Requisitos activos</h2></div><div class="filters"><input type="search" placeholder="Buscar requisito" [value]="query()" (input)="query.set($any($event.target).value)" /><select [value]="status()" (change)="status.set($any($event.target).value)"><option value="todos">Todos</option><option value="nuevo">Nuevo</option><option value="en_progreso">En progreso</option><option value="validado">Validado</option><option value="bloqueado">Bloqueado</option></select></div></header>
        @if (filteredRequirements().length === 0) {<div class="empty"><strong>No hay requisitos con esos filtros</strong><p>Ajusta la busqueda o registra un nuevo requerimiento.</p></div>} @else {<div class="table-wrap"><table><thead><tr><th>ID</th><th>Requisito</th><th>Responsable</th><th>Estado</th><th>Avance</th><th>Fecha</th></tr></thead><tbody>@for (item of filteredRequirements(); track item.id) {<tr><td>{{ item.id }}</td><td><strong>{{ item.title }}</strong><span>{{ item.area }} - prioridad {{ item.priority }}</span></td><td>{{ item.owner }}</td><td><span class="status" [ngClass]="item.status">{{ item.status.replace('_', ' ') }}</span></td><td><div class="progress"><i [style.width.%]="item.progress"></i></div><small>{{ item.progress }}%</small></td><td>{{ item.dueDate | date:'dd MMM' }}</td></tr>}</tbody></table></div>}
      </section>
      <section class="grid-two">
        <article class="panel"><header class="panel-header"><div><p>Clientes</p><h2>Cuentas prioritarias</h2></div></header>@for (customer of customers(); track customer.id) {<div class="customer-card"><div><strong>{{ customer.company }}</strong><span>{{ customer.contact }} - {{ customer.plan }}</span></div><div><b>{{ customer.revenue | currency:'MXN':'symbol':'1.0-0' }}</b><small>Health {{ customer.health }}%</small></div></div>}</article>
        <article class="panel form-panel"><header class="panel-header"><div><p>Accion rapida</p><h2>Registrar decision</h2></div></header><form [formGroup]="decisionForm" (ngSubmit)="saveDecision()"><label>Decision <input formControlName="title" placeholder="Aprobar alcance del modulo de evidencias" /></label><label>Riesgo <select formControlName="risk"><option value="bajo">Bajo</option><option value="medio">Medio</option><option value="alto">Alto</option></select></label><button type="submit" [disabled]="decisionForm.invalid">Guardar decision</button>@if (decisionForm.controls.title.invalid && decisionForm.controls.title.touched) {<small class="error">Escribe una decision de al menos 8 caracteres.</small>}</form></article>
      </section>
    </section>
    <app-modal [open]="openModal()" title="Crear requisito" (close)="openModal.set(false)"><form class="modal-form" [formGroup]="requirementForm" (ngSubmit)="createRequirement()"><label>Titulo <input formControlName="title" /></label><label>Responsable <input formControlName="owner" /></label><label>Prioridad <select formControlName="priority"><option value="alta">Alta</option><option value="media">Media</option><option value="baja">Baja</option></select></label><button type="submit" [disabled]="requirementForm.invalid">Crear requisito</button></form></app-modal>
    <app-toast [visible]="toastVisible()" title="Cambios guardados" message="La operacion se registro en el tablero." />
  `,
  styleUrl: './dashboard.page.scss'
})
export class DashboardPage implements OnInit {
  private readonly service = inject(DashboardService);
  private readonly fb = inject(FormBuilder);
  readonly context = inject(RequirementsContextService);

  readonly loading = signal(true);
  readonly openModal = signal(false);
  readonly toastVisible = signal(false);
  readonly query = signal('');
  readonly status = signal('todos');
  readonly kpis = signal<Kpi[]>([]);
  readonly requirements = signal<Requirement[]>([]);
  readonly customers = signal<Customer[]>([]);

  readonly filteredRequirements = computed(() => {
    const term = this.query().toLowerCase().trim();
    const status = this.status();
    return this.requirements().filter((item) => {
      const matchesTerm = !term || `${item.id} ${item.title} ${item.owner} ${item.area}`.toLowerCase().includes(term);
      return matchesTerm && (status === 'todos' || item.status === status);
    });
  });

  readonly decisionForm = this.fb.nonNullable.group({ title: ['', [Validators.required, Validators.minLength(8)]], risk: ['medio', Validators.required] });
  readonly requirementForm = this.fb.nonNullable.group({ title: ['', [Validators.required, Validators.minLength(8)]], owner: ['', Validators.required], priority: ['media', Validators.required] });

  ngOnInit() {
    this.service.getOverview().subscribe({ next: (data) => { this.kpis.set(data.kpis); this.requirements.set(data.requirements); this.customers.set(data.customers); this.loading.set(false); }, error: () => this.loading.set(false) });
  }

  saveDecision() {
    if (this.decisionForm.invalid) { this.decisionForm.markAllAsTouched(); return; }
    this.showToast();
    this.decisionForm.reset({ title: '', risk: 'medio' });
  }

  createRequirement() {
    if (this.requirementForm.invalid) { this.requirementForm.markAllAsTouched(); return; }
    const value = this.requirementForm.getRawValue();
    this.requirements.update((items) => [{ id: `REQ-${1900 + items.length}`, title: value.title, owner: value.owner, area: 'Producto', status: 'nuevo', priority: value.priority as Requirement['priority'], dueDate: '2026-06-03', progress: 8 }, ...items]);
    this.openModal.set(false);
    this.requirementForm.reset({ title: '', owner: '', priority: 'media' });
    this.showToast();
  }

  private showToast() {
    this.toastVisible.set(true);
    window.setTimeout(() => this.toastVisible.set(false), 2600);
  }
}
"""

DASHBOARD_PAGE_SCSS = """
.page{display:grid;gap:22px}.hero,.panel,.kpi{border:1px solid var(--line);border-radius:24px;background:rgba(255,255,255,.88);box-shadow:0 18px 44px rgba(15,23,42,.07)}.hero{display:flex;justify-content:space-between;gap:24px;padding:30px}.capabilities{display:flex;flex-wrap:wrap;gap:10px}.capabilities span{border:1px solid var(--line);border-radius:999px;background:#fff;padding:8px 12px;color:var(--brand);font-size:12px;font-weight:800;text-transform:uppercase}.hero p,.panel-header p{margin:0 0 6px;color:var(--brand);font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}h1,h2,.hero span{margin:0}h1{font-size:clamp(28px,4vw,46px);line-height:1}.hero span{display:block;margin-top:12px;color:var(--muted)}button{border:0;border-radius:16px;background:var(--brand);color:white;padding:12px 16px;font-weight:800}button:disabled{opacity:.52;cursor:not-allowed}.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.kpi{padding:20px}.kpi span,.kpi small{color:var(--muted)}.kpi strong{display:block;margin:12px 0 8px;font-size:30px}.kpi small:not(.down){color:var(--success)}.down{color:var(--danger)}.panel{padding:22px}.panel-header{display:flex;justify-content:space-between;gap:16px;margin-bottom:18px}.filters{display:flex;gap:10px}input,select{width:100%;border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:12px 14px;outline:none}input:focus,select:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(99,91,255,.12)}.table-wrap{overflow-x:auto}table{width:100%;min-width:780px;border-collapse:collapse}th,td{padding:14px 12px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--muted);font-size:12px;text-transform:uppercase}td span{display:block;color:var(--muted);font-size:13px}tr:hover td{background:#f8fafc}.status{display:inline-flex;border-radius:999px;padding:6px 10px;color:var(--text);background:#eef2ff}.status.validado{background:#dcfce7}.status.bloqueado{background:#fee2e2}.progress{height:8px;border-radius:999px;background:#e2e8f0;overflow:hidden}.progress i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,var(--brand),#06b6d4)}.grid-two{display:grid;grid-template-columns:1.15fr .85fr;gap:18px}.customer-card{display:flex;justify-content:space-between;gap:16px;padding:16px 0;border-bottom:1px solid var(--line)}.customer-card:last-child{border-bottom:0}.customer-card span,.customer-card small{display:block;color:var(--muted);margin-top:4px}form,.modal-form{display:grid;gap:14px}label{display:grid;gap:8px;color:var(--muted);font-size:13px;font-weight:700}.error{color:var(--danger)}.empty{display:grid;place-items:center;min-height:180px;border:1px dashed var(--line);border-radius:18px;color:var(--muted);text-align:center}.empty strong{color:var(--text)}@media (max-width:1100px){.kpi-grid,.grid-two{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:720px){.hero,.panel-header,.filters,.customer-card{flex-direction:column}.kpi-grid,.grid-two{grid-template-columns:1fr}}
"""

CUSTOMERS_PAGE_TS = """
import { CommonModule, CurrencyPipe } from '@angular/common';
import { Component, OnInit, computed, signal } from '@angular/core';
import { Customer } from '../../models/customer.model';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-customers-page',
  standalone: true,
  imports: [CommonModule, CurrencyPipe],
  template: `
    <section class="panel">
      <header><div><p>Relacion comercial</p><h1>Clientes y unidades operativas</h1></div><input type="search" placeholder="Buscar cliente" [value]="query()" (input)="query.set($any($event.target).value)" /></header>
      <div class="cards">@for (customer of filteredCustomers(); track customer.id) {<article><span>{{ customer.id }}</span><h2>{{ customer.company }}</h2><p>{{ customer.contact }}</p><div class="meta"><strong>{{ customer.revenue | currency:'MXN':'symbol':'1.0-0' }}</strong><small>{{ customer.plan }}</small></div><meter min="0" max="100" [value]="customer.health"></meter><small>Salud de cuenta {{ customer.health }}%</small></article>}</div>
    </section>
  `,
  styles: [`.panel{border:1px solid var(--line);border-radius:24px;background:var(--panel);padding:24px;box-shadow:var(--shadow)}header{display:flex;justify-content:space-between;gap:16px;margin-bottom:20px}p,h1,h2{margin:0}header p,article span{color:var(--brand);font-size:12px;font-weight:800;text-transform:uppercase}input{width:min(360px,100%);border:1px solid var(--line);border-radius:14px;padding:12px 14px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{padding:18px;border:1px solid var(--line);border-radius:20px;background:var(--panel-strong);transition:160ms ease}article:hover{transform:translateY(-2px);box-shadow:0 18px 38px rgba(15,23,42,.08)}article p,small{color:var(--muted)}.meta{display:flex;justify-content:space-between;margin:18px 0}meter{width:100%;height:10px}@media (max-width:980px){.cards{grid-template-columns:1fr}header{flex-direction:column}}`]
})
export class CustomersPage implements OnInit {
  readonly query = signal('');
  readonly customers = signal<Customer[]>([]);
  readonly filteredCustomers = computed(() => {
    const term = this.query().toLowerCase().trim();
    return this.customers().filter((customer) => `${customer.company} ${customer.contact} ${customer.plan}`.toLowerCase().includes(term));
  });

  constructor(private readonly service: DashboardService) {}

  ngOnInit() {
    this.service.getOverview().subscribe((data) => this.customers.set(data.customers));
  }
}
"""

SETTINGS_PAGE_TS = """
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastComponent } from '../../shared/components/toast/toast.component';

@Component({
  selector: 'app-settings-page',
  standalone: true,
  imports: [ReactiveFormsModule, ToastComponent],
  template: `
    <section class="panel">
      <header><p>Administracion</p><h1>Configuracion del workspace</h1></header>
      <form [formGroup]="form" (ngSubmit)="save()">
        <label>Nombre del workspace <input formControlName="workspace" /></label>
        <label>Correo de notificaciones <input formControlName="email" type="email" /></label>
        <label>SLA critico <select formControlName="sla"><option value="24">24 horas</option><option value="48">48 horas</option><option value="72">72 horas</option></select></label>
        <label class="toggle"><input type="checkbox" formControlName="darkMode" /> Activar modo oscuro opcional</label>
        <button type="submit" [disabled]="form.invalid">Guardar configuracion</button>
      </form>
    </section>
    <app-toast [visible]="toastVisible()" title="Configuracion guardada" message="Los cambios estan listos para sincronizarse con la API." />
  `,
  styles: [`.panel{max-width:760px;border:1px solid var(--line);border-radius:24px;background:var(--panel);padding:28px;box-shadow:var(--shadow)}p,h1{margin:0}p{color:var(--brand);font-size:12px;font-weight:800;text-transform:uppercase}form{display:grid;gap:16px;margin-top:24px}label{display:grid;gap:8px;color:var(--muted);font-weight:700}input,select{border:1px solid var(--line);border-radius:14px;padding:12px 14px;outline:none}.toggle{display:flex;align-items:center;gap:10px}.toggle input{width:18px;height:18px}button{width:fit-content;border:0;border-radius:16px;background:var(--brand);color:white;padding:12px 16px;font-weight:800}button:disabled{opacity:.52}`]
})
export class SettingsPage {
  private readonly fb = inject(FormBuilder);

  readonly toastVisible = signal(false);
  readonly form = this.fb.nonNullable.group({
    workspace: ['Seguimiento SEG', [Validators.required, Validators.minLength(4)]],
    email: ['operaciones@seg.local', [Validators.required, Validators.email]],
    sla: ['48', Validators.required],
    darkMode: [false]
  });
  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.toastVisible.set(true);
    window.setTimeout(() => this.toastVisible.set(false), 2600);
  }
}
"""

ARCHITECTURE_MD = """
# Arquitectura del Proyecto

## Estructura

- `src/app/core`: piezas transversales de plataforma.
- `src/app/shared`: componentes reutilizables sin dependencia de dominio.
- `src/app/features`: espacio para dominios desacoplados.
- `src/app/layout`: shell, navegacion principal y topbar.
- `src/app/services`: servicios listos para reemplazar mocks por API real.
- `src/app/guards`: reglas de acceso por ruta.
- `src/app/interceptors`: espacio para interceptores por dominio.
- `src/app/models`: contratos TypeScript del dominio.
- `src/app/pages`: pantallas lazy-loaded.
- `src/app/components`: componentes de producto reutilizables.

## Modulos y componentes

- `ShellComponent`: layout responsive con sidebar, header, navegacion y outlet.
- `DashboardPage`: KPIs, tabla filtrable, formularios, modal, toast, loading y empty states.
- `CustomersPage`: vista comercial con busqueda y tarjetas de cuentas.
- `SettingsPage`: formulario reactivo con validaciones.
- `ModalComponent`, `ToastComponent`, `SkeletonComponent`: UI compartida.

## Decisiones tecnicas

- Angular standalone components.
- Rutas con lazy loading por pagina.
- TypeScript estricto.
- SCSS global y estilos por componente.
- Signals para estado local de UI.
- RxJS para fuentes asincronas mock.
- Servicios preparados para conectar APIs reales.
- Guard funcional e interceptor HTTP funcional.

## Como escalar el proyecto

- Mover dominios grandes a `features/<dominio>`.
- Sustituir mocks de `DashboardService` por `HttpClient`.
- Agregar autenticacion real al `authGuard`.
- Agregar manejo centralizado de errores en el interceptor.
- Crear libreria de componentes en `shared` si el producto crece.
"""

def crear_carpeta_proyecto(base_dir, nombre_base):
    base_dir = Path(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    nombre_base = str(nombre_base).strip()
    if not nombre_base:
        raise ValueError("El nombre base del proyecto no puede estar vacio.")

    carpeta_original = base_dir / nombre_base
    carpeta_final = carpeta_original
    indice = 0
    separador = "" if nombre_base.endswith("_") else "_"

    while carpeta_final.exists():
        indice += 1
        carpeta_final = base_dir / f"{nombre_base}{separador}{indice}"

    os.makedirs(carpeta_final, exist_ok=True)

    print(f"[carpeta original detectada] {carpeta_original}")
    print(f"[nueva carpeta creada] {carpeta_final}")
    print(f"[ruta final del proyecto] {carpeta_final.resolve()}")

    return carpeta_final


def _carpeta_contiene_proyecto(path):
    path = Path(path)

    if not path.exists():
        return False

    angular_markers = [
        path / "angular.json",
        path / "package.json",
        path / "src" / "main.ts",
    ]

    if any(marker.exists() for marker in angular_markers):
        return True

    return any(path.iterdir())


def generar_estructura_proyecto(path):
    root = Path(path)
    output_file = root / "estructura_proyecto.txt"

    lines = [f"{root.name}/"]
    children = sorted(
        [
            child
            for child in root.iterdir()
            if child.name != output_file.name
            and not (child.is_dir() and child.name in TREE_EXCLUDED_DIRS)
        ],
        key=lambda item: (not item.is_dir(), item.name.lower()),
    )

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        _append_tree_line(child, "", is_last, lines)

    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not MODO_TECNICO:
        print(f"Estructura generada: {output_file}")
    return output_file


def _append_tree_line(path, prefix, is_last, lines):
    connector = "`-- " if is_last else "|-- "
    lines.append(f"{prefix}{connector}{path.name}{'/' if path.is_dir() else ''}")

    if not path.is_dir():
        return

    children = sorted(
        [
            child
            for child in path.iterdir()
            if not (child.is_dir() and child.name in TREE_EXCLUDED_DIRS)
        ],
        key=lambda item: (not item.is_dir(), item.name.lower()),
    )
    next_prefix = prefix + ("    " if is_last else "|   ")

    for index, child in enumerate(children):
        _append_tree_line(child, next_prefix, index == len(children) - 1, lines)


def premium_angular_files(base, requerimientos=""):
    requirements_context = build_requirements_context_ts(requerimientos)
    return {
        base / "package.json": """
{
  "name": "requisitos-suite",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  },
  "dependencies": {
    "@angular/animations": "^21.2.0",
    "@angular/common": "^21.2.0",
    "@angular/compiler": "^21.2.0",
    "@angular/core": "^21.2.0",
    "@angular/forms": "^21.2.0",
    "@angular/platform-browser": "^21.2.0",
    "@angular/platform-browser-dynamic": "^21.2.0",
    "@angular/router": "^21.2.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.15.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^21.2.0",
    "@angular/cli": "^21.2.0",
    "@angular/compiler-cli": "^21.2.0",
    "typescript": "~5.9.2"
  }
}
""",
        base / "angular.json": """
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "projects": {
    "requisitos-suite": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/requisitos-suite",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": [],
            "styles": ["src/styles.scss"],
            "scripts": []
          }
        }
      }
    }
  }
}
""",
        base / "tsconfig.json": """
{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2023",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2023", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
""",
        base / "tsconfig.app.json": """
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"],
  "include": ["src/**/*.d.ts", "src/**/*.ts"]
}
""",
        base / "src" / "main.ts": """
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((error) => console.error(error));
""",
        base / "src" / "index.html": """
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Requisitos Suite</title>
    <base href="/">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#0f172a">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <app-root></app-root>
  </body>
</html>
""",
        base / "src" / "styles.scss": PREMIUM_GLOBAL_SCSS,
        base / "src" / "environments" / "environment.ts": """
export const environment = {
  production: false,
  apiUrl: 'https://api.requisitos-suite.local/v1',
  appName: 'Requisitos Suite'
};
""",
        base / "src" / "app" / "app.component.ts": """
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: '<router-outlet />',
  styleUrl: './app.component.scss'
})
export class AppComponent {}
""",
        base / "src" / "app" / "app.component.scss": """
:host {
  display: block;
  min-height: 100vh;
}
""",
        base / "src" / "app" / "app.config.ts": """
import { ApplicationConfig } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';
import { apiInterceptor } from './core/interceptors/api.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    provideHttpClient(withInterceptors([apiInterceptor])),
    provideRouter(routes, withComponentInputBinding())
  ]
};
""",
        base / "src" / "app" / "app.routes.ts": """
import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { ShellComponent } from './layout/shell/shell.component';

export const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', loadComponent: () => import('./pages/dashboard/dashboard.page').then((m) => m.DashboardPage) },
      { path: 'clientes', loadComponent: () => import('./pages/customers/customers.page').then((m) => m.CustomersPage) },
      { path: 'configuracion', loadComponent: () => import('./pages/settings/settings.page').then((m) => m.SettingsPage) }
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
""",
        base / "src" / "app" / "guards" / "auth.guard.ts": """
import { CanActivateFn } from '@angular/router';

export const authGuard: CanActivateFn = () => true;
""",
        base / "src" / "app" / "core" / "interceptors" / "api.interceptor.ts": """
import { HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const apiInterceptor: HttpInterceptorFn = (req, next) => {
  const request = req.clone({
    setHeaders: { 'X-Product': 'Requisitos-Suite' }
  });

  return next(request).pipe(catchError((error) => throwError(() => error)));
};
""",
        base / "src" / "app" / "models" / "requirement.model.ts": MODELS_REQUIREMENT,
        base / "src" / "app" / "models" / "customer.model.ts": MODELS_CUSTOMER,
        base / "src" / "app" / "models" / "kpi.model.ts": MODELS_KPI,
        base / "src" / "app" / "services" / "dashboard.service.ts": DASHBOARD_SERVICE_TS,
        base / "src" / "app" / "services" / "requirements-context.service.ts": requirements_context,
        base / "src" / "app" / "layout" / "shell" / "shell.component.ts": SHELL_COMPONENT_TS,
        base / "src" / "app" / "shared" / "components" / "skeleton" / "skeleton.component.ts": SKELETON_COMPONENT_TS,
        base / "src" / "app" / "shared" / "components" / "toast" / "toast.component.ts": TOAST_COMPONENT_TS,
        base / "src" / "app" / "shared" / "components" / "modal" / "modal.component.ts": MODAL_COMPONENT_TS,
        base / "src" / "app" / "pages" / "dashboard" / "dashboard.page.ts": DASHBOARD_PAGE_TS,
        base / "src" / "app" / "pages" / "dashboard" / "dashboard.page.scss": DASHBOARD_PAGE_SCSS,
        base / "src" / "app" / "pages" / "customers" / "customers.page.ts": CUSTOMERS_PAGE_TS,
        base / "src" / "app" / "pages" / "settings" / "settings.page.ts": SETTINGS_PAGE_TS,
        base / "src" / "app" / "features" / ".gitkeep": "",
        base / "src" / "app" / "components" / ".gitkeep": "",
        base / "src" / "app" / "interceptors" / ".gitkeep": "",
        base / "ARQUITECTURA_PROYECTO.md": ARCHITECTURE_MD,
    }


def build_requirements_context_ts(requerimientos):
    escaped = (requerimientos or "").replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    keywords = extract_requirement_keywords(requerimientos)

    return f"""
import {{ Injectable }} from '@angular/core';

@Injectable({{ providedIn: 'root' }})
export class RequirementsContextService {{
  readonly rawMarkdown = `{escaped}`;
  readonly detectedCapabilities = {keywords};
}}
"""


def extract_requirement_keywords(requerimientos):
    text = (requerimientos or "").lower()
    mapping = {
        "dashboard": ["dashboard", "tablero", "seguimiento", "tracking"],
        "clientes": ["cliente", "clientes", "cuentas"],
        "ventas": ["venta", "ventas", "comercial"],
        "aprobaciones": ["aprobar", "aprobacion", "aprobaciones", "solicitud"],
        "metricas": ["metrica", "metricas", "kpi", "analytics", "grafica"],
        "usuarios": ["usuario", "usuarios", "rol", "roles", "permisos"],
        "notificaciones": ["notificacion", "alerta", "alertas"],
        "busqueda": ["buscar", "busqueda", "filtro", "filtrar"],
        "velocidad": ["rapido", "rapida", "velocidad", "agil"]
    }
    detected = [key for key, values in mapping.items() if any(value in text for value in values)]
    if not detected:
        detected = ["dashboard", "busqueda", "metricas", "usuarios"]

    return "[" + ", ".join(f"'{item}'" for item in detected) + "]"


class Orchestrator:
    def __init__(
        self,
        chat_client,
        chat_model,
        transcribe_client,
        transcribe_model,
        openai_service,
        output_dir="frontend",
    ):
        self.chat_client = chat_client
        self.chat_model = chat_model
        self.transcribe_client = transcribe_client
        self.transcribe_model = transcribe_model
        self.openai_service = openai_service
        self.output_dir = Path(output_dir)

        self.transcriber = TranscriptionAgent() if not MODO_TECNICO else None
        self.cleaner = CleaningAgent(self.openai_service.ask) if not MODO_TECNICO else None
        self.requirements = RequirementsAgent(self.openai_service.ask) if not MODO_TECNICO else None
        self.ui_generator = (
            UIGenerationAgent(self.chat_client, self.chat_model)
            if not MODO_TECNICO
            else None
        )
        self.ui_improver = (
            UIImprovementAgent(self.chat_client, self.chat_model)
            if not MODO_TECNICO
            else None
        )
        self.file_writer = FileWriterAgent()
        self.validator = ValidationAgent(self.openai_service.ask) if not MODO_TECNICO else None

    def run(self, source_path):
        source_path = Path(source_path)
        input_type = self.detect_input_type(source_path)
        project_type = self.detect_project_type(source_path, input_type)

        if MODO_TECNICO:
            return self._run_modo_tecnico(source_path, input_type, project_type)

        base = self._crear_carpeta_salida()
        self.ensure_angular_project(base)

        texto = self._obtener_texto_entrada(source_path, input_type)
        requerimientos = self.requirements.run(texto)
        requirements_path = base / "REQUERIMIENTOS.md"
        requirements_path.write_text(requerimientos.strip() + "\n", encoding="utf-8")
        print("[OK] Requerimientos generados")

        self.ensure_angular_project(base, requerimientos)
        build_log = []
        build_log.append("[OK] Proyecto generado")
        print("[OK] Proyecto generado")

        self.instalar_dependencias(base)
        build_log.append("[OK] Dependencias instaladas")
        print("[OK] Dependencias instaladas")

        (base / "BUILD_LOG.md").write_text("\n".join(build_log) + "\n", encoding="utf-8")
        build_ok = self.build_with_auto_fix(base, build_log)
        (base / "BUILD_LOG.md").write_text("\n".join(build_log) + "\n", encoding="utf-8")
        if not build_ok:
            generar_estructura_proyecto(base)
            raise RuntimeError(f"Build fallido despues de {MAX_BUILD_ATTEMPTS} intentos: {base}")

        generar_estructura_proyecto(base)
        (base / "BUILD_LOG.md").write_text("\n".join(build_log) + "\n", encoding="utf-8")
        self.abrir_carpeta_proyecto(base)

        return ProjectResult(
            transcripcion=texto,
            limpio=texto,
            requerimientos=requerimientos,
            codigo_ui="",
            carpeta_salida=str(base),
        )

    def _run_modo_tecnico(self, source_path, input_type, project_type):
        base = self._crear_carpeta_salida()

        self._log_tecnico(f"[INFO] Agente seleccionado: GeneradorAngularTecnico")
        self._log_tecnico(f"[INFO] Tipo de entrada: {input_type}")
        self._log_tecnico(f"[INFO] Tipo de proyecto: {project_type}")

        self.ensure_angular_project(base)
        generar_estructura_proyecto(base)
        self.instalar_dependencias(base)
        self.abrir_carpeta_proyecto(base)

        self._log_tecnico("[OK] Proyecto generado")
        self._log_tecnico("[OK] Dependencias instaladas")
        self._log_tecnico("[OK] Carpeta abierta:")
        self._log_tecnico(str(base.resolve()).replace("\\", "/"))

        return ProjectResult(
            transcripcion="",
            limpio="",
            requerimientos="",
            codigo_ui="",
            carpeta_salida=str(base),
        )

    def detect_input_type(self, source_path):
        if source_path.is_dir():
            return "directorio"

        suffix = source_path.suffix.lower()

        if suffix in MEDIA_EXTENSIONS:
            return "media"

        if suffix in TRANSCRIPTION_EXTENSIONS:
            return "transcripcion"

        return "texto"

    def detect_project_type(self, source_path, input_type):
        if input_type == "directorio" and self._is_angular_project(source_path):
            return "angular_existente"

        return "angular_nuevo"

    def _crear_carpeta_salida(self):
        output_dir = self.output_dir
        base_dir = output_dir.parent if output_dir.parent != Path("") else Path(".")
        nombre_base = output_dir.name

        return crear_carpeta_proyecto(base_dir, nombre_base)

    def instalar_dependencias(self, base):
        base = Path(base)
        command = "npm install" if os.name == "nt" else ["npm", "install"]

        try:
          subprocess.run(
            command,
            cwd=base,
            check=True,
            shell=os.name == "nt",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
            errors="replace"
          )
        except FileNotFoundError as exc:
            raise RuntimeError("npm no esta disponible en el PATH.") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"npm install fallo en: {base}") from exc

    def build_with_auto_fix(self, base, build_log):
        for attempt in range(1, MAX_BUILD_ATTEMPTS + 1):
            code, output = self.ejecutar_build(base)
            build_log.append(f"## Build intento {attempt}")
            build_log.append(f"Codigo de salida: {code}")

            if output.strip():
                build_log.append("```text")
                build_log.append(output[-8000:])
                build_log.append("```")

            if code == 0:
                build_log.append("[OK] Build exitoso")
                print("[OK] Build exitoso")
                return True

            fixed = self.aplicar_fixes_build(base, output, build_log)
            if not fixed:
                build_log.append("[ERROR] Build sin fix deterministico disponible")

        return False

    def ejecutar_build(self, base):

      if os.name == "nt":
          command = "chcp 65001 > nul && npm run build"
      else:
          command = ["npm", "run", "build"]

      env = os.environ.copy()

      env["PYTHONUTF8"] = "1"
      env["PYTHONIOENCODING"] = "utf-8"

      result = subprocess.run(
          command,
          cwd=base,
          shell=os.name == "nt",
          capture_output=True,
          text=True,
          encoding="utf-8",
          errors="replace",
          env=env
      )

      stdout = result.stdout or ""
      stderr = result.stderr or ""

      output = stdout + "\n" + stderr

      return result.returncode, output

    def aplicar_fixes_build(self, base, output, build_log):
        fixed = False
        missing = self._missing_required_files(base)

        if missing:
            self.ensure_angular_project(base, (base / "REQUERIMIENTOS.md").read_text(encoding="utf-8"))
            build_log.append("[FIX] Archivos faltantes creados")
            print("[FIX] Archivos faltantes creados")
            fixed = True

        if "Cannot find module" in output or "Could not resolve" in output or "TS2307" in output:
            self.ensure_angular_project(base, (base / "REQUERIMIENTOS.md").read_text(encoding="utf-8"))
            build_log.append("[FIX] Ruta Angular corregida")
            print("[FIX] Ruta Angular corregida")
            fixed = True

        if "app.config" in output or "app.routes" in output or "main.ts" in output:
            self.ensure_angular_project(base, (base / "REQUERIMIENTOS.md").read_text(encoding="utf-8"))
            build_log.append("[FIX] Configuracion Angular corregida")
            print("[FIX] Configuracion Angular corregida")
            fixed = True

        if "Cannot find package" in output or "ERESOLVE" in output or "not found" in output.lower():
            self.instalar_dependencias(base)
            build_log.append("[FIX] Dependencia instalada")
            print("[FIX] Dependencia instalada")
            fixed = True

        if "error TS" in output:
            self.ensure_angular_project(base, (base / "REQUERIMIENTOS.md").read_text(encoding="utf-8"))
            build_log.append("[FIX] Error TypeScript corregido")
            print("[FIX] Error TypeScript corregido")
            fixed = True

        return fixed

    def abrir_carpeta_proyecto(self, base):
        base = Path(base).resolve()

        if os.name == "nt":
            try:
                os.startfile(str(base))
            except OSError:
                subprocess.run(
                    ["explorer", str(base)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return

        opener = "open" if os.name == "posix" and os.uname().sysname == "Darwin" else "xdg-open"
        subprocess.run(
            [opener, str(base)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def ensure_angular_project(self, base, requerimientos=""):
        base = Path(base)
        if not MODO_TECNICO:
            print(f"Verificando proyecto Angular en: {base}")

        for directory in [
            base,
            base / "src",
            base / "src" / "app",
        ]:
            os.makedirs(directory, exist_ok=True)

        base_files = premium_angular_files(base, requerimientos)

        for file_path, content in base_files.items():
            if not file_path.exists():
                os.makedirs(file_path.parent, exist_ok=True)
                file_path.write_text(content.strip() + "\n", encoding="utf-8")
                if not MODO_TECNICO:
                    print(f"Archivo base creado: {file_path}")

    def _obtener_texto_entrada(self, source_path, input_type):
        if input_type == "media":
            return self.transcriber.run(
                source_path,
                self.transcribe_client,
                self.transcribe_model,
            )

        if input_type == "transcripcion":
            return source_path.read_text(encoding="utf-8")

        if input_type == "directorio":
            return self._describe_existing_project(source_path)

        return str(source_path)

    def _selected_agent(self, input_type):
        if input_type == "media":
            return "TranscriptionAgent -> CleaningAgent -> RequirementsAgent -> UIGenerationAgent"

        if input_type == "transcripcion":
            return "CleaningAgent -> RequirementsAgent -> UIGenerationAgent"

        if input_type == "directorio":
            return "RequirementsAgent -> UIGenerationAgent"

        return "ninguno"

    def _is_angular_project(self, path):
        return (path / "angular.json").exists() and (path / "package.json").exists()

    def _describe_existing_project(self, path):
        files = [
            str(file.relative_to(path))
            for file in path.rglob("*")
            if file.is_file() and "node_modules" not in file.parts
        ]

        return "Proyecto existente con archivos:\n" + "\n".join(files[:300])

    def _missing_required_files(self, base):
        missing = []

        for relative_path in ANGULAR_REQUIRED_FILES:
            full_path = Path(base) / relative_path
            if not full_path.exists():
                missing.append(relative_path)

        return missing


    def log(self, label, value):
        print(f"[{label}] {value}")

    def log_files(self, label, files):
        print(f"[{label}]")

        if not files:
            print("  - ninguno")
            return

        for file in files:
            print(f"  - {file}")

    def _log_tecnico(self, message):
        if MODO_TECNICO:
            print(message)

