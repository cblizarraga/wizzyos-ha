# Contrato Preliminar Para Backend WizzyOS

Este documento describe lo que el backend WizzyOS SaaS/GCP debe exponer para que la integracion Home Assistant pueda enviar estados de entidades locales.

Estado: borrador tecnico. Debe revisarse de nuevo cuando la integracion HA termine la implementacion del cliente de envio.

## Contexto

- Home Assistant es la fuente de verdad.
- WizzyOS HA envia eventos de entidades seleccionadas.
- El backend crea o actualiza gemelos digitales con esos eventos.
- La primera entidad objetivo es el nivel del tanque de gas.

## Endpoint Requerido

`POST /v1/home-assistant/events`

Debe aceptar JSON con eventos de cambio de estado.

## Autenticacion

Header:

`Authorization: Bearer <api_token>`

Requisitos:

- Token asociado a una cuenta/tenant/instalacion WizzyOS.
- Token revocable.
- Token rotatable.
- No aceptar tokens en query string.

## Headers

La integracion enviara:

- `Authorization: Bearer <api_token>`
- `Content-Type: application/json`
- `User-Agent: WizzyOS-HA/<version>`

Opcional recomendado:

- `X-WizzyOS-Schema-Version: 1.0`
- `X-WizzyOS-Event-Id: <uuid>`

## Payload

```json
{
  "schema_version": "1.0",
  "source": "home_assistant",
  "integration": "wizzyos",
  "instance_id": "01HAXAMPLE",
  "event_id": "4d67af98-4c67-4677-a980-0bc4ac0c9186",
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

## Campos

- `schema_version`: version del contrato del payload.
- `source`: siempre `home_assistant` para esta integracion.
- `integration`: siempre `wizzyos`.
- `instance_id`: identificador estable de la entrada configurada en HA.
- `event_id`: UUID unico por evento.
- `sent_at`: fecha/hora UTC de envio.
- `entity.entity_id`: entity_id original de Home Assistant.
- `entity.state`: estado como string, igual que HA.
- `entity.attributes`: atributos relevantes de HA.
- `entity.last_changed`: timestamp de ultimo cambio de estado.
- `entity.last_updated`: timestamp de ultima actualizacion.
- `home_assistant.time_zone`: zona horaria local de HA.

## Respuestas

### Exito

`202 Accepted`

```json
{
  "accepted": true,
  "event_id": "4d67af98-4c67-4677-a980-0bc4ac0c9186"
}
```

### Error De Validacion

`400 Bad Request`

```json
{
  "error": "invalid_payload",
  "message": "entity.entity_id is required"
}
```

### Token Invalido

`401 Unauthorized`

```json
{
  "error": "unauthorized"
}
```

### Sin Permiso

`403 Forbidden`

```json
{
  "error": "forbidden"
}
```

### Rate Limit

`429 Too Many Requests`

```json
{
  "error": "rate_limited",
  "retry_after": 30
}
```

### Error Temporal

`503 Service Unavailable`

```json
{
  "error": "temporary_unavailable"
}
```

## Requisitos De Backend

- Aceptar HTTPS.
- Validar token.
- Validar payload.
- Responder rapido; objetivo menor a 1 segundo.
- Soportar idempotencia por `event_id`.
- Registrar eventos por tenant/instalacion.
- Crear o actualizar gemelo digital por `entity_id`.
- Mantener ultimo estado conocido por entidad.
- No rechazar estados como `unknown` o `unavailable`; almacenarlos como estados validos o marcarlos como no disponibles.
- No exigir que `state` sea numerico; HA siempre lo entrega como string.

## Modelo Minimo Sugerido

Entidad/gemelo digital:

- `tenant_id`
- `instance_id`
- `entity_id`
- `friendly_name`
- `state`
- `unit_of_measurement`
- `attributes`
- `last_changed`
- `last_updated`
- `received_at`

Evento:

- `event_id`
- `tenant_id`
- `instance_id`
- `entity_id`
- `payload`
- `received_at`

## Consideraciones Para GCP

- Cloud Run puede exponer el endpoint HTTP.
- Usar Secret Manager para secretos del backend.
- Usar Firestore, Cloud SQL o BigQuery segun necesidad de consulta.
- Cloud Logging debe registrar errores sin exponer tokens.
- Si se usa Pub/Sub, el endpoint puede validar y publicar el evento para procesamiento asincrono.

## Preguntas Para El Agente Backend

- Como se generara y revocara el `api_token`?
- Existira tenant/account id explicito o se deriva del token?
- Donde se persistiran gemelos digitales?
- Se necesita historial completo o solo ultimo estado?
- Cuales son limites de rate por instalacion?
- Se requiere dashboard en tiempo real con WebSocket/SSE?
- Se debe aceptar batch de eventos en una version posterior?

## Criterios De Aceptacion Backend

- Recibe `POST /v1/home-assistant/events` con token valido.
- Responde `202` para payload valido.
- Rechaza token invalido con `401`.
- Persiste o actualiza el gemelo digital por `entity_id`.
- Soporta idempotencia por `event_id`.
- Registra errores sin exponer secretos.
- Puede probarse con un payload del tanque de gas.
