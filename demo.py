"""
=============================================================================
SENTINELS OF INTEGRITY — Demo CLI
Run this to see the project's output in action!
=============================================================================
"""

import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/api/v1/detect"

def print_report(data):
    print("\n" + "="*60)
    print("SENTINELS OF INTEGRITY - TRUST REPORT")
    print("="*60)
    print(f"Report ID:  {data['report_id']}")
    print(f"Platform:   {data['platform'].upper()}")
    print(f"Media Hash: {data['media_hash'][:24]}...")
    print("-" * 60)
    
    score = data['sentinels_score']
    verdict = data['verdict'].upper()
    
    # ANSI colors
    color_code = "32" # Green
    if verdict == "SUSPICIOUS": color_code = "33" # Yellow
    elif verdict == "SYNTHETIC": color_code = "31" # Red
    
    print(f"TRUST SCORE: \033[{color_code}m{score}/100\033[0m")
    print(f"VERDICT:     \033[{color_code}m{verdict}\033[0m")
    print("-" * 60)
    
    print("AI ANALYSIS (ML ENGINE)")
    ml = data['ml_result']
    print(f"  * Synthetic Confidence: {ml['confidence']:.1%}")
    print(f"  * Model Version:       {ml['model_version']}")
    if ml['artifacts']:
        print(f"  * Detected Artifacts:  {', '.join(ml['artifacts'])}")
    else:
        print("  * Detected Artifacts:  NONE (Clean)")
        
    print("\nPROVENANCE (BLOCKCHAIN)")
    bc = data['blockchain_result']
    if bc['is_registered']:
        print(f"  * Status:      REGISTERED [OK]")
        print(f"  * Author:      {bc['author']}")
        print(f"  * ZK-Verified: {bc['zk_verified']}")
    else:
        print(f"  * Status:      UNREGISTERED [NO]")
    
    print("="*60 + "\n")

def run_demo():
    scenarios = [
        {
            "name": "Authentic Video (YouTube)",
            "payload": {
                "media_hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                "media_url": "https://www.youtube.com/watch?v=authentic",
                "platform": "youtube"
            }
        },
        {
            "name": "Deepfake Detection (Twitter)",
            "payload": {
                "media_hash": "ff" * 32,
                "media_url": "https://x.com/user/status/deepfake",
                "platform": "twitter"
            }
        }
    ]

    print(">>> Starting Sentinels of Integrity Demo...")
    time.sleep(1)

    for scenario in scenarios:
        print(f"\n- Analyzing: {scenario['name']}...")
        try:
            response = requests.post(API_URL, json=scenario['payload'])
            if response.status_code == 200:
                print_report(response.json())
            else:
                print(f"X Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"X Connection Failed: Is the API running on port 8000? ({e})")
        time.sleep(2)

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('color')
    run_demo()
