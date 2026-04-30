from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import random
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cacc-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*")

active_attack = None
attack_thread = None
attack_history = []
current_logs = []

ATTACKS_INFO = {
    'dos': {'name': 'SYN FLOOD', 'icon': '💣', 'cve': 'CVE-2024-6387', 'type': 'Denial of Service'},
    'ddos': {'name': 'BOTNET DDoS', 'icon': '🌊', 'cve': 'CVE-2024-3400', 'type': 'Distributed DoS'},
    'mitm': {'name': 'MITM', 'icon': '👤', 'cve': 'CVE-2024-4762', 'type': 'Intercettazione'},
    'ip_spoofing': {'name': 'IP SPOOFING', 'icon': '🎭', 'cve': 'CVE-2024-2875', 'type': 'Masquerading'},
    'teardrop': {'name': 'TEARDROP', 'icon': '💥', 'cve': 'CVE-1999-0016', 'type': 'Buffer Overflow'},
    'ransomware': {'name': 'RANSOMWARE', 'icon': '🔒', 'cve': 'CVE-2024-38077', 'type': 'Malware/Ransomware'},
    'worm': {'name': 'WORM', 'icon': '🕸️', 'cve': 'CVE-2008-4250', 'type': 'Malware/Worm'},
    'botnet': {'name': 'BOTNET C2', 'icon': '🤖', 'cve': 'CVE-2016-10174', 'type': 'Botnet'}
}

LATEST_CVES = [
    {'cve': 'CVE-2025-1038', 'name': 'Nginx HTTP/2 Rapid Reset', 'cvss': 8.6},
    {'cve': 'CVE-2025-0696', 'name': 'CloudFlare WAF Bypass', 'cvss': 7.8},
    {'cve': 'CVE-2024-6387', 'name': 'OpenSSH regreSSHion', 'cvss': 8.1},
    {'cve': 'CVE-2024-38077', 'name': 'LockBit 4.0 RCE', 'cvss': 9.8},
    {'cve': 'CVE-2024-3400', 'name': 'Palo Alto PAN-OS DDoS', 'cvss': 9.8}
]


def add_log(message):
    global current_logs
    timestamp = datetime.now().isoformat()
    current_logs.append({'timestamp': timestamp, 'message': message})
    if len(current_logs) > 50:
        current_logs = current_logs[-50:]


def run_attack_simulation(attack_id, duration=60):
    global active_attack, attack_history, current_logs
    attack_info = ATTACKS_INFO[attack_id]

    add_log(f"🚨 {attack_info['name']} attack started | CVE: {attack_info['cve']}")
    socketio.emit('attack_update', {
        'attack': attack_info['name'],
        'type': attack_info['type'],
        'metrics': {},
        'logs': current_logs[-5:],
        'cve_id': attack_info['cve']
    })

    metrics_history = []

    for step in range(duration):
        if active_attack != attack_id:
            break

        if attack_id == 'dos':
            packet_rate = min(1000000, step * 50000)
            server_load = min(100, step * 5)
            backlog = min(10000, step * 500)
            metrics = {'packet_rate': packet_rate, 'server_load': server_load, 'backlog': backlog}
            if step == 20:
                add_log(f"⚠️ Server load at {server_load}% - Backlog: {backlog}")
            elif step == 40:
                add_log(f"💀 CRITICAL: Server unresponsive! SYN queue exhausted.")

        elif attack_id == 'ddos':
            bot_count = int(100000 / (1 + math.exp(-0.3 * (step - 15)))) if step < 30 else 100000
            attack_intensity = min(100, bot_count / 1000)
            bandwidth = bot_count * 0.1
            metrics = {'bot_count': bot_count, 'attack_intensity': attack_intensity, 'bandwidth': bandwidth}
            if step == 30:
                add_log(f"🔥 Botnet reached {bot_count} bots! Full-scale DDoS engaged.")
            elif step % 15 == 0 and step > 0:
                add_log(f"🌊 Bandwidth saturation: {bandwidth / 1000:.1f} Gbps")

        elif attack_id == 'mitm':
            packets_intercepted = step * random.randint(50, 150)
            credentials_captured = int(step * random.uniform(0.5, 2))
            metrics = {'packets_intercepted': packets_intercepted, 'credentials_captured': credentials_captured}
            if step == 25:
                add_log(f"🔐 SESSION HIJACKED: Authentication tokens captured!")
            elif step % 10 == 0 and step > 0:
                add_log(f"📡 Intercepted {packets_intercepted} packets, {credentials_captured} credentials")

        elif attack_id == 'ip_spoofing':
            spoof_rate = min(80, step * 5) if step < 15 else 80
            spoofed_packets = int((1000 + step * 100) * spoof_rate / 100)
            metrics = {'spoof_rate': spoof_rate, 'spoofed_packets': spoofed_packets}
            if step == 15:
                add_log(f"🎭 IP Spoofing engaged: {spoof_rate}% packets spoofed")

        elif attack_id == 'teardrop':
            fragments_sent = step * 100
            overlapping_fragments = int(50 * (1 - math.exp(-step / 10)))
            metrics = {'fragments_sent': fragments_sent, 'overlapping_fragments': overlapping_fragments}
            if step >= 25:
                add_log(f"💥 CRITICAL: Target system CRASHED due to buffer overflow!")
                metrics['system_crashed'] = True

        elif attack_id == 'ransomware':
            encryption_speed = step * 10 if step < 10 else 100
            files_encrypted = min(10000, encryption_speed * step)
            progress = (files_encrypted / 10000) * 100
            metrics = {'files_encrypted': files_encrypted, 'progress': progress}
            if progress >= 25 and progress < 30:
                add_log(f"🔒 {progress:.0f}% files encrypted. Ransom note dropped!")
            elif progress >= 50 and progress < 55:
                add_log(f"💰 Ransomware: Pay $50,000 within 48h (BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa)")

        elif attack_id == 'worm':
            if step < 20:
                infected_hosts = int(10000 * (1 - math.exp(-0.3 * step)))
            else:
                infected_hosts = min(10000, infected_hosts + 300)
            infection_rate = (infected_hosts / 10000) * 100
            metrics = {'infected_hosts': infected_hosts, 'infection_rate': infection_rate}
            if infection_rate >= 50:
                add_log(f"🕸️ CRITICAL: Worm infected 50% of network ({infected_hosts} hosts)")

        elif attack_id == 'botnet':
            if step < 20:
                bot_count = int(150000 * (1 - math.exp(-step / 5)))
            else:
                bot_count = 150000
            c2_traffic = bot_count // 50
            metrics = {'bot_count': bot_count, 'c2_traffic': c2_traffic}
            if random.random() < 0.2:
                commands = ['scan_ports', 'exfil_data', 'ddos_target']
                add_log(f"🤖 C2 → BOTNET: New command '{random.choice(commands)}' sent to {bot_count} bots")

        metrics_history.append(metrics)
        socketio.emit('attack_update', {
            'attack': attack_info['name'],
            'type': attack_info['type'],
            'metrics': metrics,
            'logs': current_logs[-3:],
            'step': step,
            'cve_id': attack_info['cve']
        })
        time.sleep(1)

    if active_attack == attack_id:
        active_attack = None
        add_log(f"✅ {attack_info['name']} attack completed. Duration: {duration}s")
        attack_history.insert(0, {
            'time': datetime.now().strftime('%H:%M:%S'),
            'name': attack_info['name'],
            'cve': attack_info['cve'],
            'duration': f'{duration}s'
        })
        socketio.emit('attack_complete', {'attack': attack_info['name']})


@app.route('/')
def index():
    attacks = [{'id': k, 'name': v['name'], 'icon': v['icon'], 'cve': v['cve']} for k, v in ATTACKS_INFO.items()]
    return render_template('index.html',
                           attacks=attacks,
                           latest_cves=LATEST_CVES,
                           history=attack_history[:10])


@app.route('/attack/start/<attack_id>', methods=['POST'])
def start_attack(attack_id):
    global active_attack, attack_thread
    if active_attack:
        return redirect(url_for('index'))
    if attack_id not in ATTACKS_INFO:
        return redirect(url_for('index'))

    active_attack = attack_id
    attack_thread = threading.Thread(target=run_attack_simulation, args=(attack_id, 60))
    attack_thread.start()
    return redirect(url_for('index'))


@app.route('/attack/stop', methods=['POST'])
def stop_attack():
    global active_attack
    if active_attack:
        attack_name = ATTACKS_INFO[active_attack]['name']
        active_attack = None
        add_log(f"⏹️ {attack_name} attack stopped manually")
    return redirect(url_for('index'))


@app.route('/api/status')
def status():
    return {
        'active': active_attack is not None,
        'attack': ATTACKS_INFO[active_attack]['name'] if active_attack else None,
        'cve': ATTACKS_INFO[active_attack]['cve'] if active_attack else None
    }


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)