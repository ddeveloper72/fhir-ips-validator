# FHIR IPS Bundle Validator - Docker Deployment Guide

Complete guide for deploying your own instance of the FHIR IPS Bundle Validator using Docker.

---

## 🎯 **Why Deploy Your Own Instance?**

- ✅ **Data Privacy**: All validation happens in your infrastructure (HIPAA/GDPR compliant)
- ✅ **No Rate Limits**: Use your own API keys without sharing
- ✅ **Custom Configuration**: Configure validation services to your needs
- ✅ **Enterprise Ready**: Deploy on-premise or in your cloud environment
- ✅ **Cost Control**: Only pay for your own API usage

---

## 📋 **Prerequisites**

### **Required:**
- Docker 20.10+ and Docker Compose 2.0+
- API credentials for validation services you want to use:
  - Azure FHIR Service (optional - for Azure FHIR validation)
  - eHDSI Gazelle API key (optional - for CDA validation)
  - EHDS Gazelle API key (optional - for FHIR IPS validation)

### **Obtain API Keys:**

#### **Azure FHIR Service** (Optional)
1. Create Azure FHIR Service in Azure Portal
2. Create Service Principal with FHIR Data Contributor role
3. Note: Base URL, Client ID, Client Secret, Tenant ID

#### **eHDSI Gazelle** (Optional)
1. Register at https://gazelle.ehdsi.eu/gazelle/user-management/registration
2. Login and go to: User Management → API Keys
3. Generate new API key
4. Note expiry date (typically 30 days)

#### **EHDS Gazelle** (Optional)
1. Register at https://ehds.gazelle-platform.net/gazelle/user-management/registration
2. Login and go to: User Management → API Keys
3. Generate new API key
4. Note expiry date (typically 30 days)

---

## 🚀 **Quick Start**

### **Step 1: Clone Repository**

```bash
git clone https://github.com/ddeveloper72/fhir-ips-validator.git
cd fhir-ips-validator
```

### **Step 2: Configure Credentials**

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Azure FHIR (optional)
AZURE_FHIR_BASE_URL=your-fhir-service.fhir.azurehealthcareapis.com
AZURE_FHIR_CLIENT_ID=your-client-id
AZURE_FHIR_CLIENT_SECRET=your-secret
AZURE_FHIR_TENANT_ID=your-tenant-id

# eHDSI Gazelle (optional)
EVS_API_KEY=your-ehdsi-api-key

# EHDS Gazelle (optional)
EHDS_GAZELLE_API_KEY=your-ehds-api-key
```

### **Step 3: Start the Application**

```bash
docker-compose up -d
```

### **Step 4: Access the Application**

Open your browser: **http://localhost:8501**

---

## 📦 **Deployment Options**

### **Option 1: Docker Compose (Recommended)**

**Best for:** Quick deployment, local testing, development

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### **Option 2: Docker Run**

**Best for:** Simple single-container deployment

```bash
# Build image
docker build -t fhir-ips-validator:latest .

# Run container
docker run -d \
  --name fhir-validator \
  -p 8501:8501 \
  -e AZURE_FHIR_BASE_URL=your-fhir-service.fhir.azurehealthcareapis.com \
  -e AZURE_FHIR_CLIENT_ID=your-client-id \
  -e AZURE_FHIR_CLIENT_SECRET=your-secret \
  -e AZURE_FHIR_TENANT_ID=your-tenant-id \
  -e EVS_API_KEY=your-ehdsi-key \
  -e EHDS_GAZELLE_API_KEY=your-ehds-key \
  -v $(pwd)/examples:/app/examples:ro \
  fhir-ips-validator:latest

# View logs
docker logs -f fhir-validator

# Stop and remove
docker stop fhir-validator && docker rm fhir-validator
```

### **Option 3: Kubernetes**

**Best for:** Production, scalability, high availability

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fhir-validator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fhir-validator
  template:
    metadata:
      labels:
        app: fhir-validator
    spec:
      containers:
      - name: fhir-validator
        image: fhir-ips-validator:latest
        ports:
        - containerPort: 8501
        env:
        - name: AZURE_FHIR_BASE_URL
          valueFrom:
            secretKeyRef:
              name: fhir-secrets
              key: azure-fhir-base-url
        # ... more env vars from secrets
---
apiVersion: v1
kind: Service
metadata:
  name: fhir-validator-service
spec:
  selector:
    app: fhir-validator
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

---

## 🔒 **Security Best Practices**

### **1. Secrets Management**

**❌ Don't:**
- Hardcode credentials in Dockerfile
- Commit .env file to git
- Use demo/shared credentials in production

**✅ Do:**
- Use environment variables or secrets management
- Rotate API keys regularly (set reminders)
- Use separate credentials per environment (dev/staging/prod)

### **2. Network Security**

```yaml
# docker-compose.yml with reverse proxy
version: '3.8'
services:
  fhir-validator:
    # ... existing config
    expose:
      - "8501"  # Internal only
    networks:
      - internal
  
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - internal
    depends_on:
      - fhir-validator

networks:
  internal:
```

### **3. Container Security**

- ✅ App runs as non-root user (`streamlit:1000`)
- ✅ Multi-stage build reduces attack surface
- ✅ No unnecessary packages in final image
- ✅ Regular base image updates

---

## 📊 **Monitoring & Health Checks**

### **Built-in Health Check**

```bash
# Manual check
curl http://localhost:8501/_stcore/health

# Docker health status
docker inspect --format='{{.State.Health.Status}}' fhir-ips-validator
```

### **Log Monitoring**

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service errors
docker-compose logs fhir-validator | grep ERROR
```

---

## 🔧 **Configuration Options**

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |
| `API_TIMEOUT_SECONDS` | `60` | Validation API timeout |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### **Custom Examples**

Mount your own example files:

```yaml
# docker-compose.yml
volumes:
  - ./examples:/app/examples:ro
  - ./my-custom-examples:/app/custom-examples:ro
```

---

## 🐛 **Troubleshooting**

### **Issue: Container won't start**

```bash
# Check logs
docker-compose logs

# Common causes:
# - Port 8501 already in use
# - Invalid .env file format
# - Missing required dependencies
```

**Solution:**
```bash
# Use different port
# In docker-compose.yml:
ports:
  - "8080:8501"  # Host:8080 → Container:8501
```

### **Issue: "Authentication failed" errors**

**Solution:**
1. Verify API keys are correct in `.env`
2. Check key hasn't expired
3. Test keys manually:
   ```bash
   # Test Azure
   curl -X POST \
     https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token \
     -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&..."
   ```

### **Issue: Slow validation**

**Solution:**
- Increase API timeout: `API_TIMEOUT_SECONDS=120`
- Check network connectivity to validation services
- Consider caching frequently validated documents

### **Issue: High memory usage**

**Solution:**
```yaml
# docker-compose.yml
services:
  fhir-validator:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

---

## 🔄 **Updates & Maintenance**

### **Update to Latest Version**

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### **Backup & Restore**

No persistent data to backup (stateless application). Just keep your `.env` file secure.

### **Monitoring API Key Expiry**

App shows warnings 7 days before expiry. Rotate keys:

1. Generate new key on Gazelle platform
2. Update `.env` file
3. Restart: `docker-compose restart`

---

## 🌐 **Production Deployment Examples**

### **AWS ECS**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_URL
docker build -t fhir-validator .
docker tag fhir-validator:latest $ECR_URL/fhir-validator:latest
docker push $ECR_URL/fhir-validator:latest

# Deploy to ECS
aws ecs update-service \
  --cluster my-cluster \
  --service fhir-validator \
  --force-new-deployment
```

### **Azure Container Instances**

```bash
az container create \
  --resource-group my-rg \
  --name fhir-validator \
  --image fhir-validator:latest \
  --dns-name-label fhir-validator \
  --ports 8501 \
  --environment-variables \
    AZURE_FHIR_BASE_URL=$AZURE_FHIR_BASE_URL \
    EVS_API_KEY=$EVS_API_KEY \
    EHDS_GAZELLE_API_KEY=$EHDS_GAZELLE_API_KEY
```

### **Google Cloud Run**

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/my-project/fhir-validator

# Deploy
gcloud run deploy fhir-validator \
  --image gcr.io/my-project/fhir-validator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "AZURE_FHIR_BASE_URL=$AZURE_FHIR_BASE_URL"
```

---

## 📚 **Additional Resources**

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Azure FHIR Service](https://learn.microsoft.com/azure/healthcare-apis/fhir/)
- [Gazelle Platform Docs](https://gazelle.ehdsi.eu/gazelle-documentation/)

---

## 💬 **Support**

- 📖 [Main README](../README.md)
- 🐛 [Report Issues](https://github.com/ddeveloper72/fhir-ips-validator/issues)
- 💡 [Feature Requests](https://github.com/ddeveloper72/fhir-ips-validator/issues/new)

---

**Last Updated:** May 2026  
**Version:** 1.0.0
