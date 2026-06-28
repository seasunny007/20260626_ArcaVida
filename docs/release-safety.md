# 发布安全说明 / Notas de seguridad de publicacion / Release Safety Notes

本文档提供中文、西班牙语和英文说明；如三种文本存在不一致，以中文文本为准。

Este documento ofrece informacion en chino, espanol e ingles. Si existe alguna inconsistencia entre los tres textos, prevalecera el texto chino.

This document provides Chinese, Spanish, and English information. If there is any inconsistency among the three texts, the Chinese text controls.

本文面向维护者和发布者，用于降低社区预览发布中的隐私、安全、合规和误用风险。

Esta nota esta dirigida a mantenedores y publicadores. Reduce riesgos de privacidad, seguridad, cumplimiento y uso indebido durante publicaciones de vista previa comunitaria.

This note is for maintainers and publishers. It reduces privacy, safety, compliance, and misuse risks during community-preview releases.

v2.0.0 的 Public Release 是社区预览版的公开发布，目标是接受公开审阅和支持本地试运行。它不是生产级救援系统、自动核实系统、资源调度系统或应急派遣权威。

El Public Release v2.0.0 es la publicacion publica de la vista previa comunitaria, destinada a revision publica y pruebas locales. No es un sistema de rescate de produccion, sistema de verificacion automatica, sistema de asignacion de recursos ni autoridad de despacho de emergencias.

The v2.0.0 Public Release is the public release of the community preview, intended for public review and local trial use. It is not a production rescue system, automatic verification system, resource-allocation system, or emergency-dispatch authority.

## 数据边界 / Limite de datos / Data Boundary

发布版不包含面向真实求助数据的数据收集、真实个案样本库或公开导出功能。公开演示、Issue、PR 和社区讨论只应使用合成、公开或充分匿名化样例。

La version de publicacion no incluye funciones de recoleccion de datos, repositorios de casos reales ni exportacion publica para datos reales de solicitud de ayuda. Las demostraciones publicas, issues, pull requests y discusiones comunitarias solo deben usar ejemplos sinteticos, publicos o suficientemente anonimizados.

The release build does not include data-collection, sample-repository, or public-export features for real help-request data. Public demos, issues, pull requests, and community discussion should use only synthetic, public, or fully anonymized samples.

默认策略 / Politica predeterminada / Default policy:

- 公开演示、Issue、PR 和社区讨论只使用合成、公开或充分匿名化样例。 / Usa solo ejemplos sinteticos, publicos o suficientemente anonimizados en demos, issues, pull requests y discusion comunitaria. / Use only synthetic, public, or fully anonymized samples in demos, issues, pull requests, and community discussion.
- 不收集未经授权的真实私密求助消息、电话号码、精确个人位置、身份证件或联系人信息。 / No recopiles mensajes privados reales sin autorizacion, telefonos, ubicaciones personales exactas, documentos de identidad ni datos de contacto. / Do not collect unauthorized private help-request messages, phone numbers, exact personal locations, identity documents, or contact details.
- 不在公开仓库中提供真实个案样本库、批量导出或二次分析入口。 / No proporciones repositorios de casos reales, exportaciones masivas ni entradas de analisis secundario en el repositorio publico. / Do not provide real-case sample repositories, bulk exports, or secondary-analysis entry points in the public repository.

## 争议风险 / Riesgos de controversia / Controversy Risks

可能引起争议的点包括 / Potential controversy risks include:

Posibles puntos de controversia:

- 被误解为收集灾民或求助者数据。 / Ser malinterpretado como recoleccion de datos de personas afectadas o solicitantes de ayuda. / Being misunderstood as collecting affected-person or help-requester data.
- 匿名化不足导致重新识别风险。 / Anonimizacion insuficiente que genere riesgo de reidentificacion. / Insufficient anonymization creating re-identification risk.
- 将数据收集或二次分析目标置于救援协调目标之上。 / Parecer que se prioriza la recoleccion de datos o el analisis secundario sobre la coordinacion de ayuda. / Appearing to prioritize data collection or secondary analysis over relief coordination.
- 用真实灾情样例做公开展示。 / Usar mensajes reales de desastre en demos publicas. / Using real disaster messages in public demos.
- 暗示系统能核实事实、定位人员或派遣队伍。 / Sugerir que el sistema puede verificar hechos, localizar personas o despachar equipos. / Implying that the system can verify facts, locate people, or dispatch teams.

发布口径应明确：ArcaVida 是桌面分拣辅助工具，不是公众求助入口、现场救援系统、数据收集平台或应急派遣权威。

La comunicacion de publicacion debe ser clara: ArcaVida es una herramienta auxiliar de triaje de escritorio, no un portal publico de solicitud de ayuda, sistema de rescate en campo, plataforma de recoleccion de datos ni autoridad de despacho de emergencias.

Release wording should be explicit: ArcaVida is a desk-side triage aid, not a public help-request portal, field rescue system, data-collection platform, or emergency-dispatch authority.

## 发布者保护 / Protecciones para publicadores / Publisher Protections

发布者应采取以下保护措施 / Publishers should use these protections:

Los publicadores deben usar estas protecciones:

- 使用 GitHub Release 发布版本，不把 `main` 分支当作正式发布物。 / Publica versiones mediante GitHub Releases; no trates `main` como artefacto oficial. / Publish versions through GitHub Releases instead of treating `main` as the release artifact.
- 发布前清理 Git 历史中的本机路径、凭证、临时数据库、日志和个人信息。 / Limpia rutas locales, credenciales, bases de datos temporales, logs e informacion personal del historial de Git antes de una publicacion amplia. / Clean local paths, credentials, temporary databases, logs, and personal information from Git history before broad release.
- Release notes 写明非目标、人工复核要求、非商业许可和无担保声明。 / Las notas de publicacion deben indicar no objetivos, revision humana, licencia no comercial y ausencia de garantia. / Release notes should state non-goals, human-review requirements, non-commercial licensing, and no-warranty terms.
- 使用合成数据截图和演示，不展示真实求助消息。 / Usa capturas y demos con datos sinteticos; no muestres mensajes reales de solicitud de ayuda. / Use synthetic screenshots and demos; do not show real help-request messages.
- 不在公开 Issue 中处理真实个案、定位请求或救援派遣请求。 / No gestiones casos reales, solicitudes de ubicacion ni solicitudes de despacho en issues publicos. / Do not handle real cases, location requests, or dispatch requests in public issues.
- 对安全问题使用私密报告渠道或 GitHub Security Advisories。 / Usa canales privados o GitHub Security Advisories para problemas de seguridad. / Use private reporting channels or GitHub Security Advisories for security issues.
- 保留清晰的许可、贡献、行为准则和安全边界文档。 / Mantén documentos claros de licencia, contribucion, conducta y limites de seguridad. / Keep clear license, contribution, code-of-conduct, and safety-boundary documents.
- 不承诺效果、覆盖地区、可用性、救援结果或响应时间。 / No prometas resultados, cobertura geografica, disponibilidad, resultados de rescate ni tiempos de respuesta. / Do not promise outcomes, geographic coverage, availability, rescue results, or response times.

## 建议发布节奏 / Flujo recomendado de publicacion / Recommended Release Flow

1. 使用 GitHub Release 发布社区预览版。 / Publica la vista previa comunitaria mediante GitHub Releases. / Publish the community preview through GitHub Releases.
2. 小范围邀请救援协调、隐私安全和开源维护者审阅。 / Invita a un grupo pequeno de coordinacion de ayuda, privacidad/seguridad y mantenedores de codigo abierto para revision. / Invite a small group of relief-coordination, privacy/safety, and open-source maintainers to review it.
3. 收到反馈后再扩大传播。 / Amplia la difusion solo despues de recibir comentarios de revision. / Broaden distribution only after review feedback.
4. 后续如增加任何真实数据导出或二次分析能力，应先完成隐私、安全和适用场景评审。 / Si en el futuro se agregan exportacion de datos reales o analisis secundario, completa primero la revision de privacidad, seguridad y caso de uso. / If future real-data export or secondary-analysis features are added, complete privacy, safety, and use-case review first.
