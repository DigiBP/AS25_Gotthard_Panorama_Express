To start the n8n create a GET Post to this link: http://localhost:5678/webhook-test/81b35ac1-fff7-4899-b673-f0bae0093212

n8n [Generate CHecklist] --> /Generate_Checklist --> Backend 
backend --> /Webhook_status_checklist --> n8n
n8n [Create Order] --> /create_order --> backend
backend --> /Webhook_order_response --> n8n
n8n [Contact Storageworker] --> /Communication --> backend
backend --> /Webhook_con_status --> n8n

