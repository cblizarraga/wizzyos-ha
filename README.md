# WizzyOS

WizzyOS es un custom component de Home Assistant para visualizar entidades basicas de una instancia local, iniciando con el nivel del tanque de gas.

## Estado

Proyecto en desarrollo inicial. WizzyOS ya permite seleccionar una entidad existente y crear un sensor visible basado en ella.

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
5. Selecciona una entidad existente, por ejemplo la entidad real del tanque de gas.

Para agregar o quitar entidades desde una configuracion existente, abre WizzyOS, usa el menu de tres puntos y selecciona `Configurar`.

## Objetivo De Prueba Basica

Confirmar que la integracion puede leer una entidad local existente, crear un sensor propio de WizzyOS y mantenerlo actualizado con el estado de la entidad seleccionada.

## Pendientes

- Definir el `entity_id` real del tanque de gas.
- Definir la unidad esperada del nivel del tanque.
- Permitir editar o agregar multiples entidades desde un flujo de opciones mas avanzado.

## Solucion De Problemas

Si HACS muestra error `404` intentando descargar una URL como `refs/heads/<commit>.zip`, elimina el repositorio personalizado de HACS y agregalo de nuevo usando la URL del repositorio:

`https://github.com/cblizarraga/wizzyos-ha`

Despues instala la version mas reciente o la rama `main`, reinicia Home Assistant y verifica que el manifest instalado sea `0.3.1` o superior.
