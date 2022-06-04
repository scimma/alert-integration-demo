{{- define "tom.backendEnv" }}
- name: URL_BASE_PATH
  value: {{ .Values.ingress.basePath }}
- name: DJANGO_HOSTNAME
  value: {{ .Values.ingress.hostname }}
- name: DJANGO_DEBUG
  value: {{ .Values.django.debug | quote }}
- name: DJANGO_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: tom-demo-secrets
      key: django_secret_key
- name: DB_HOST
  value: {{ .Values.postgresql.hostname }}
- name: DB_NAME
  value: {{ .Values.postgresql.postgresqlDatabase }}
- name: DB_USER
  value: {{ .Values.postgresql.postgresqlUsername }}
- name: DB_PASS
  valueFrom:
    secretKeyRef:
      name: tom-demo-secrets
      key: postgres-password
{{- if .Values.oidc.enabled }}
- name: OIDC_SRV_DISCOVERY_URL
  value: {{ .Values.oidc.discoveryUrl | quote }}
- name: OIDC_REDIRECT_URL
  value: {{ .Values.oidc.redirectUrl | quote }}
- name: OIDC_REDIRECT_URL_POST_LOGOUT
  value: {{ .Values.oidc.redirectPostLogoutUrl | quote }}
- name: OIDC_OP_AUTHORIZATION_ENDPOINT
  value: {{ .Values.oidc.authorize_url | quote }}
- name: OIDC_OP_TOKEN_ENDPOINT
  value: {{ .Values.oidc.token_url | quote }}
- name: OIDC_OP_USER_ENDPOINT
  value: {{ .Values.oidc.userdata_url | quote }}
- name: OIDC_SCOPES
  value: {{ .Values.oidc.scopes | quote }}
- name: OIDC_LOGIN_URL_PATH
  value: {{ .Values.oidc.login_url_path | quote }}
- name: OIDC_RP_SIGN_ALGO
  value: {{ .Values.oidc.signingAlgorithm | quote }}
- name: OIDC_OP_JWKS_ENDPOINT
  value: {{ .Values.oidc.jwksEndpoint | quote }}
{{- with .Values.oidc.existingSecret }}
- name: OIDC_CLIENT_ID
  valueFrom:
    secretKeyRef:
      name: "{{ . }}"
      key: "oidc-client-id"
- name: OIDC_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: "{{ . }}"
      key: "oidc-client-secret"
{{- end }}
{{- end }}
{{- end }}
