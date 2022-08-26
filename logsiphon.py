from pathlib import Path

from PyPDF2 import PdfReader
import glob
import json
from datetime import datetime


def parse_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text


def update_siphon(log, siphon_log):
    updates = []

    last_updated = datetime.strptime(siphon_log['last_updated'], "%Y-%m-%d %H:%M:%S")
    log = log.replace('\"', '')
    log = log.split("\n")
    i = 4
    time = datetime.strptime(log[i], "%Y-%m-%d %H:%M:%S")

    while (time > last_updated):
        update = {
            "time": log[i],
            "player": log[i + 1],
            "type": log[i + 2],
            "amount": log[i + 3]
        }

        updates.append(update)

        time = datetime.strptime(log[i + 4], "%Y-%m-%d %H:%M:%S")
        i += 4

    for update in updates:
        if update['player'] in siphon_log['users']:
            siphon_log['users'][update['player']]['history'].append(update)
            siphon_log['users'][update['player']]['total_net_siphon'] += int(update['amount'])
            print("Updated " + update['player'] + ". New net siphon: " + str(
                siphon_log['users'][update['player']]['total_net_siphon']))
        if not update['player'] in siphon_log['users']:
            siphon_log['users'][update['player']] = {
                "total_net_siphon": 0,
                "history": []
            }
            siphon_log['users'][update['player']]['history'].append(update)
            siphon_log['users'][update['player']]['total_net_siphon'] += int(update['amount'])
            print("Updated " + update['player'] + ". New net siphon: " + str(
                siphon_log['users'][update['player']]['total_net_siphon']))

    siphon_log['last_updated'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return

def save_old_log(log):
    base = Path('logs')
    log_path = log['last_updated'].replace(' ', '-').replace(':', '')
    jsonpath = base / (log_path + ".json")
    with open(jsonpath, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=4)
    return

def save_log(log):
    with open('siphonlog.json', 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=4)
    return

def check_siphon(log):
    for user in log['users']:
        if log['users'][user]['total_net_siphon'] < 0:
            print("Player: " + user + " has a negative siphon balance of " + str(log['users'][user]['total_net_siphon']))

if __name__ == '__main__':
    pdf_paths = glob.glob("update/*.pdf")

    with open("siphonlog.json") as json_data_file:
        siphon_log = json.load(json_data_file)

    last_updated = datetime.strptime(siphon_log['last_updated'], "%Y-%m-%d %H:%M:%S")

    for pdf in pdf_paths:
        siphon_update = parse_pdf(pdf)
        save_old_log(siphon_log)
        update_siphon(siphon_update, siphon_log)
        save_log(siphon_log)

    check_siphon(siphon_log)
    print("Press Enter to exit")
    input()
    quit()