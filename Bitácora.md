#  Bitácora Técnica: Sistema de Notificaciones Multi-Canal (Event-Driven Architecture)

Antes de desplegar cualquier recurso de infraestructura, se estableció una estrategia de protección financiera para monitorear el consumo de la cuenta AWS y evitar cargos inesperados fuera de la Capa Gratuita o del presupuesto asignado.

### 1.1. Alarma de Facturación (Billing Alarm)
Se implementó una alarma en **Amazon CloudWatch** para recibir notificaciones proactivas cuando el gasto estimado se acerque al límite definido.

* **Métrica Monitoreada:** `EstimatedCharges` (Cargos Estimados Totales de la cuenta).
* **Umbral de Alerta:** $15.00 USD.
* **Región de Configuración:** `us-east-1` (N. Virginia) - *Requisito obligatorio de AWS para métricas de facturación globales.*

<img width="1657" height="620" alt="image" src="https://github.com/user-attachments/assets/007afdb7-68ca-4f58-afc4-4d0663c53126" />


### 1.2. Canal de Notificación (Amazon SNS)
Para entregar la alerta, se configuró un sistema de notificación vía correo electrónico utilizando **Amazon SNS** (Simple Notification Service).

* **Tema SNS:** `AlarmaPresupuesto20USD`.
* **Protocolo:** Email.
* **Estado:** Suscripción confirmada (Endpoint verificado).

> **Evidencia de Configuración:**
> Creación de la suscripción al tema SNS para vincular el correo electrónico de alerta.
> 
<img width="1622" height="506" alt="image" src="https://github.com/user-attachments/assets/e26c7484-390b-4504-ac3c-00cd2d809802" />




---
