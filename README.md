<div align="center">

# GST Invoice Agent

AI-assisted invoice automation system for GST calculation, PDF generation, payment tracking, analytics, and business workflows.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red)](https://streamlit.io)
[![React](https://img.shields.io/badge/React-UI-blue)](https://react.dev/)

</div>

## Overview

GST Invoice Agent is a full invoice-management system for Indian business workflows. It combines a FastAPI backend, Streamlit dashboard, React/Vite UI pieces, and a collection of business agents for invoice creation, GST calculation, exports, reminders, audits, and backups.

## Features

| Area | Capabilities |
|---|---|
| Invoices | Create invoices, calculate GST, generate PDF files |
| Customers | Store and search customer information |
| Payments | Track payment state and reminders |
| Analytics | Reports, summaries, and business insights |
| Exports | Excel and PDF export support |
| Agents | Invoice, audit, analytics, email, backup, search, notification, and recurring agents |
| Security | Auth, validation, audit trail, and testing support |

## Tech Stack

- FastAPI
- Streamlit
- React + Vite
- SQLite / database models
- PDF and Excel generation
- pytest
- Netlify / Render deployment files

## Run Locally

```bash
git clone https://github.com/BUNNY-RANGU/gst-invoice-agent.git
cd gst-invoice-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run API:

```bash
python main.py
```

Run dashboard:

```bash
streamlit run streamlit_app.py
```

Open:

```text
API docs: http://localhost:8000/docs
Dashboard: http://localhost:8501
```

## Testing

```bash
pytest
```

## Deployment

Deployment helpers are included for Render, Netlify, and Procfile-based hosting. Use environment variables from `.env.example` when deploying.

## Author

Built by [Rangu Suchandra](https://github.com/BUNNY-RANGU).
