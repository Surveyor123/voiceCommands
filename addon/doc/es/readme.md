# Comandos de Voz para NVDA

Ejecuta los comandos de NVDA hablando en lugar de presionar teclas.

NVDA ya tiene una descripción para cada comando en su cuadro de diálogo Gestos de Entrada. Comandos de Voz escucha a través de tu micrófono, convierte tu voz en texto con el motor sin conexión [Vosk](https://alphacephei.com/vosk/) engine, compara ese texto con esas descripciones (y con las frases que tú mismo definas), y ejecuta el comando que mejor se adapte. Tu voz se procesa en tu ordenador y nunca sale de él.

## Cómo funciona

1.  Cuando empiezas a escuchar, el complemento recopila los comandos que están disponibles en ese momento. Esto incluye los comandos de la aplicación en la que estás trabajando, por lo que un comando de otra aplicación solo se ofrecerá mientras esa aplicación tenga el foco.
2.  Hablas y luego detienes la escucha. Vosk convierte tu voz en texto.
3.  El texto se compara con las descripciones de los comandos y con tus propias frases. También se le indica al reconocedor qué frases esperar, lo que lo hace mucho más preciso que el dictado libre.
4.  Si un comando se adapta claramente, se ejecuta. Si varios se adaptan de forma similar, se abre una lista y tú eliges.

## Requisitos

- NVDA 2026.1 o posterior, de 64 bits, en Windows.
- Un micrófono configurado como dispositivo de grabación predeterminado en Windows.
- Conexión a Internet por una única vez para descargar el modelo de voz (un modelo pequeño ocupa entre 40 y 100 MB).

## Instalación y primera ejecución

1.  Abre el archivo `.nvda-addon` y confirma la instalación. Reinicia NVDA cuando se te solicite.
2.  Unos segundos después de que se inicie NVDA, el complemento notará que no hay ningún modelo de voz instalado y te preguntará si puede descargar uno para tu idioma de NVDA. Elige **Sí**. La descarga se realiza en segundo plano; NVDA anunciará el progreso y te avisará cuando los comandos de voz estén listos.

Si eliges **No**, el complemento no volverá a preguntar al iniciar. Se te preguntará de nuevo cuando empieces a escuchar o cuando uses el comando "Descarga el modelo de reconocimiento de voz".

## Inicio rápido

No hay teclas asignadas por defecto, así que elige las tuyas:

1.  Abre el menú de NVDA, luego Preferencias y después Gestos de entrada.
2.  Expande la categoría **Comandos de Voz** y asigna una tecla a **Inicia la escucha de comandos de voz**. Asigna teclas a los demás comandos que desees allí también.

Sin teclas también puede usar el menú Herramientas (ver El menú Herramientas).

Luego, para dar un comando de voz:

1.  Presiona tu tecla. Un pitido agudo te indicará que se ha empezado a escuchar.
2.  Di el comando.
3.  Presiona la tecla de nuevo. Un pitido grave te indicará que se ha detenido la escucha y el comando se ejecutará.

Si no se reconoce nada, NVDA dirá  "No se entendió". Si lo que escuchó no se ajusta lo suficientemente bien a ningún comando, NVDA dirá "No hay ningún comando coincidente" y nombra el más cercano, o abre una lista de candidatos (ver Cuando no está seguro).

## El menú Herramientas

Abre el menú de NVDA, luego Herramientas, y después **Comandos de Voz** para usar el complemento sin asignar teclas:

- **Iniciar o detener la escucha** funciona como una tecla: elegirlo una vez para iniciar y de nuevo para detener. Una tecla es más rápida, porque el menú tiene que abrirse cada vez.
- **Editor de frases de comando...** abre el editor de frases.
- **Enseñar la última frase hablada...** abre el cuadro de diálogo para los nombres que el reconocedor no conoce.
- **Mis comandos...** abre el cuadro de diálogo para tus propios comandos.
- **Alterna la atenuación del volumen** activa o desactiva la atenuación del volumen de otras aplicaciones.
- **Descargar modelo de voz...** inicia la descarga del modelo, tras preguntar.
- **Abrir la carpeta del modelo** abre la carpeta del modelo en el Explorador de archivos.
- **Introduce un comando...** abre un cuadro de diálogo donde puedes escribir una frase de comando.

Estos comandos hacen lo mismo que los comandos del cuadro de diálogo Gestos de Entrada (ver Referencia de comandos).

## Elegir qué decir

Las descripciones de NVDA suelen ser frases completas, por ejemplo "Informa de la línea actual bajo el cursor de la aplicación. Pulsando esta tecla dos veces rápidamente deletreará la línea actual." No tienes que decirlo todo.

| Lo que dices                                                                                           | Qué esperar                                                                     |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| La primera frase de la descripción, como "Informa de la línea actual bajo el cursor de la aplicación" | Normalmente funciona bien. Para muchos comandos, la primera frase es toda la descripción. |
| Una frase corta que hayas definido en el [editor de frases](#your-own-phrases), como "leer línea"              | Preciso y lo más confiable. **Recomendado para los comandos que usas todos los días.**   |
| Una paráfrasis corta propia que no esté definida en ningún sitio, como "lee la línea actual"           | Menos confiable. Puede abrir la lista o coincidir con un comando similar.           |

Dos cosas ayudan en la práctica. Di la frase a un ritmo constante, en un momento de silencio, y no omitas las palabras distintivas. Además, define frases cortas para los comandos que más uses: toma un minuto y hace que todo sea más rápido.

## Tus propias frases

Usa el editor de frases para decir los comandos a tu manera. Asigna una tecla a **Abre el cuadro de diálogo para editar las frases (alias) utilizadas para los comandos** y ábrelo desde la aplicación cuyos comandos quieras editar.

1.  En **Buscar comandos**, escribe unas pocas palabras para filtrar la  lista, luego selecciona el comando  en **Comandos**.
2.  Escribe tu frase en **Nueva frase** y elige **Añadir frase**. Puedes añadir varias frases a un mismo comando. Para cambiar o eliminar una, selecciónala en **Frases que dices para este comando** y elige **Editar frase seleccionada** o **Eliminar frase seleccionada**.
3.  Desmarca **Usar también la descripción original** si el comando solo debe responder a tus frases.
4.  Elige **Guardar**.

Las buenas frases son cortas, de dos a cuatro palabras, y suenan diferentes entre sí. Tus frases tienen prioridad sobre las descripciones originales, y funcionan con la función de repetición y la lista de candidatos como cualquier otro comando. El editor muestra los comandos que están disponibles desde donde lo abriste, así que ábrelo dentro de una aplicación para editar los comandos de esa aplicación.

## Nombres que el reconocedor no conoce

El modelo de voz tiene un vocabulario fijo y no puede aprender palabras nuevas. Por lo tanto, un comando que contenga un nombre raro o extranjero, como el de un artista o el título de una canción, a menudo se escuchará como otras palabras que suenan similar. Por ejemplo, "Zülfü Livaneli" puede escribirse como "gül suyu divane izi". El complemento intenta corresponder dicho texto por sonido, lo que funciona cuando el modelo escribe algo cercano al nombre ("inti ilimani" para "Inti Illimani"), pero no cuando escribe palabras completamente diferentes.

Cuando no se reconozca un comando, enseña al complemento lo que escuchó el reconocedor:

1.  Di el comando que falló.
2.  Abre el menú Herramientas, luego Comandos de Voz y después **Enseñar la última frase hablada**. También puedes asignar una tecla a **Abre un cuadro de diálogo que añade lo último que escuchó el reconocedor como frase hablada de un comando que elijas** en el cuadro de diálogo Gestos de Entrada.
3.  La lista de la parte superior muestra los textos que produjo el reconocedor, todos marcados. Desmarca los que parezcan incorrectos.
4.  En **Buscar comandos**, encuentra el comando, selecciónalo en la lista de abajo y elige **Guardar frases**.

Los textos marcados se guardan como frases de ese comando, exactamente como si los hubieras escrito en el editor de frases, y podrás editarlos o eliminarlos allí más tarde. Al tratarse de palabras que el modelo ya conoce, la misma pronunciación se encontrará directamente la próxima vez. La lista siempre muestra lo que el reconocedor escuchó la última vez que dijiste un comando, se haya reconocido o no, así que abre el cuadro de diálogo justo después del comando que falló. También es una forma rápida de ver qué hizo el reconocedor con tu voz, sin necesidad de mirar el registro  de NVDA. No se incluyen los comandos que escribas en el cuadro de diálogo de comandos.

## Compartir y respaldar tus frases

El editor de frases puede guardar tus frases en un archivo y cargarlas de nuevo, de modo que puedes hacer una copia de seguridad, moverlas a otro ordenador o compartirlas con otras personas.

- **Exportar frases...** (Ctrl+E) guarda las frases que están en el editor, junto con los comandos cuya descripción original desactivaste, en un archivo `.json`. Se omiten los comandos sin frases.
- **Importar frases...** (Ctrl+I) lee dicho archivo y añade sus frases al editor. No se elimina ni cambia nada de lo que ya tienes: se saltan las frases que ya tienes, y para un comando del que ya tienes configuración, se mantiene tu elección de **Usar también la descripción original**. NVDA te indicará cuántos cambios se han importado. Nada se almacena hasta que elijas **Guardar** (Ctrl+S), por lo que primero puedes revisar el resultado y elegir Cancelar para descartarlo.

En el editor de frases, estos atajos funcionan dondequiera que esté el foco.

El archivo tiene el mismo formato que `aliases.json` en la carpeta de configuración de Comandos de Voz (ver Configuración y datos), por lo que también se puede importar una copia de ese archivo. Las frases están vinculadas a los comandos mediante un ID que no depende del idioma de la interfaz, así, un archivo creado por el editor funciona con cualquier idioma de NVDA. Un archivo también puede nombrar un comando por su texto en lugar de su ID, escrito tal como aparece en la lista del editor: `description - category`, por ejemplo `Show desktop - Windows commands`. Dicha entrada solo coincide cuando NVDA utiliza el idioma de ese texto. Una frase para un comando que no existe en tu ordenador, como el comando de una aplicación que no tienes instalada, se conserva pero no hace nada hasta que ese comando exista. El editor solo enumera los comandos disponibles donde lo abriste, así que ábrelo dentro de una aplicación para ver las frases importadas de los comandos de esa aplicación. Tus propios comandos (ver Tus propios comandos) obtienen un ID diferente en cada ordenador, por lo que las frases para ellos no se transfieren; añade las mismas frases a los comandos en otro ordenador en su lugar.

**Un conjunto turco todo listo.** El complemento viene con el `tr-phrases.json` en su carpeta `locale\tr\LC_MESSAGES`: se trata de frases cortas en turco (de dos o tres palabras) para los propios comandos de NVDA y para muchos complementos populares. Impórtalo como cualquier otro archivo. Nombra los comandos según su texto (ver más arriba), por lo que funciona con un NVDA en turco. Para un comando del que no tengas ninguna configuración, también desactiva la descripción larga original, de modo que dicho comando solo responda a la frase corta; vuelve a activar **Usar también la descripción original** en el editor si deseas ambas.

## Excluir comandos del control por voz

Hay algunos comandos que nunca querrás ejecutar por voz, por ejemplo porque son riesgosos ("cerrar ventana", "bloquear el equipo") o porque suenan demasiado parecidos a otros y se seleccionan por error. Para excluir uno:

1.  Abre el editor de frases y selecciona el comando, como se describe en Tus propias frases.
2.  Desmarca  **Usar también la descripción original** y no añadas ninguna frase propia.
3.  Elige **Guardar**.

El comando dejará de formar parte de lo que el complemento escucha, por lo que nunca se ejecutará, nunca se ofrecerá en la lista de candidatos y no se buscará por sonido. Seguirá funcionando con su propia tecla desde el cuadro de diálogo Gestos de Entrada. Esto funciona para los comandos de NVDA, los comandos integrados de Windows y tus propios comandos. Para volver a activar un comando, selecciónalo de nuevo y activa  **Usar también la descripción original**, o añade una frase. Un comando propio también se puede eliminar simplemente en su cuadro de diálogo.

Excluir un comando también hace que el reconocimiento sea más confiable: cuantos menos comandos haya para elegir, menos a menudo se confundirá uno similar con el que dijiste.

## Repetir un comando

Termina la frase con un número y la palabra "veces": "leer línea dos veces", "siguiente línea tres veces". El número puede ser del dos al cinco, y también funcionan los dígitos ("3 veces"). El comando se ejecuta esa cantidad de veces seguidas.

Para los comandos que reaccionan al ser presionados varias veces, NVDA cuenta esto como pulsaciones de teclas repetidas. Por ejemplo, el comando que informa de la línea actual la lee una vez, la deletrea dos veces y da descripciones de caracteres tres veces. Para otros comandos, como moverse a la siguiente línea, el efecto es simplemente que ocurre varias veces.

## Pulsar teclas con la voz

Los comandos de la categoría de Gestos de Entrada **Teclas de sistema del teclado emuladas** presionan una tecla del teclado del sistema por ti, como una tecla de flecha, Tab o Escape. Funcionan como cualquier otro comando, y la repetición es especialmente útil aquí: "flecha abajo tres veces" pulsar la tecla tres veces. Di el nombre de la tecla tal como aparece en el cuadro de diálogo Gestos de Entrada. NVDA trata la pulsación de la forma en que trata a sus propias teclas emuladas: deja que sus propios comandos manejen la tecla primero y, de lo contrario, la envía al sistema.

## Comandos integrados de Windows

El cuadro de diálogo Gestos de Entrada de NVDA solo enumera los comandos propios de NVDA, por lo que el complemento aporta un conjunto propio de comandos de Windows para todo el sistema. Los dices como cualquier otro comando, por ejemplo "mostrar el escritorio", "mostrar la barra de tareas", "mostrar la bandeja del sistema", "copiar" o "pegar". Cada uno simplemente presiona el atajo que Windows ya usa para ello, por lo que funciona en cualquier aplicación. Los atajos que terminan en una letra (como Windows+I) se presionan mediante el código de tecla virtual de la tecla en lugar de por el carácter, por lo que funcionan con cualquier distribución de teclado, incluyendo el turco.

- **Escritorio y shell:** mostrar el escritorio, mostrar la barra de tareas, mostrar la bandeja del sistema, abrir el menú Inicio, abrir el Explorador de archivos, abrir el cuadro de diálogo Ejecutar, abrir la Configuración de Windows, abrir la búsqueda de Windows, abrir la configuración rápida, abrir el centro de notificaciones, abrir el historial del portapapeles, abrir el panel de emojis, iniciar la escritura por voz de Windows, abrir el menú de proyección de pantalla, hacer una captura de pantalla, abrir el Administrador de tareas, bloquear el equipo.
- **Ventanas y escritorios virtuales:** minimizar todas las ventanas, restaurar las ventanas minimizadas, mostrar la vista de tareas, cambiar a la ventana anterior, cerrar ventana, maximizar ventana, minimizar ventana, acoplar ventana a la izquierda o derecha, escritorio virtual siguiente, anterior, nuvo y cerrar escritorio virtual.
- **Sonido y multimedia:** subir el volumen, bajar el volumen, silenciar o activar el sonido, reproducir o pausar el contenido multimedia, pista siguiente, pista anterior.
- **Edición:** copiar, cortar, pegar, seleccionar todo, deshacer, rehacer, guardar, buscar, imprimir, crear nuevo, abrir archivo, cambiar nombre, propiedades, actualizar.
- **Navegación y pestañas:** ir atrás, ir adelante, nueva pestaña, cerrar pestaña, reabrir pestaña cerrada, pestaña siguiente, pestaña anterior.

Los comandos donde repetir tiene sentido aceptan  "dos veces", etc., por ejemplo "subir el volumen tres veces" o "pestaña siguiente dos veces". Estos comandos aparecen en el editor de frases de comando bajo la categoría **Comandos de Windows**, por lo que puedes añadir tus propias frases para ellos o desactivar su frase original. Un comando de NVDA con la misma descripción tiene prioridad. Las descripciones son traducibles, por lo que las frases que dices están en tu idioma.

## Tus propios comandos

Puedes añadir comandos propios. Asigna una tecla a **Abre el cuadro de diálogo para añadir tus propios comandos** en la categoría Comandos de Voz del cuadro de diálogo Gestos de Entrada, presiónala y elige **Añadir**. Escribe lo que vas a decir y luego elige  lo que hace el comando:

- **Abrir un programa, archivo, carpeta o dirección web:** escríbelo o usa los botones para examinar. Se abrirá como si hubieras hecho doble clic en él, por lo que una dirección web se abre en tu navegador. Las variables de entorno como `%USERPROFILE%` funcionan, al igual que los nombres de las carpetas `music`, `documents`, `downloads`, `desktop`, `pictures` y `videos`, y las direcciones `shell:` de Windows. Un programa que esté en la ruta del sistema, como `notepad`, no necesita carpeta.
- **Presione una combinación de teclas:** escribe las teclas con los nombres de tecla de NVDA, por ejemplo `control+shift+n`. Las abreviaturas comunes como `ctrl`, `win`, `esc` y `left` se entienden. Los comandos de teclas se pueden repetir ("dos veces").

Tus comandos se enumeran en el editor de frases bajo  **Mis comandos**, donde puedes añadirles frases adicionales. Si un comando tuyo tiene el mismo nombre que un comando de NVDA, se usará el tuyo. Nada aquí ejecuta scripts o comandos de shell: un comando transmite su objetivo a Windows o presiona teclas. Tus comandos se guardan en `userCommands.json` en la carpeta de configuración de Comandos de Voz (ver Configuración y datos).

## Cuando no está seguro

Cuando varios comandos se adaptan de forma similar, o ninguno se adapta lo suficientemente bien como para ejecutarse por sí solo, se abre una lista con los mejores candidatos. Usa las teclas de flecha y presiona Intro para ejecutar el que deseas, o presiona Escape para cancelar. Si elegiste una repetición, esta se aplica al comando que elijas.

## Escribir en lugar de hablar

Asigna una tecla a **Abre un cuadro de diálogo donde puedes escribir una frase de comando**. Lo que escribas pasa por el mismo proceso de coincidencia que el habla, lo que resulta útil para probar frases y para situaciones en las que no puedes hablar.

## Referencia de comandos

Todos estos comandos se encuentran en el cuadro de diálogo Gestos de Entrada, en la categoría Comandos de Voz.

| Comando                                                                                                                | Qué hace                                             |
|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| Inicia la escucha de comandos de voz; presiona de nuevo para detenerla y ejecutar el comando                                | El comando principal. Presiona una vez para iniciar y de nuevo para detener. |
| Abre un cuadro de diálogo donde puedes escribir una frase de comando                                                                        | Ejecuta una frase escrita a través del mismo proceso de coincidencia.           |
| Abre el cuadro de diálogo para editar las frases (alias) utilizadas para los comandos                                                   | Abre el editor de frases.                                 |
| Alterna la atenuación del volumen de otras aplicaciones mientras se escucha un comando de voz                                  | Atenuación del volumen activada o desactivada.                         |
| Descarga el modelo de reconocimiento de voz para el idioma de NVDA                                                           | Inicia la descarga del modelo, tras preguntar.                 |
| Abre un cuadro de diálogo que añade lo último que escuchó el reconocedor como frase hablada de un comando que elijas                     | Enseña al complemento un nombre que no reconoce.         |
| Abre el cuadro de diálogo para añadir tus propios comandos: abrir un programa, archivo, carpeta o dirección web, o presionar una combinación de teclas | Abre el cuadro de diálogo para tus propios comandos.                  |
| Abre la carpeta del modelo en el Explorador de archivos                                                                                | Para instalar un modelo manualmente.                          |

## Atenuación del volumen de otras aplicaciones

La música y los videos serían captados por el micrófono y perturbarían al reconocedor. Mientras estás escuchando, el volumen de todas las sesiones de audio, excepto la de NVDA, se atenúa al 20% de su volumen, y se restablece cuando   lo detienes. Las sesiones cuyo volumen cambies tú mismo en ese intervalo no se modifican.

Windows recuerda los volúmenes por aplicación, por lo que el complemento también guarda un pequeño archivo de recuperación. Si NVDA se cierra mientras el volumen está atenuado, los volúmenes originales se restauran la próxima vez que se inicie NVDA.

Esta función utiliza una biblioteca que viene con NVDA. Si no está disponible, la escucha seguirá funcionando, solo que sin atenuar el volumen de nada. Puedes desactivarlo con el comando de alternancia.

## El modelo de voz

- El complemento busca el modelo en la carpeta `voiceCommands\model` dentro de la carpeta de configuración de  NVDA, por ejemplo `%AppData%\nvda\voiceCommands\model`. El comando "Abre la carpeta del modelo en el Explorador de archivos" te lleva allí.
- La descarga automática utiliza la lista oficial de modelos en <https://alphacephei.com/vosk/models>. Elige un modelo pequeño para tu idioma de NVDA, verifica su suma de comprobación y lo extrae en esa carpeta.
- Para instalar un modelo tú mismo, descarga uno de esa página y extráelo en la carpeta model. Se reconocen ambos diseños de modelo de Vosk, y los archivos pueden estar en una subcarpeta.
- Los modelos grandes son más precisos pero necesitan mucha más memoria y tardan más en cargarse.
- Si no hay un modelo listo para tu idioma, el complemento ofrece abrir la página de modelos.

## Configuración y datos

Se guardan en `%AppData%\nvda\voiceCommands`, o en la carpeta de configuración de un NVDA portátil:

| Elemento                    | Contenido                                                                                         |
|-------------------------|--------------------------------------------------------------------------------------------------|
| `aliases.json`          | Tus frases del editor de frases y del cuadro de diálogo enseñar.                                        |
| `userCommands.json`     | Tus propios comandos.                                                                               |
| `settings.json`         | Si la atenuación de volumen está activada y si se debe preguntar sobre la descarga al iniciar.                 |
| `ducking-recovery.json` | Temporal: existe solo mientras el volumen de otras aplicaciones está atenuado, para restaurarlo después de un cuelgue. |
| `model\`                | El modelo de voz.                                                                                |

Los valores de la parte superior de `globalPlugins/voiceCommands/__init__.py`, como los umbrales de coincidencia y el tamaño de la lista de candidatos, se pueden editar si deseas ajustar el comportamiento.

## Solución de problemas

| Problema                                   | Qué comprobar                                                                                                                                                             |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "No se encontró el modelo de Vosk"                    | Instala un modelo como se describió anteriormente. El mensaje indica la carpeta exacta.                                                                                                   |
| No se reconoce nada                     | Asegúrate de que el micrófono correcto sea el predeterminado de Windows y no esté silenciado.                                                                                                      |
| Un nombre nunca se reconoce                | El modelo puede escribirlo como otras palabras. Abre **Enseñar la última frase hablada** justo después de decirlo para ver qué se escuchó y guárdalo como una frase (ver Nombres que el reconocedor no conoce). |
| Se ejecuta el comando incorrecto                    | Define una frase corta propia para ese comando en el editor de frases.                                                                                                  |
| "Este comando no está disponible en este momento" | El comando pertenece a otra aplicación. Dilo mientras esa aplicación tenga el foco.                                                                                      |
| La música o el video siguen interfiriendo       | Algunas aplicaciones no exponen una sesión de audio que se pueda atenuar. Paúsalas antes de escuchar.                                                                        |
| Quieres ver qué se escuchó            | Abre **Enseñar la última frase hablada** justo después de hablar: su lista muestra los textos que produjo el reconocedor. Para más detalles, establece el nivel de registro de NVDA en Depuración (Menú NVDA, Preferencias, Opciones, Privacidad y Seguridad, Nivel de registro), habla y abre el registro (NVDA+F1): las líneas "Voice command recognition" muestran lo que escuchó cada reconocedor, y las líneas "Voice command candidate" muestran qué tan cerca estuvieron las mejores coincidencias. Estas líneas solo se escriben que en el nivel de Depuración. |

## Privacidad

El audio del micrófono es procesado en tu ordenador por Vosk y nunca se envía a ningún sitio. La red solo se utiliza cuando permites la descarga del modelo, y únicamente para conectarse a alphacephei.com.

## Traducción

El complemento está escrito en inglés y viene con una traducción al turco. Para traducirlo, copia `voiceCommands.pot` a `locale/<idioma>/LC_MESSAGES/nvda.po` y traduce los mensajes; cada uno tiene un comentario para los traductores. Las palabras utilizadas para repetir un comando ("two times") también son traducibles, por lo que hablar funciona de forma natural en tu idioma.

## Licencia

Comandos de Voz está publicado bajo la Licencia Pública General GNU, versión 2.