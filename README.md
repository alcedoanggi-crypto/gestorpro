# GestorPro — Sistema de Gestión de Proyectos

Aplicación web MVC construida con **Flask + SQLAlchemy + PostgreSQL**, con dashboard
dinámico, diagrama de Gantt interactivo, reportes con gráficos, exportación a PDF/Excel,
notificaciones y control de acceso por roles.

## Arquitectura (MVC)

```
gestorpro/
├── wsgi.py                  # punto de entrada
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py          # application factory (wiring)
│   ├── config.py            # configuración por entorno
│   ├── extensions.py        # instancias de db, login, csrf, mail, migrate
│   ├── seeds.py             # datos de demostración (flask seed)
│   │
│   ├── models/              # ── M ── capa de datos (SQLAlchemy)
│   │   ├── enums.py         # estados y prioridades de dominio
│   │   ├── role.py          # roles: admin / gerente / colaborador
│   │   ├── user.py          # usuarios + hash de contraseña + token de reseteo
│   │   ├── team.py          # equipos (N:M con usuarios)
│   │   ├── project.py       # proyectos + métricas derivadas
│   │   ├── task.py          # tareas + dependencias (Gantt) + comentarios
│   │   ├── comment.py
│   │   └── notification.py
│   │
│   ├── controllers/         # ── C ── blueprints (rutas / lógica de request)
│   │   ├── auth.py          # login, registro, logout, recuperación
│   │   ├── dashboard.py
│   │   ├── projects.py      # CRUD + vista de cronograma
│   │   ├── tasks.py         # CRUD + cambio de estado + comentarios
│   │   ├── users.py         # CRUD de usuarios + perfil
│   │   ├── teams.py         # CRUD de equipos
│   │   ├── reports.py       # gráficos + exportación PDF/Excel
│   │   └── api.py           # JSON: Gantt drag&drop, notificaciones
│   │
│   ├── services/            # lógica de negocio reutilizable
│   │   ├── report_service.py       # agregaciones para Chart.js
│   │   ├── export_service.py       # openpyxl + reportlab
│   │   ├── notification_service.py  # generación / scanner de vencimientos
│   │   └── mail_service.py
│   │
│   ├── forms/               # validación (Flask-WTF)
│   ├── utils/               # decoradores de rol, permisos de objeto, scoping
│   │
│   ├── templates/           # ── V ── vistas (Jinja2 + Bootstrap 5)
│   │   ├── base.html        # layout, tema claro/oscuro, sidebar por rol
│   │   ├── partials/        # sidebar, topbar, flash, macros
│   │   ├── auth/  dashboard/  projects/  tasks/  users/  teams/  reports/  errors/
│   │
│   └── static/
│       ├── css/style.css    # diseño minimalista + modo oscuro (CSS vars)
│       └── js/  app.js · dashboard.js · gantt.js · reports.js
└── tests/                   # pytest (SQLite en memoria)
```

### Roles y permisos

| Rol         | Alcance |
|-------------|---------|
| **admin**       | Todo: usuarios, equipos, todos los proyectos y reportes |
| **gerente**     | Sus proyectos, sus equipos, tareas y reportes |
| **colaborador** | Solo las tareas que tiene asignadas y los proyectos donde participa |

El **sidebar se genera dinámicamente** según el rol. El primer usuario registrado
se convierte en `admin` automáticamente.

## Puesta en marcha

### 1. Requisitos
- Python 3.10+
- PostgreSQL 13+ (o SQLite para pruebas)

### 2. Instalación

```bash
cd gestorpro
python -m venv .venv
# Windows:  .venv\Scripts\activate     Linux/Mac:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # y edita DATABASE_URL, SECRET_KEY, SMTP...
# El driver es psycopg 3 -> la URL usa el prefijo postgresql+psycopg://
```

### 3. Base de datos PostgreSQL

```sql
CREATE DATABASE gestorpro;
```

```bash
# Opción A — rápida (crea tablas + roles)
flask init-db

# Opción B — con migraciones versionadas
flask db init
flask db migrate -m "esquema inicial"
flask db upgrade
```

### 4. Datos de demostración (opcional)

```bash
flask seed
```

Usuarios de prueba (contraseña `Demo1234`):

| Correo             | Rol         |
|--------------------|-------------|
| admin@demo.com     | admin       |
| gerente@demo.com   | gerente     |
| diego@demo.com     | colaborador |

### 5. Ejecutar

```bash
flask run           # http://localhost:5000
# producción:  gunicorn wsgi:app
```

## Funcionalidades

- **Autenticación**: hash `pbkdf2:sha256` (Werkzeug), sesiones con Flask-Login,
  protección CSRF, recuperación de contraseña por token con expiración (1 h),
  respuesta anti-enumeración de usuarios.
- **Dashboard**: tarjetas resumen (proyectos activos, tareas pendientes, por vencer,
  retrasadas), gráfico de línea de completadas por mes y doughnut de estados,
  lista de tareas propias y proyectos recientes.
- **Gantt interactivo** (Frappe Gantt): cronograma por proyecto con dependencias,
  cambio de vista Día/Semana/Mes y **arrastrar-y-soltar de fechas** persistido vía
  `POST /api/tasks/<id>/schedule`.
- **Reportes** (Chart.js): progreso por proyecto, carga de trabajo por usuario,
  distribución de estados/prioridades, cumplimiento de plazos y serie mensual.
- **Exportación**: Excel (`openpyxl`, hojas de proyectos y tareas) y PDF
  (`reportlab`, resumen + detalle).
- **CRUD completo** de proyectos, tareas, usuarios y equipos con validación.
- **Notificaciones**: al asignar tareas, al comentar y un scanner de vencimientos
  (`flask scan-notifications`) pensado para un cron:

  ```
  */30 * * * *  cd /ruta/gestorpro && .venv/bin/flask scan-notifications
  ```

## UI/UX

- Bootstrap 5.3 + Font Awesome 6, tipografía Inter.
- **Modo claro/oscuro** con `data-bs-theme` y variables CSS, preferencia en `localStorage`.
- Layout responsive con sidebar colapsable en móvil.

## Tests

```bash
pytest
```

Usan SQLite en memoria (`TESTING`), sin necesidad de PostgreSQL.
