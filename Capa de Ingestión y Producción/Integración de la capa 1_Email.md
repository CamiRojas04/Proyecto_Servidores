### Integración de Capa 1 - Email (EventBridge)
Se configuró la regla `RoutingRule-Email-v2` para enrutar eventos con `type: EMAIL` hacia la cola SQS.

* **Reto encontrado:** Los eventos fallaban silenciosamente y terminaban en la DLQ.
* **Diagnóstico:** Al inspeccionar los atributos del mensaje en la DLQ, se encontró el error `INVALID_JSON`.
    > **Evidencia:** Mensaje en DLQ con código de error.
    >
<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/15b8c909-64e9-49fc-addc-271e032fbf9e" />

* **Causa:** El *Transformador de Entrada* de EventBridge estaba generando texto plano o JSON malformado que SQS rechazaba.
* **Solución:** Se reconfiguró la plantilla del transformador para construir explícitamente un objeto JSON válido.
* 
<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/ed041aa0-66b9-4e38-b253-623b5ac752b2" />

* **Resultado Final:** El correo fue recibido correctamente a través del flujo completo EventBridge -> SQS -> Lambda -> SES.

* <img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/ac514935-e6dc-451c-bdef-4a70af59b204" />
