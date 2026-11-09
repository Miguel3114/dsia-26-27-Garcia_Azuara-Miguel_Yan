# DSIA 2026-2027 — Miguel García

Repositorio de la asignatura **Desarrollo de Soluciones de IA**.

**Entorno:** Python 3.12.

## Proyectos

### Proyecto I — Programación avanzada en Python

- **Parte A:** carga y validación de datos de ventas.
- **Parte B:** carga, validación y métricas de demanda de viajeros EMT Madrid.

[Documentación del Proyecto I](proyecto_i/README.md)

### Proyecto II — Automatización e integración de servicios

Pipeline de datos EMT Madrid, control de calidad, entrenamiento de `RandomForestRegressor`, predicción de demanda por línea, fecha y franja, cliente de IA `mock`/Hugging Face, tests y automatización mediante Bash.

- [Documentación y comandos del Proyecto II](proyecto_ii/README.md)
- [Declaración de uso de IA del Proyecto II](proyecto_ii/AI_USAGE.md)

## Pruebas

Desde la raíz y con las dependencias instaladas:

```bash
python -m pytest -q -c pytest.ini
```

El workflow [GitHub Actions](.github/workflows/ci.yml) ejecuta los tests de ambos proyectos.
