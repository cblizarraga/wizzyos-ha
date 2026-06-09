# WizzyOS

WizzyOS es un custom component de Home Assistant para visualizar entidades basicas de una instancia local, iniciando con el nivel del tanque de gas.

## Estado

Proyecto en desarrollo inicial. WizzyOS ya permite configurar un `entity_id` existente y leer su estado inicial desde Home Assistant.

Repositorio activo: `wizzyos-ha`.

## Instalacion Desde Repositorio

La instalacion esperada es como repositorio personalizado, no copiando archivos manualmente.

### HACS

1. En Home Assistant, abre HACS.
2. Ve a Integraciones.
3. Abre el menu de tres puntos.
4. Selecciona Repositorios personalizados.
5. Agrega esta URL: `https://github.com/cblizarraga/wizzyos-ha`
6. Selecciona la categoria Integracion.
7. Instala `WizzyOS`.
8. Reinicia Home Assistant.

## Configuracion

1. En Home Assistant, ve a Configuracion.
2. Abre Dispositivos y servicios.
3. Agrega la integracion `WizzyOS`.
4. Ingresa un nombre.
5. Ingresa el `entity_id` real del tanque de gas, por ejemplo `sensor.tanque_gas`.

## Objetivo De Prueba Basica

Confirmar que la integracion puede leer una entidad local existente usando `hass.states.get(entity_id)` y guardar una lectura inicial en `hass.data`.

## Pendientes

- Definir el `entity_id` real del tanque de gas.
- Definir la unidad esperada del nivel del tanque.
- Implementar la visualizacion inicial del valor.
