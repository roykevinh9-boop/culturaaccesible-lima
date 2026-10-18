# Publicación futura de CulturaAccesible Lima

Precios consultados el 18/10/2026. Esta es una propuesta; la aplicación continúa ejecutándose localmente. Los importes son USD, antes de impuestos. No se ha contratado ni publicado un servidor.

## Alternativas y presupuesto

| Alternativa | Precio del proveedor | Presupuesto para este proyecto |
|---|---|---|
| Railway Hobby | Mínimo USD 5/mes, que cubre los primeros USD 5 de consumo. El exceso se cobra por recursos utilizados. | Estimación inicial propia: USD 15–30/mes para Java, Python y MySQL con poco tráfico. Se debe medir el consumo para confirmarlo. |
| DigitalOcean Droplet Basic | USD 12/mes por 2 GiB y 1 vCPU; USD 24/mes por 4 GiB y 2 vCPU. | Probar 2 GiB para el piloto; usar 4 GiB si las mediciones lo requieren. Copias de seguridad y otros servicios se presupuestan aparte. Requiere administrar el servidor. |
| HTTPS | Railway incluye certificados automáticos. Let's Encrypt ofrece certificados TLS gratuitos para un servidor propio. | El certificado puede costar USD 0. Su instalación no vuelve segura por sí sola a toda la aplicación. |

Railway ofrece una dirección de su plataforma; un dominio propio es opcional y su precio depende del nombre, la extensión y la renovación. El chatbot actual se ejecuta con modelos locales y no necesita pagar una API de IA externa; su cómputo sí consume recursos del hosting.

## Cómo se publicaría

1. Preparar Java y Python para Linux, con archivos de contenedor e inicio separados. El iniciador actual de Windows sirve para la demostración local.
2. Crear una base MySQL persistente en el servidor e importar la estructura y los datos elegidos. Conservar el respaldo local; no publicar `.local/` ni sus contraseñas.
3. Configurar las conexiones mediante variables privadas del hosting. El navegador accede a Java; Java consulta MySQL y Python por la red interna.
4. Exponer únicamente la web mediante HTTPS. En Railway, la comunicación privada entre servicios utiliza túneles WireGuard cifrados y la base puede permanecer sin acceso público.
5. Antes de abrirla al público, limitar solicitudes al chat y los reportes, añadir protección contra abuso, comprobar validación y cabeceras, usar permisos mínimos y separar datos de ejemplo. Si se agregan cuentas, usar un sistema de autenticación y hashes de contraseñas apropiados; no guardarlas como texto.
6. Definir copias de seguridad cifradas, comprobar una restauración, configurar alertas y límites de gasto, y probar el dominio, el chat, los filtros y la persistencia después de reiniciar los servicios.

Una vez desplegados también MySQL y Python, la web podría funcionar con esta PC apagada. HTTPS cifra la comunicación; el cifrado de discos y respaldos requiere configuración adicional según el proveedor. No se promete protección absoluta.

## Fuentes oficiales

- Railway, planes y facturación: https://docs.railway.com/pricing/plans
- Railway, HTTPS y dominios: https://docs.railway.com/networking/public-networking
- Railway, red privada y cifrado: https://docs.railway.com/networking/private-networking/how-it-works
- Railway, MySQL: https://docs.railway.com/databases/mysql
- DigitalOcean, precios: https://www.digitalocean.com/pricing/droplets
- Let's Encrypt, certificados gratuitos: https://letsencrypt.org/
