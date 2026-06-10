# Diseno Del Puente HA -> WizzyOS SaaS

## Objetivo

WizzyOS debe actuar como puente entre Home Assistant y WizzyOS SaaS/GCP. Home Assistant es la fuente de verdad de las entidades locales y WizzyOS debe reflejar sus estados hacia la nube para crear o actualizar gemelos digitales.

## Alcance De La Integracion

- Seleccionar entidades existentes de Home Assistant.
- Mantener sensores espejo locales para validar visualmente lo seleccionado.
- Exportar estados y atributos hacia el backend de WizzyOS.
- Enviar datos por eventos de cambio de estado, no por polling.
- Permitir configurar endpoint y credenciales desde la UI de Home Assistant.
- Manejar errores de red sin romper Home Assistant.

## No Alcance Inicial

- Crear dispositivos desde WizzyOS SaaS hacia Home Assistant.
- Control remoto de entidades desde la nube.
- Sincronizacion bidireccional.
- Dashboard frontend propio dentro de Home Assistant.
- Descubrimiento automatico masivo de todas las entidades.

## Tipo De Integracion

`integration_type: service`

Justificacion: Home Assistant exporta datos hacia un servicio externo. WizzyOS SaaS/GCP consume esos datos para visualizar gemelos digitales. Si en el futuro WizzyOS crea dispositivos en la nube y los importa hacia Home Assistant, se reevaluara `hub`.

## Flujo Funcional

1. Usuario instala WizzyOS desde HACS.
2. Usuario agrega la integracion desde Home Assistant.
3. Config flow solicita:
   - Nombre de la instancia.
   - Entidad inicial.
   - URL del backend.
   - API token o credencial equivalente.
4. Options flow permite editar:
   - Lista de entidades exportadas.
   - URL del backend.
   - Token.
   - Habilitar/deshabilitar envio.
5. WizzyOS crea sensores espejo locales para las entidades seleccionadas.
6. WizzyOS se suscribe a cambios de estado de las entidades seleccionadas.
7. Cuando una entidad cambia, WizzyOS envia un payload al backend.
8. El backend confirma recepcion.
9. Si el backend falla, WizzyOS registra el error y reintenta de forma limitada.

## Configuracion Requerida

Campos propuestos:

- `name`: nombre visible de la entrada WizzyOS.
- `entity_id`: entidad inicial seleccionada.
- `entities`: lista de entidades a exportar.
- `backend_url`: URL base del backend WizzyOS.
- `api_token`: token secreto para autenticar la instancia.
- `enabled`: booleano para activar o pausar envio.

## Almacenamiento En Home Assistant

Datos no secretos en config entry:

- `name`
- `entity_id`
- `backend_url`

Opciones editables:

- `entities`
- `enabled`

Credenciales:

- `api_token` debe tratarse como secreto. Si Home Assistant no permite almacenamiento seguro adicional en esta etapa, documentar el riesgo y mantenerlo en config entry con cuidado hasta implementar un mecanismo mejor.

## Eventos De Estado

La integracion debe usar `async_track_state_change_event` para las entidades configuradas.

Reglas:

- Enviar evento solo si `new_state` existe.
- Ignorar entidades no configuradas.
- Incluir `old_state` solo si aporta valor y no infla demasiado el payload.
- Evitar enviar atributos gigantes o sensibles si se identifican.

## Payload De Telemetria

Payload minimo propuesto:

```json
{
  "schema_version": "1.0",
  "source": "home_assistant",
  "integration": "wizzyos",
  "instance_id": "<config_entry_id>",
  "event_id": "<uuid>",
  "sent_at": "2026-06-09T00:00:00Z",
  "entity": {
    "entity_id": "sensor.nivel_de_tanque_de_gas",
    "state": "75",
    "attributes": {
      "unit_of_measurement": "%",
      "friendly_name": "Nivel de tanque de gas"
    },
    "last_changed": "2026-06-09T00:00:00Z",
    "last_updated": "2026-06-09T00:00:00Z"
  },
  "home_assistant": {
    "time_zone": "America/Mexico_City"
  }
}
```

## Endpoints Esperados

Endpoint minimo:

- `POST /v1/home-assistant/events`

Headers:

- `Authorization: Bearer <api_token>`
- `Content-Type: application/json`
- `User-Agent: WizzyOS-HA/<version>`

Respuestas esperadas:

- `202 Accepted`: evento recibido.
- `400 Bad Request`: payload invalido.
- `401 Unauthorized`: token invalido.
- `403 Forbidden`: token sin permiso.
- `429 Too Many Requests`: aplicar backoff.
- `500/503`: error temporal, reintentar.

## Reintentos

Primera version:

- Reintento simple con backoff corto.
- No bloquear el event loop de Home Assistant.
- No persistir cola en disco inicialmente.
- Si falla, registrar warning con entidad, codigo HTTP y razon.

Version posterior:

- Cola persistente opcional.
- Deduplicacion por `event_id`.
- Batch de eventos si el volumen crece.

## Seguridad

- Usar HTTPS para backend.
- No loggear tokens.
- Sanitizar errores para evitar exponer credenciales.
- Permitir rotar token desde options flow.
- Rechazar URL sin `https://` salvo modo desarrollo explicito.

## Observabilidad Local

Agregar diagnostico basico en Home Assistant:

- Ultimo envio exitoso.
- Ultimo error.
- Cantidad de eventos enviados desde inicio.
- Cantidad de errores desde inicio.
- Estado de conexion/logica de envio.

## Plan De Implementacion En La Integracion

1. Agregar constantes para `backend_url`, `api_token`, `enabled` y metricas. Estado: implementado.
2. Extender config flow para pedir backend y token. Estado: implementado.
3. Extender options flow para editar backend, token, enabled y entidades. Estado: implementado.
4. Crear cliente HTTP asincrono usando la sesion de Home Assistant. Estado: implementado.
5. Suscribir cambios de estado para entidades configuradas. Estado: implementado.
6. Construir payload versionado. Estado: implementado.
7. Enviar payload al backend. Estado: implementado, pendiente de prueba con backend real.
8. Manejar errores HTTP/red. Estado: implementado basico.
9. Agregar datos de diagnostico local. Estado: parcial, metricas internas creadas.
10. Documentar pruebas manuales. Estado: pendiente.

## Criterios De Aceptacion

- WizzyOS instala desde HACS sin errores.
- WizzyOS aparece como `service`.
- Usuario puede seleccionar entidades existentes.
- Usuario puede configurar backend URL y token.
- Al cambiar el tanque de gas, se envia un evento al backend.
- Si backend no responde, Home Assistant no se rompe.
- Los errores aparecen en logs sin exponer token.
- La memoria documental queda actualizada tras cada cambio relevante.
