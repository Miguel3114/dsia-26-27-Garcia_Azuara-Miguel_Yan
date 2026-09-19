# Sesión 1 — Entornos virtuales y Git

## 1. Diferencia entre Python global y `.venv`

El Python global es la instalación de Python disponible de forma general en el sistema.

Un entorno virtual `.venv` crea un entorno aislado para un proyecto concreto. Esto evita conflictos entre proyectos que puedan necesitar versiones diferentes de una misma librería.

## 2. ¿Para qué sirve `python -m pip` frente a llamar solo a `pip`?

`python -m pip` ejecuta `pip` utilizando explícitamente el intérprete de Python actual.

Esto ayuda a asegurarnos de que los paquetes se instalan en el entorno correcto, especialmente cuando hay varias instalaciones de Python o varios entornos virtuales.

## 3. Explica working tree / staging / commit

* **Working tree:** son los archivos del proyecto que estamos editando actualmente.
* **Staging:** es la zona donde seleccionamos los cambios que queremos incluir en el siguiente commit.
* **Commit:** es una instantánea de los cambios guardada en el historial de Git.

El flujo habitual es:

`working tree → git add → staging → git commit → commit`

## 4. ¿Clone y pull son lo mismo? ¿Por qué?

No, no son lo mismo.

`git clone` se utiliza para descargar un repositorio completo por primera vez en nuestro ordenador.

`git pull` se utiliza cuando ya tenemos el repositorio clonado y queremos traer los cambios más recientes del repositorio remoto.

## 5. Lista cuatro cosas que no se suben a GitHub y justifica una

Cuatro cosas que no deberían subirse a GitHub son:

* `.venv/`
* `.env`
* Claves API, tokens o contraseñas
* Credenciales o archivos privados

Por ejemplo, `.env` no debe subirse porque puede contener claves API, contraseñas u otra información secreta.

Además, `.venv/` tampoco debe subirse porque es un entorno que se puede regenerar a partir de las dependencias del proyecto.

## 6. Reescribe a buen estilo: `update`, `fix final`, `cambios varios`

* `update` → `Update session documentation`
* `fix final` → `Fix installation instructions`
* `cambios varios` → `Update environment configuration`

Los mensajes de commit deben ser claros y describir de forma concreta qué cambio se ha realizado.

## 7. ¿Qué haces si el IDE no importa `pandas` pero la terminal sí?

Comprobaría qué intérprete de Python está utilizando el IDE.

Si la terminal puede importar `pandas` pero el IDE no, probablemente el IDE esté utilizando un intérprete diferente al del entorno virtual.

En VS Code o Cursor seleccionaría el intérprete de `.venv` mediante:

`Python: Select Interpreter`

y elegiría:

`.venv\Scripts\python.exe`

## 8. ¿Qué haces si subiste `.env` por error?

Lo primero sería revocar o rotar cualquier clave o credencial que estuviera dentro del archivo `.env`.

Después añadiría `.env` al `.gitignore` para evitar que vuelva a subirse.

Si el archivo ya está siendo seguido por Git, dejaría de versionarlo con:

`git rm --cached .env`

y haría un nuevo commit con ese cambio.

Si el secreto llegó a publicarse en el historial, eliminarlo en un commit nuevo no es suficiente, por lo que habría que limpiar el historial si fuera necesario.
