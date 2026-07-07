{{- define "ragops-sentinel.name" -}}
ragops-sentinel
{{- end -}}

{{- define "ragops-sentinel.fullname" -}}
{{ .Release.Name }}-ragops-sentinel
{{- end -}}

{{- define "ragops-sentinel.labels" -}}
app.kubernetes.io/name: {{ include "ragops-sentinel.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
