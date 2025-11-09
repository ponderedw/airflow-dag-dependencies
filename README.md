# Airflow DAG Dependencies

An Apache Airflow 3 plugin that restores and enhances the DAG Dependencies visualization that was removed in Airflow 3.1.1.

## Overview

This plugin provides an interactive visualization of DAG dependencies, datasets, and trigger relationships using D3.js. It not only restores the missing functionality from Airflow 2 but adds enhanced filtering capabilities for better workflow understanding.

## Features

- **Interactive Graph Visualization**: See all DAG relationships at a glance
- **Dataset Dependencies**: Visualize dataset-triggered DAGs with green connections
- **DAG Triggers**: Identify DAG-to-DAG triggers with yellow connections  
- **Schedule Types**: Distinguish between scheduled (tan), dataset-triggered (green), and manual (pink) DAGs
- **Advanced Filtering**: Powerful search syntax for exploring complex dependency chains
- **Real-time Data**: Uses DagBag to fetch live DAG information

## Quick Start

### Installation

```bash
pip install airflow-dag-dependencies
```

### Docker Demo

```bash
git clone https://github.com/ponderedw/airflow-dag-dependencies
cd airflow-dag-dependencies
docker compose up
```

Visit `http://localhost:8080` (username: `airflow`, password: `airflow`) and navigate to Browse → DAG Dependencies.

## Search Syntax

- `dag_name` - Find DAGs containing the term
- `+dag_name` - Show DAG and all upstream dependencies
- `dag_name+` - Show DAG and all downstream dependencies  
- `+dag_name+` - Show DAG and all connected dependencies
- `2+dag_name` - Show DAG and 2 levels upstream
- `dag_name+3` - Show DAG and 3 levels downstream
- `1+dag_name+2` - Show DAG with 1 upstream and 2 downstream levels
- `@exact_name` - Exact match only

## Airflow 3 Plugin Development

This plugin demonstrates key differences in Airflow 3 plugin architecture:

### Airflow 2 vs 3 Comparison

**Airflow 2:**
```python
class MyPlugin(AirflowPlugin):
    flask_blueprints = [my_blueprint]
    admin_views = [MyAdminView] 
    menu_links = [my_menu_link]
```

**Airflow 3:**
```python
class MyPlugin(AirflowPlugin):
    fastapi_apps = [my_fastapi_app]
    external_views = [my_external_view]
```

### Key Changes
- **FastAPI** replaces Flask for better performance and async support
- **External Views** replace Flask-Admin views for flexible UI integration
- **Simplified** menu integration through external view definitions

## Technical Architecture

### Package Structure
```
airflow_dag_dependencies/
├── __init__.py
└── plugins/
    ├── __init__.py
    └── dags_dependencies_plugin.py
```

### FastAPI Integration
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def dag_dependencies_graph():
    return html_content

@app.get("/api/dag-dependencies") 
async def get_dag_dependencies():
    return {"nodes": nodes, "links": links}
```

### Plugin Registration
```python
class DagDependenciesPlugin(AirflowPlugin):
    name = "dags_dependencies_plugin"
    fastapi_apps = [{
        "app": app,
        "url_prefix": "/dags_dependencies", 
        "name": "DAG Dependencies App"
    }]
    external_views = [{
        "name": "DAG Dependencies",
        "href": "/dags_dependencies/",
        "destination": "nav",
        "category": "browse"
    }]
```

## Requirements

- Python ≥3.12, <3.14
- Apache Airflow ≥3.1.0

## Contributing

We welcome contributions! This plugin serves as both a useful tool and a reference implementation for Airflow 3 plugin development.

## What's Next

Future tutorials will cover:
- Building React components for Airflow 3
- Advanced authentication and permissions
- Modern frontend integration patterns

---

**Made by [Ponder](https://ponder.co/) • [Blog Post](https://ponder.co/airflow-3-plugin-dag-dependencies/) • [GitHub](https://github.com/ponderedw/airflow-dag-dependencies)**