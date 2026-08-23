import json
import random
import time
import uuid
import argparse
from datetime import datetime, timezone

import numpy as np
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os


load_dotenv()

NODE_ID = os.getenv("NODE_ID", f"node-{uuid.uuid4().hex[:6]}")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

TOPIC_TELEMETRY = f"sentineo/{NODE_ID}/telemetry"
TOPIC_STATUS = f"sentineo/{NODE_ID}/status"
TOPIC_EVENTS = f"sentineo/{NODE_ID}/events"


class SensorSimulator:
    """Responsavel por gerar valores simulados dos sensores e modos de ataque."""

    def __init__(self, node_id, attack_mode='normal'):
        self.node_id = node_id
        self.attack_mode = attack_mode
        self.attack_step = 0
        self.door_state = 'closed'
        self.door_timer = 0

        self.temp_base = 30.0
        self.humidity_base = 65.0
        self.energy_base = 200.0
        self.vibration_base = 0.05

    def set_attack_mode(self, mode):
        self.attack_mode = mode
        self.attack_step = 0
        self.door_state = 'closed'
        self.door_timer = 0

    def generate_telemetry(self):
        if self.attack_mode == 'normal':
            return self._generate_normal()
        elif self.attack_mode == 'temperature':
            return self._attack_temperature()
        elif self.attack_mode == 'energy':
            return self._attack_energy()
        elif self.attack_mode == 'vibration':
            return self._attack_vibration()
        elif self.attack_mode == 'door':
            return self._attack_door()
        elif self.attack_mode == 'random':
            return self._attack_random()
        else:
            return self._generate_normal()

    def _generate_normal(self):
        self.attack_step = 0
        temp = round(float(self.temp_base) + float(np.random.normal(0, 1.5)), 1)
        temp = max(20, min(40, temp))
        hum_val = float(self.humidity_base) + float(np.random.normal(0, 3))
        humidity = round(float(np.clip(hum_val, 30, 90)), 1)
        eng_val = float(self.energy_base) + float(np.random.normal(0, 15))
        energy = round(float(np.clip(eng_val, 50, 800)), 1)
        vib_val = float(self.vibration_base) + float(np.random.normal(0, 0.02))
        vibration = round(float(np.clip(vib_val, 0.01, 0.5)), 3)
        self.door_timer += 1
        if self.door_timer >= 20:
            self.door_timer = 0
            if random.random() < 0.05:
                self.door_state = 'open'
            else:
                self.door_state = 'closed'
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "energy": energy,
            "vibration": vibration,
            "door": self.door_state,
        }

    def _attack_temperature(self):
        self.attack_step += 1
        temp = round(30 + self.attack_step * 0.5, 1)
        temp = max(20, min(45, temp))
        humidity = round(float(np.clip(65 + np.random.normal(0, 3), 30, 90)), 1)
        energy = round(float(np.clip(200 + np.random.normal(0, 15), 50, 800)), 1)
        vibration = round(float(np.clip(0.05 + np.random.normal(0, 0.02), 0.01, 0.5)), 3)
        self.door_state = 'closed'
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "energy": energy,
            "vibration": vibration,
            "door": self.door_state,
        }

    def _attack_energy(self):
        self.attack_step += 1
        energy = round(200 + self.attack_step * 20, 1)
        energy = max(50, min(2000, energy))
        temp = round(30 + np.random.normal(0, 1.5), 1)
        temp = max(20, min(45, temp))
        hum_val = 65 + np.random.normal(0, 3)
        humidity = round(float(np.clip(hum_val, 30, 90)), 1)
        vibration = round(float(np.clip(0.05 + np.random.normal(0, 0.02), 0.01, 0.5)), 3)
        self.door_state = 'closed'
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "energy": energy,
            "vibration": vibration,
            "door": self.door_state,
        }

    def _attack_vibration(self):
        self.attack_step += 1
        vibration = round(float(np.clip(0.05 + self.attack_step * 0.02, 0.01, 2.0)), 3)
        temp = round(30 + np.random.normal(0, 1.5), 1)
        temp = max(20, min(45, temp))
        hum_val = 65 + np.random.normal(0, 3)
        humidity = round(float(np.clip(hum_val, 30, 90)), 1)
        energy = round(float(np.clip(200 + np.random.normal(0, 15), 50, 800)), 1)
        self.door_state = 'closed'
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "energy": energy,
            "vibration": vibration,
            "door": self.door_state,
        }

    def _attack_door(self):
        self.attack_step += 1
        self.door_state = 'open'
        temp = round(30 + np.random.normal(0, 1.5), 1)
        temp = max(20, min(45, temp))
        hum_val = 65 + np.random.normal(0, 3)
        humidity = round(float(np.clip(hum_val, 30, 90)), 1)
        energy = round(float(np.clip(200 + np.random.normal(0, 15), 50, 800)), 1)
        vibration = round(float(np.clip(0.05 + np.random.normal(0, 0.02), 0.01, 0.5)), 3)
        return {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": temp,
            "humidity": humidity,
            "energy": energy,
            "vibration": vibration,
            "door": self.door_state,
        }

    def _attack_random(self):
        modes = ['temperature', 'energy', 'vibration', 'door']
        chosen = random.choice(modes)
        return getattr(self, '_attack_' + chosen)()


class RulesEngine:
    """Responsavel por analisar a telemetria e determinar status/eventos."""

    def __init__(self):
        self.temp_warning = 35.0
        self.temp_critical = 40.0
        self.energy_warning = 800.0
        self.energy_critical = 1500.0
        self.vibration_warning = 0.5
        self.vibration_critical = 1.0

    def classify(self, telemetry):
        events = []
        temperature = telemetry.get('temperature', 0)
        energy = telemetry.get('energy', 0)
        vibration = telemetry.get('vibration', 0)
        door = telemetry.get('door', 'closed')

        if temperature >= self.temp_critical:
            events.append({
                'event_type': 'temperature_critical',
                'severity': 'critical',
                'message': 'Temperatura critica'
            })
        elif temperature >= self.temp_warning:
            events.append({
                'event_type': 'temperature_high',
                'severity': 'warning',
                'message': 'Temperatura acima do limite'
            })

        if energy >= self.energy_critical:
            events.append({
                'event_type': 'energy_critical',
                'severity': 'critical',
                'message': 'Consumo critico'
            })
        elif energy >= self.energy_warning:
            events.append({
                'event_type': 'energy_high',
                'severity': 'warning',
                'message': 'Consumo alto'
            })

        if vibration >= self.vibration_critical:
            events.append({
                'event_type': 'vibration_critical',
                'severity': 'critical',
                'message': 'Vibracao critica'
            })
        elif vibration >= self.vibration_warning:
            events.append({
                'event_type': 'vibration_high',
                'severity': 'warning',
                'message': 'Vibracao alta'
            })

        if door == 'open':
            events.append({
                'event_type': 'door_open',
                'severity': 'warning',
                'message': 'Porta aberta'
            })

        has_critical = any(e['severity'] == 'critical' for e in events)
        has_warning = any(e['severity'] == 'warning' for e in events)

        if has_critical:
            status = 'critical'
        elif has_warning:
            status = 'warning'
        else:
            status = 'online'

        if not events:
            return status, None

        severity_order = {'critical': 3, 'warning': 2}
        primary = max(events, key=lambda e: severity_order.get(e['severity'], 1))

        event = {
            'event_id': 'evt-' + uuid.uuid4().hex[:6],
            'node_id': telemetry.get('node_id', 'node-001'),
            'timestamp': telemetry.get('timestamp', datetime.now(timezone.utc).isoformat()),
            'event_type': primary['event_type'],
            'severity': primary['severity'],
            'message': primary['message'],
        }

        return status, event


class SentiNeoNode:
    """Responsavel por orquestrar o no SentiNeo completo."""

    def __init__(self, attack_mode='normal'):
        self.attack_mode = attack_mode
        self.node_id = NODE_ID
        self.mqtt_host = MQTT_HOST
        self.mqtt_port = MQTT_PORT

        self.sensor = SensorSimulator(self.node_id, self.attack_mode)
        self.rules = RulesEngine()

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.node_id
        )
        self.connected = False

        self.topic_telemetry = TOPIC_TELEMETRY
        self.topic_status = TOPIC_STATUS
        self.topic_events = TOPIC_EVENTS

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print("[MQTT] Reconnected")
        else:
            print("[MQTT] Connection failed with code " + str(rc))
            self.connected = False

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        print("[MQTT] Connection lost")
        try:
            self.client.reconnect()
        except Exception:
            print("[MQTT] Attempting reconnect...")

    def _on_publish(self, client, userdata, mid, *args):
        pass

    def connect_mqtt(self):
        try:
            self.client.connect(self.mqtt_host, self.mqtt_port)
            self.client.loop_start()
        except Exception as e:
            print("[MQTT] Failed to connect: " + str(e))

    def disconnect_mqtt(self):
        self.connected = False
        self.client.loop_stop()
        try:
            self.client.disconnect()
        except Exception:
            pass

    def publish_telemetry(self, payload):
        if not self.connected:
            return
        try:
            result = self.client.publish(
                self.topic_telemetry,
                json.dumps(payload),
                qos=1
            )
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
        except Exception:
            pass
        return False

    def publish_status(self, status):
        if not self.connected:
            return
        try:
            payload = {
                "node_id": self.node_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
            }
            result = self.client.publish(
                self.topic_status,
                json.dumps(payload),
                qos=1
            )
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print("[MQTT] Failed to publish status")
        except Exception:
            pass

    def publish_event(self, event):
        if not self.connected:
            return
        try:
            payload = {
                "event_id": event.get('event_id', 'evt-' + uuid.uuid4().hex[:6]),
                "node_id": event.get('node_id', self.node_id),
                "timestamp": event.get('timestamp', datetime.now(timezone.utc).isoformat()),
                "event_type": event.get('event_type', 'sensor_anomaly'),
                "severity": event.get('severity', 'info'),
                "message": event.get('message', 'Evento do sistema'),
            }
            result = self.client.publish(
                self.topic_events,
                json.dumps(payload),
                qos=1
            )
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print("[MQTT] Failed to publish event")
        except Exception:
            pass

    def _format_telemetry_log(self, telemetry, status):
        print("[TX] T=" + str(telemetry['temperature']) + "C H=" + str(telemetry['humidity']) + "% E=" + str(telemetry['energy']) + "W V=" + str(telemetry['vibration']) + "g DOOR=" + telemetry['door'].upper() + " STATUS=" + status)

    def _format_event_log(self, event):
        icons = {'info': 'informational', 'warning': 'warning', 'critical': 'critical'}
        print("[EVENT] " + event['event_type'])
        print("[EVENT] severity=" + event['severity'])

    def run(self):
        print("[SentiNeo] Node: " + self.node_id)
        print("[SentiNeo] MQTT: " + self.mqtt_host + ":" + str(self.mqtt_port))
        print("[SentiNeo] Topic: " + self.topic_telemetry)
        if self.attack_mode != 'normal':
            print("[SentiNeo] Mode: ATK-" + self.attack_mode.upper())
        else:
            print("[SentiNeo] Mode: NORMAL")

        self.connect_mqtt()

        try:
            while True:
                telemetry = self.sensor.generate_telemetry()
                status, event = self.rules.classify(telemetry)
                self.publish_telemetry(telemetry)
                self.publish_status(status)
                if event:
                    self.publish_event(event)
                self._format_telemetry_log(telemetry, status)
                if event:
                    self._format_event_log(event)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n[SentiNeo] Node desligando...")
        finally:
            self.disconnect_mqtt()


def main():
    parser = argparse.ArgumentParser(description="SentiNeo Node Simulator")
    parser.add_argument(
        '--attack',
        choices=['normal', 'temperature', 'energy', 'vibration', 'door', 'random'],
        default='normal',
        help='Modo de simulacao (default: normal)'
    )
    args = parser.parse_args()
    node = SentiNeoNode(attack_mode=args.attack)
    if args.attack != 'normal':
        print("[SentiNeo] Attack mode: " + args.attack)
    node.run()


if __name__ == "__main__":
    main()
