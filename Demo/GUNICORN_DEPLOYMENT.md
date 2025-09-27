# Gunicorn Deployment Guide

## 📋 Overview

This guide provides complete instructions for deploying the AI Research Proposal Evaluation System using Gunicorn WSGI server for production environments.

## 🗂️ Files Added/Modified

### New Files Created:
- `wsgi.py` - WSGI entry point for Gunicorn
- `gunicorn.conf.py` - Production-ready Gunicorn configuration
- `start_gunicorn.sh` - Automated startup script
- `test_gunicorn.py` - Configuration testing script`

### Modified Files:
- `requirements.txt` - Added gunicorn==21.2.0
- `README.md` - Added comprehensive Gunicorn deployment section

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Configuration
```bash
python test_gunicorn.py
```

### 3. Start Server
```bash
# Option 1: Using startup script (recommended)
./start_gunicorn.sh

# Option 2: Direct gunicorn command
gunicorn --config gunicorn.conf.py wsgi:app
```

## ⚙️ Configuration Details

### Gunicorn Settings (`gunicorn.conf.py`)
- **Workers**: `CPU_COUNT * 2 + 1` (auto-scaling)
- **Timeout**: 300 seconds (for long AI evaluations)
- **Memory Management**: Auto-restart workers after 1000 requests
- **Logging**: Structured logs in `logs/` directory
- **Security**: Production-ready settings

### WSGI Entry Point (`wsgi.py`)
- Clean import structure
- Path management for deployment
- Flask app initialization

## 📊 Performance Features

### Automatic Scaling
- Worker count scales with CPU cores
- Memory leak prevention with worker recycling
- Graceful timeout handling

### Logging & Monitoring
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`
- Process ID: `logs/gunicorn.pid`

### Security
- Production environment variables
- Secure worker configuration
- SSL support ready

## 🔧 Advanced Deployment

### Systemd Service
For production servers, create a systemd service:

```bash
sudo nano /etc/systemd/system/idea2proposal.service
```

Add the service configuration from README.md, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable idea2proposal
sudo systemctl start idea2proposal
```

### SSL Configuration
Uncomment SSL settings in `gunicorn.conf.py`:
```python
keyfile = 'path/to/keyfile'
certfile = 'path/to/certfile'
```

### Load Balancing
For high-traffic deployments, use a reverse proxy:
- Nginx (recommended)
- Apache
- CloudFlare

## 🧪 Testing

### Configuration Test
```bash
python test_gunicorn.py
```

### Manual Testing
```bash
# Start server
./start_gunicorn.sh

# Test endpoint (in another terminal)
curl http://localhost:4090
```

## 📈 Monitoring

### Log Files
- `logs/access.log` - HTTP access logs
- `logs/error.log` - Application errors
- `logs/gunicorn.pid` - Process ID

### Health Checks
```bash
# Check if running
ps aux | grep gunicorn

# Check logs
tail -f logs/access.log
tail -f logs/error.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port 4090
   lsof -i :4090
   # Kill process
   kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   chmod +x start_gunicorn.sh
   chmod +x test_gunicorn.py
   ```

3. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration errors**
   ```bash
   python test_gunicorn.py
   ```

### Performance Tuning

1. **Adjust workers** in `gunicorn.conf.py`:
   ```python
   workers = 4  # Fixed number instead of auto-scaling
   ```

2. **Memory optimization**:
   ```python
   max_requests = 500  # Lower for memory-constrained environments
   ```

3. **Timeout adjustment**:
   ```python
   timeout = 600  # Increase for very long AI evaluations
   ```

## 📝 Notes

- The configuration is optimized for AI workloads with long processing times
- Worker recycling prevents memory leaks during extended use
- Logs are automatically rotated and managed
- SSL support is ready but requires certificate files
- Systemd service provides automatic restart on failure

## 🎯 Production Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Configuration tested (`python test_gunicorn.py`)
- [ ] Logs directory created (`mkdir -p logs`)
- [ ] SSL certificates configured (if using HTTPS)
- [ ] Systemd service configured (optional)
- [ ] Reverse proxy configured (optional)
- [ ] Monitoring setup (optional)

## 🆘 Support

If you encounter issues:

1. Run the test script: `python test_gunicorn.py`
2. Check logs: `tail -f logs/error.log`
3. Verify configuration: `gunicorn --check-config --config gunicorn.conf.py wsgi:app`
4. Check system resources: `htop` or `top`
