{{- define "tom.backendEnv" -}}
- name: URL_BASE_PATH
  value: {{ .Values.ingress.basePath }}
- name: DJANGO_HOSTNAME
  value: {{ .Values.ingress.hostname }}
- name: DJANGO_DEBUG
  value: {{ .Values.django.debug | quote }}
- name: DJANGO_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: django-secrets
      key: django_secret_key
- name: DB_HOST
  value: {{ .Values.postgresql.hostname }}
- name: DB_USER
  valueFrom:
    secretKeyRef:
      name: django-secrets
      key: postgresql-username
- name: DB_PASS
  valueFrom:
    secretKeyRef:
      name: django-secrets
      key: postgresql-password
- name: DB_NAME
  valueFrom:
    secretKeyRef:
      name: django-secrets
      key: postgresql-database
{{- end -}}
