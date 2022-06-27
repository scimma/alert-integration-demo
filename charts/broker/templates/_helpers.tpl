{{- define "broker.backendEnv" -}}
- name: MARIADB_SERVICE_NAME
  value: {{ .Values.mariadb.fullnameOverride | quote }}
- name: MARIADB_DATABASE
  value: {{ .Values.mariadb.auth.database }}
- name: MARIADB_USER
  value: {{ .Values.mariadb.auth.username }}
- name: MARIADB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mariadb.auth.existingSecret | quote }}
      key: "mariadb-password"
- name: INGEST_WAIT_TIME
  value: {{ .Values.sourceDataIngest.waitTime | quote }}
- name: CLASSIFY_WAIT_TIME
  value: {{ .Values.classifier.waitTime | quote }}
- name: SOURCE_DATA_PUBLISH_WAIT_TIME
  value: {{ .Values.sourceDataPublisher.waitTime | quote }}
- name: ALERT_DATA_PUBLISH_WAIT_TIME
  value: {{ .Values.alertDataPublisher.waitTime | quote }}
- name: HOP_URL_SOURCE
  value: {{ .Values.sourceDataPublisher.hopUrl | quote }}
- name: HOP_URL_RESULTS
  value: {{ .Values.alertDataPublisher.hopUrl | quote }}
{{- end -}}
