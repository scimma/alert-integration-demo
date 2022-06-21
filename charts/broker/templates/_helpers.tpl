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
{{- end -}}