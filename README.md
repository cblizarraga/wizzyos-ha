# WizzyOS

WizzyOS es un custom component de Home Assistant para seleccionar entidades locales y reflejarlas hacia WizzyOS SaaS, iniciando con el nivel del tanque de gas.

## Estado

Proyecto en desarrollo inicial. WizzyOS ya permite seleccionar una entidad existente y crear un sensor visible basado en ella.

La integracion tambien puede configurarse con una URL de backend y API token para enviar eventos de cambio de estado hacia WizzyOS SaaS. Si el envio esta desactivado, WizzyOS sigue funcionando localmente sin llamar al backend.

Repositorio activo: `wizzyos-ha`.

Tipo de integracion: `service`, porque Home Assistant es la fuente de verdad y WizzyOS exporta/refleja datos hacia un servicio externo donde viven los gemelos digitales.

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
6. Opcionalmente configura la URL HTTPS del backend WizzyOS y el API token.
7. Activa `Enviar eventos al backend` solo cuando backend URL y API token sean validos.

Para agregar o quitar entidades desde una configuracion existente, abre WizzyOS, usa el menu de tres puntos y selecciona `Configurar`.

Nota: HACS tambien crea una pagina/dispositivo llamado `WizzyOS` para la entidad de actualizacion del repositorio. Esa pantalla muestra `Update`, `Pre-release` y un enlace `Visitar`. La configuracion de entidades propias de WizzyOS esta en la entrada de la integracion instalada desde `Configuracion > Dispositivos y servicios`, no en la pagina de HACS.

Si solo ves WizzyOS dentro de la pagina de HACS, vuelve a la lista principal de integraciones y usa `Agregar integracion` para buscar `WizzyOS`. La pagina de HACS solo administra el repositorio instalado; no es el flujo de configuracion de entidades de WizzyOS.

## Objetivo De Prueba Basica

Confirmar que la integracion puede leer una entidad local existente, crear un sensor propio de WizzyOS y mantenerlo actualizado con el estado de la entidad seleccionada.

## Arquitectura

- Direccion principal actual: Home Assistant -> WizzyOS SaaS.
- Home Assistant mantiene las entidades locales como fuente de verdad.
- WizzyOS reflejara esas entidades hacia la nube para crear y visualizar gemelos digitales.
- Por esta razon el manifest usa `integration_type: service`.
- El envio usa eventos de cambio de estado de Home Assistant, no polling.
- Si en el futuro WizzyOS SaaS crea dispositivos en la nube y los importa hacia Home Assistant como dispositivos administrados localmente, se reevaluara cambiar a `hub`.

## Pendientes

- Definir el `entity_id` real del tanque de gas.
- Definir la unidad esperada del nivel del tanque.
- Permitir editar o agregar multiples entidades desde un flujo de opciones mas avanzado.

## Solucion De Problemas

Si HACS muestra error `404` intentando descargar una URL como `refs/heads/<commit>.zip`, elimina el repositorio personalizado de HACS y agregalo de nuevo usando la URL del repositorio:

`https://github.com/cblizarraga/wizzyos-ha`

Despues instala la version mas reciente o la rama `main`, reinicia Home Assistant y verifica que el manifest instalado sea `0.3.1` o superior.
