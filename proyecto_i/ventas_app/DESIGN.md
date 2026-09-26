# Diseño

- **SRP (Single Responsibility Principle)** — `validator.py` solamente
  contiene la lógica encargada de comprobar si los datos son válidos.
  No carga ni guarda ficheros.

- **OCP (Open/Closed Principle)** — `metrics.py` permite añadir nuevas
  métricas sin modificar la lógica de carga o validación.

- **DIP (Dependency Inversion Principle)** — `cli.py` trabaja con el
  protocolo `SalesRepository` en lugar de depender directamente de la
  lectura de CSV. La implementación concreta `CsvSalesRepository` puede
  sustituirse por otra, como `JsonSalesRepository`, sin modificar la
  lógica de validación ni las métricas.