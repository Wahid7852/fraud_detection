const { spawn } = require('child_process');
const path = require('path');

// Colors for terminal output
const colors = {
    reset: "\x1b[0m",
    bright: "\x1b[1m",
    cyan: "\x1b[36m",
    magenta: "\x1b[35m",
    yellow: "\x1b[33m",
    red: "\x1b[31m"
};

function log(service, message, color) {
    const timestamp = new Date().toLocaleTimeString();
    process.stdout.write(`${color}[${timestamp}] [${service}] ${message}${colors.reset}\n`);
}

log("System", "Starting Fraud Detection Platform...", colors.bright + colors.yellow);

// Start Backend
const backend = spawn('uvicorn', ['app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'], {
    cwd: path.join(process.cwd(), 'backend'),
    shell: true
});

backend.stdout.on('data', (data) => {
    log("Backend", data.toString().trim(), colors.cyan);
});

backend.stderr.on('data', (data) => {
    log("Backend Error", data.toString().trim(), colors.red);
});

// Start Frontend
const frontend = spawn('npm', ['run', 'dev'], {
    cwd: path.join(process.cwd(), 'frontend'),
    shell: true
});

frontend.stdout.on('data', (data) => {
    log("Frontend", data.toString().trim(), colors.magenta);
});

frontend.stderr.on('data', (data) => {
    log("Frontend Error", data.toString().trim(), colors.red);
});

// Handle termination
process.on('SIGINT', () => {
    log("System", "Shutting down services...", colors.yellow);
    backend.kill();
    frontend.kill();
    process.exit();
});
