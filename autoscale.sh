#!/bin/bash

# Shell color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to log messages with timestamp and color
log() {
    local level=$1
    local message=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    case $level in
        "INFO")
            echo -e "${GREEN}[${timestamp}] INFO: ${message}${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] WARNING: ${message}${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] ERROR: ${message}${NC}"
            ;;
        "SUCCESS")
            echo -e "${CYAN}[${timestamp}] SUCCESS: ${message}${NC}"
            ;;
        "COMMAND")
            echo -e "${BLUE}[${timestamp}] COMMAND: ${message}${NC}"
            ;;
        "HEADER")
            echo -e "${MAGENTA}${message}${NC}"
            ;;
        *)
            echo -e "[${timestamp}] ${level}: ${message}"
            ;;
    esac
}

# Print script header
log "HEADER" "======================================================"
log "HEADER" "             GCP AUTOSCALING DEPLOYMENT               "
log "HEADER" "======================================================"

# Configuration
GCP_ZONE="us-central1-a"
LOCAL_DATA_PATH="$HOME/local/data"  
REMOTE_DATA_PATH="$HOME" 
GCP_USER="vboxuser"  
CPU_THRESHOLD=75
APP_DIR="myapp"
PORT="8080"

log "INFO" "Starting GCP automation script"
log "INFO" "Configuration:"
log "INFO" "  - GCP Zone: $GCP_ZONE"
log "INFO" "  - Local Data Path: $LOCAL_DATA_PATH"
log "INFO" "  - Remote Data Path: $REMOTE_DATA_PATH"
log "INFO" "  - GCP User: $GCP_USER"
log "INFO" "  - CPU Threshold: $CPU_THRESHOLD%"
log "INFO" "  - App Directory: $APP_DIR"
log "INFO" "  - Port: $PORT"

# Authenticate with GCP
log "INFO" "Authenticating with GCP..."
log "COMMAND" "gcloud auth activate-service-account --key-file=as3-g24ai1115-e07b4f7cb21b.json"
if gcloud auth activate-service-account --key-file=as3-g24ai1115-e07b4f7cb21b.json; then
    log "SUCCESS" "Authentication successful"
else
    log "ERROR" "Authentication failed!"
    exit 1
fi

log "COMMAND" "gcloud config set project assignment3-453515"
gcloud config set project assignment3-453515
log "SUCCESS" "Project set to assignment3-453515"

# Get CPU Usage
log "INFO" "Getting current CPU usage..."
CPU_USAGE=$(top -bn 1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
log "INFO" "Current CPU Usage: $CPU_USAGE%"

# Check if the VM exists in GCP
log "INFO" "Checking if VM exists in GCP..."
log "COMMAND" "gcloud compute instance-groups managed list-instances scaled-vm-group --zone us-central1-a"
INSTANCE_NAME=$(gcloud compute instance-groups managed list-instances scaled-vm-group --zone us-central1-a --format="value(name)" 2>/dev/null | head -n 1)

if [ -n "$INSTANCE_NAME" ]; then
    log "INFO" "Found existing VM: $INSTANCE_NAME"
else
    log "INFO" "No existing VM found"
fi

# If CPU usage exceeds threshold and VM does not exist, create a new VM
if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    if [ -z "$INSTANCE_NAME" ]; then
        log "WARNING" "CPU usage exceeded $CPU_THRESHOLD%. Creating a new VM in GCP..."

        log "COMMAND" "Creating instance template: scaled-vm-template"
        if gcloud compute instance-templates create scaled-vm-template \
            --image-family ubuntu-2204-lts \
            --image-project ubuntu-os-cloud \
            --machine-type e2-medium \
            --boot-disk-size 10GB \
            --tags http-server,https-server; then
            log "SUCCESS" "Instance template created successfully"
        else
            log "ERROR" "Failed to create instance template"
            exit 1
        fi

        log "COMMAND" "Creating managed instance group: scaled-vm-group"
        if gcloud compute instance-groups managed create scaled-vm-group \
            --base-instance-name scaled-vm \
            --template scaled-vm-template \
            --size 1 \
            --zone us-central1-a; then
            log "SUCCESS" "Managed instance group created successfully"
        else
            log "ERROR" "Failed to create managed instance group"
            exit 1
        fi

        log "COMMAND" "Setting autoscaling for scaled-vm-group"
        if gcloud compute instance-groups managed set-autoscaling scaled-vm-group \
            --max-num-replicas 5 \
            --min-num-replicas 1 \
            --target-cpu-utilization 0.75 \
            --cool-down-period 60 \
            --zone us-central1-a; then
            log "SUCCESS" "Autoscaling set successfully"
        else
            log "ERROR" "Failed to set autoscaling"
            exit 1
        fi
        
        log "INFO" "Getting VM name..."
        GCP_VM_NAME=$(gcloud compute instance-groups managed list-instances scaled-vm-group --zone us-central1-a --format="value(name)" | head -n 1)
        log "INFO" "VM created: $GCP_VM_NAME"
        
        log "INFO" "Waiting for the VM to be ready... (30s)"
        for i in {1..30}; do
            echo -ne "${YELLOW}.${NC}"
            sleep 1
        done
        echo ""
        log "SUCCESS" "VM should be ready now"
        
        log "INFO" "Transferring data to GCP VM..."
        log "COMMAND" "gcloud compute scp --recurse \"$LOCAL_DATA_PATH\" \"$GCP_USER@$GCP_VM_NAME:$REMOTE_DATA_PATH\" --zone=\"$GCP_ZONE\""
        if gcloud compute scp --recurse "$LOCAL_DATA_PATH" "$GCP_USER@$GCP_VM_NAME:$REMOTE_DATA_PATH" --zone="$GCP_ZONE"; then
            log "SUCCESS" "Data transfer completed successfully"
        else
            log "WARNING" "Data transfer may have had issues"
        fi
            
        # Deploy the Simple Flask API
        log "INFO" "Deploying the Flask API..."
        
        # SSH into the VM and run the setup commands
        log "COMMAND" "SSH into VM and run setup commands"
        log "INFO" "Connecting to VM and installing dependencies..."
        
        if gcloud compute ssh $GCP_VM_NAME --zone $GCP_ZONE --command "
          echo '${YELLOW}[REMOTE] Starting setup on VM...${NC}'
          
          echo '${YELLOW}[REMOTE] Updating package lists...${NC}'
          sudo apt update
          
          echo '${YELLOW}[REMOTE] Installing dependencies...${NC}'
          sudo apt install -y python3 python3-pip nginx python3-venv
          
          echo '${YELLOW}[REMOTE] Creating application directory...${NC}'
          mkdir -p /home/$USER/$APP_DIR
          cd /home/$USER/$APP_DIR
          
          echo '${YELLOW}[REMOTE] Setting up Python virtual environment...${NC}'
          python3 -m venv venv
          source venv/bin/activate
          
          echo '${YELLOW}[REMOTE] Installing Flask and Gunicorn...${NC}'
          pip install flask gunicorn
          
          echo '${YELLOW}[REMOTE] Creating Flask application...${NC}'
          echo \"from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=$PORT)\" > app.py
          
          echo '${YELLOW}[REMOTE] Creating systemd service...${NC}'
          echo \"[Unit]
Description=Flask API Service
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/$APP_DIR
ExecStart=/home/$USER/$APP_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:$PORT app:app
Restart=always

[Install]
WantedBy=multi-user.target\" | sudo tee /etc/systemd/system/flask-api.service
          
          echo '${YELLOW}[REMOTE] Enabling and starting service...${NC}'
          sudo systemctl enable flask-api.service
          sudo systemctl start flask-api.service
          
          echo '${YELLOW}[REMOTE] Configuring Nginx...${NC}'
          sudo rm -f /etc/nginx/sites-enabled/default
          echo 'server {
            listen 80;
            server_name _;
            location / {
            proxy_pass http://localhost:$PORT;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection \"upgrade\";
            proxy_set_header Host \$host;
            proxy_cache_bypass \$http_upgrade;
            }
          }' | sudo tee /etc/nginx/sites-available/flask-app
          
          sudo ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
          
          echo '${YELLOW}[REMOTE] Restarting Nginx...${NC}'
          sudo systemctl restart nginx
          
          echo '${YELLOW}[REMOTE] Checking service status...${NC}'
          sudo systemctl status flask-api.service | head -n 10
          
          echo '${YELLOW}[REMOTE] Testing API response...${NC}'
          curl -s http://localhost:$PORT/ || echo \"API not responding\"
          
          echo '${GREEN}[REMOTE] Setup completed on VM${NC}'
        "; then
            log "SUCCESS" "Flask API setup completed on $GCP_VM_NAME"
        else
            log "ERROR" "Failed to set up Flask API on VM"
        fi
        
        # Get external IP for user reference
        log "INFO" "Retrieving external IP address..."
        EXTERNAL_IP=$(gcloud compute instances describe $GCP_VM_NAME --zone=$GCP_ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
        log "SUCCESS" "Flask API deployed and running on $GCP_VM_NAME"
        log "INFO" "You can access the API at: http://$EXTERNAL_IP/"
        
        # Test Auto-Scaling by Stressing the CPU
        log "INFO" "Testing auto-scaling by generating load (this may take some time)..."
        if gcloud compute ssh $GCP_VM_NAME --zone $GCP_ZONE --command "
          echo '${YELLOW}[REMOTE] Installing Apache Benchmark...${NC}'
          sudo apt install -y apache2-utils
          
          echo '${YELLOW}[REMOTE] Running load test...${NC}'
          ab -n 1000 -c 100 http://localhost:$PORT/
          
          echo '${GREEN}[REMOTE] Load test completed${NC}'
        "; then
            log "SUCCESS" "Auto-scaling test completed"
        else
            log "WARNING" "Auto-scaling test may have had issues"
        fi
        
        log "SUCCESS" "Automation Completed Successfully!"
        log "INFO" "API URL: http://$EXTERNAL_IP/"
            
    else
        log "INFO" "GCP VM already exists. Skipping creation."
        log "INFO" "Existing VM: $INSTANCE_NAME"
    fi

# If CPU usage drops below threshold and VM exists, shut down the VM
elif (( $(echo "$CPU_USAGE < $CPU_THRESHOLD" | bc -l) )); then
    if [ -n "$INSTANCE_NAME" ]; then
        log "WARNING" "CPU usage dropped below $CPU_THRESHOLD%. Shutting down GCP VM..."
        log "COMMAND" "gcloud compute instance-groups managed delete scaled-vm-group --zone us-central1-a"
        
        if gcloud compute instance-groups managed delete scaled-vm-group --zone us-central1-a --quiet; then
            log "SUCCESS" "VM group deleted successfully"
        else
            log "ERROR" "Failed to delete VM group"
        fi
    else
        log "INFO" "No active GCP VM to shut down."
    fi
fi

log "HEADER" "======================================================"
log "HEADER" "                 SCRIPT COMPLETED                     "
log "HEADER" "======================================================"
