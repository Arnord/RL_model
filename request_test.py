import os
import json
import requests
import time
import torch
from flask import jsonify, request

import utils
import traceback


def get_state():
    state_dim = 9
    action_dim = 1
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    buffer_name = f"replay_buffer"
    replay_buffer = utils.ReplayBuffer(state_dim, action_dim, device)
    replay_buffer.load(f"./buffers/{buffer_name}_train")
    state, _, _, _, _ = replay_buffer.sample(batch_size=1)
    state = state.cpu().numpy().tolist()

    return state


def main():
    ip = 'localhost'
    port = 6010

    while True:
        try:
            state = get_state()
            state_json = json.dumps(state)
            resp = requests.post("http://{}:{}/planning".format(ip, str(port)), data={
                'state': state_json
            })
            action = resp.json()['planning_action']
            print('Planning - {}' .format(resp))
            print(action)
        except Exception as e:
            traceback.print_exc()
            print('Request Service break: ' + str(e))


if __name__ == '__main__':
    main()
