# Ejecucion

Este archivo registra el avance practico del desarrollo del componente hasta lograr una prueba basica en Home Assistant.

## Estado Actual

- Repositorio inicializado.
- Estructura base del custom component creada en `custom_components/wizzyos`.
- Configuracion de opencode creada en `opencode.json`.
- Agente especializado creado en `.opencode/agent/ha-component-dev.md`.
- Memoria documental creada en `docs/memory.json`.
- Constantes compartidas creadas en `custom_components/wizzyos/const.py`.
- Metadatos para repositorio personalizado creados en `hacs.json`.
- Guia de instalacion creada en `README.md`.
- Nombre visible de la integracion actualizado a `WizzyOS`.
- Reglas de gestion de contexto documentadas en `docs/context-management.md`.
- Tipo de integracion actualizado de `hub` a `entity` para que Home Assistant muestre entidades en vez de hubs.
- Plataforma `sensor` creada en `custom_components/wizzyos/sensor.py`.
- Config flow actualizado para seleccionar entidades existentes con selector nativo.
- Options flow creado para configurar varias entidades desde el menu `Configurar`.
- Version del manifest actualizada a `0.5.0`.
- Archivos iniciales creados:
  - `manifest.json`
  - `__init__.py`
  - `config_flow.py`

## Objetivo de la Primera Prueba

Ver el nivel del tanque de gas de la instancia local de Home Assistant usando una entidad existente.

## Datos Necesarios

- `entity_id` del tanque de gas: pendiente.
- Unidad esperada: pendiente.
- Metodo de visualizacion: pendiente. La lectura inicial se guarda en `hass.data`.

## Pasos de Ejecucion

### 1. Completar Config Flow

- Agregar campo `entity_id`.
- Validar formato basico del `entity_id`.
- Guardar el valor en la config entry.

Estado: implementado. El flujo solicita `name` y `entity_id`, valida formato basico, confirma que la entidad exista en `hass.states` y usa el `entity_id` como identificador unico para evitar duplicados.

### 2. Leer Estado de la Entidad

- Obtener la entidad desde `hass.states.get(entity_id)`.
- Confirmar que existe.
- Guardar estado y atributos relevantes.

Estado: implementado. `async_setup_entry` obtiene la entidad configurada con `hass.states.get(entity_id)`, guarda disponibilidad, estado y atributos en `hass.data`, y carga la plataforma `sensor`.

### 3. Definir Visualizacion Inicial

- Evaluar la opcion mas simple para una prueba basica.
- Priorizar una solucion que permita confirmar lectura real del estado.
- Documentar el mecanismo seleccionado.

Estado: implementado. WizzyOS crea un sensor visible que refleja la entidad seleccionada y se actualiza cuando cambia la entidad origen.

### 4. Probar en Home Assistant Local

- Agregar `https://github.com/cblizarraga/wizzyos-ha` como repositorio personalizado de HACS.
- Instalar la integracion desde HACS.
- Reiniciar Home Assistant.
- Agregar la integracion desde la UI.
- Seleccionar o ingresar el `entity_id` del tanque de gas.
- Confirmar que el estado se obtiene correctamente.

Estado: pendiente.

## Registro de Avance

### 2026-06-07

- Se creo la documentacion inicial del desarrollo.
- Se definio la meta inicial: visualizar entidades basicas de Home Assistant empezando por el tanque de gas.
- Se analizo la documentacion inicial y se identifico la siguiente ruta de trabajo: capturar `entity_id`, leer estado con `hass.states.get(entity_id)` y definir una visualizacion basica.
- Se creo el agente `ha-component-dev` para continuar el desarrollo usando `docs/plan.md`, `docs/exec.md` y `docs/memory.json` como fuente de verdad.
- Se creo `docs/memory.json` como memoria documental de largo plazo del proyecto.
- Se agrego `entity_id` al config flow con validacion de formato, validacion de existencia y prevencion de duplicados por entidad.
- Se agrego lectura inicial del estado configurado desde `hass.states` y almacenamiento minimo en `hass.data`.
- Se definio que el metodo de instalacion sera desde repositorio personalizado, no copiando la carpeta manualmente.
- Se agrego `hacs.json` y `README.md` con instrucciones iniciales para instalar desde HACS.

### 2026-06-08

- Durante la prueba local, Home Assistant mostro el error `No se pudo cargar el flujo de configuración: {"message":"Invalid handler specified"}` al intentar agregar la integracion.
- Se identifico una causa probable en `config_flow.py`: import incompatible de `valid_entity_id` desde `homeassistant.helpers.entity`.
- Se cambio el import a `homeassistant.core.valid_entity_id` y se simplifico la anotacion de retorno de `async_step_user` para compatibilidad.
- Se cambio el nombre visible de la integracion de `Componente HA` a `WizzyOS`, manteniendo inicialmente el dominio tecnico `componente_ha`.
- Se cambio el dominio tecnico de `componente_ha` a `wizzyos` y la carpeta del componente a `custom_components/wizzyos`.
- Se preparo el cambio de nombre del repositorio de `componente-ha` a `wizzyos-ha`.
- Se establecio como regla permanente documentar avances, decisiones, errores y bloqueos, manteniendo `docs/memory.json` como memoria de largo plazo.
- Se confirmo que la integracion WizzyOS ya funciona en Home Assistant local.
- Se cambio `integration_type` de `hub` a `entity` en `manifest.json` para que la UI use `Agregar Entidad` y `Entidades` en vez de `Agregar Hub` y `Hubs`.
- Se incremento la version del manifest a `0.1.1` para publicar el ajuste de metadatos.
- Se agrego `sensor.py` para crear un sensor propio de WizzyOS por cada entidad configurada.
- Se actualizo el config flow para usar un selector nativo de entidades existentes.
- Se agrego options flow para seleccionar varias entidades existentes desde el menu `Configurar` de la integracion.
- Se incremento la version del manifest a `0.3.0`.
- El log local confirmo que WizzyOS crea `sensor.nivel_de_tanque_de_gas`.
- Se corrigio el warning causado por copiar `device_class` incompatible desde la entidad origen.
- Se reforzo el registro del options flow con `@callback` y se incremento la version del manifest a `0.3.1`.
- El log local mostro errores de HACS descargando `refs/heads/cb3ea0a.zip` y `refs/heads/a29c5dc.zip`, lo que indica que HACS intento usar hashes de commit como ramas y no instalo la version nueva.
- Se documento reinstalar o re-agregar el repositorio personalizado desde `https://github.com/cblizarraga/wizzyos-ha` y usar `main` o una version estable.
- La captura del usuario mostro la pagina/dispositivo creado por HACS para el repositorio, no la entrada configurable real de WizzyOS.
- Se agrego `device_info` a los sensores espejo para que Home Assistant agrupe las entidades propias bajo un dispositivo WizzyOS real, separado del dispositivo HACS Update.
- Se revirtio `integration_type` de `entity` a `hub` porque el cambio a `entity` altero el flujo visible y la primera version con `hub` si mostraba el formulario para seleccionar entidad.
- Se definio la arquitectura principal como Home Assistant -> WizzyOS SaaS/GCP para reflejar entidades y crear gemelos digitales en la nube.
- Se cambio `integration_type` a `service`, que corresponde a integraciones que conectan Home Assistant con un servicio externo.
- Se confirmo que WizzyOS ya aparece como servicio en Home Assistant y que el tanque de gas quedo configurado.
- El log mostro `AttributeError: property 'config_entry' of 'WizzyOSOptionsFlow' object has no setter` al abrir options flow.
- Se corrigio `WizzyOSOptionsFlow` para usar `_config_entry` en vez de asignar la propiedad reservada `config_entry`.
- Se incremento la version del manifest a `0.5.1`.
- HACS intento descargar `refs/heads/1c1337b.zip`; se creo una rama remota `1c1337b` apuntando al commit corregido para resolver ese 404.
- Despues de reiniciar/reordenar HACS, el usuario reporto que WizzyOS parece quedar funcionando correctamente.
- Se revisaron logs posteriores: los errores activos son de ESPHome al no poder conectar con `wizzyos-homelab` y `kc868-a4-cbl-pruebas1`; no corresponden al custom component WizzyOS.
- Los errores `AttributeError` de `WizzyOSOptionsFlow` y `HACS 404 refs/heads/1c1337b.zip` corresponden a entradas historicas anteriores al arreglo.
- El usuario confirmo que `Configurar` ya abre sin errores.

## Riesgos o Bloqueos

- Confirmado: el tanque de gas ya quedo configurado en WizzyOS.
- Confirmado: WizzyOS aparece como servicio en Home Assistant.
- Confirmado: `Configurar` abre sin errores despues del fix de `_config_entry`.
- Falta confirmar que HACS descarga correctamente desde `main` o desde un tag estable en vez de intentar descargar hashes como ramas.
- Confirmado de forma preliminar: tras reiniciar, WizzyOS parece quedar funcionando correctamente desde HACS/Home Assistant.
- La prueba local depende de tener acceso a una instancia de Home Assistant con la entidad ya configurada.
- Confirmado: la integracion ya funciona en Home Assistant local despues de los ajustes de dominio/config flow.
