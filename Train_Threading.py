import threading
import torch
import os
import traceback
# import redis

import logging
logger = logging.getLogger('main')
import utils

from datetime import datetime
from flask import Flask, jsonify ,request
import json
import redis

app = Flask(__name__)

# 创建redis实例
red_obj = redis.Redis(host='dgx.server.ustb-ai3d.cn', port=6380, db=0)


trainer_info = {
    'policy': None,
    'device': None,
    'args': None,
    'replay_buffer': utils.ReplayBuffer()
}


def build_replay_buffer():
    state_dim = 9
    action_dim = 1
    # set_value = 65  # TODO:反归一化之后
    set_value = 0
    replay_buffer = utils.ReplayBuffer(state_dim, action_dim, device=trainer_info['device'])

    # state和next_state错位
    state = [json.loads(red_obj.lrange("state", 0, -1))
             for x in range(red_obj.llen("state"))][:-1]

    action = [json.loads(red_obj.lrange("action", 0, -1))
              for x in range(red_obj.llen("action"))][:-1]

    next_state = [json.loads(red_obj.lrange("state", 0, -1))
                  for x in range(red_obj.llen("state"))][1:]

    reward = - utils.MSE(next_state, set_value)

    done = 0

    buffer_size = min(len(state), len(action))
    for t in range(buffer_size):
        s = state[t]
        a = action[t]
        next_s = next_state[t]
        r = reward[t]
        d = done
        replay_buffer.add(s, a, next_s, r, d)

    buffer_name = "replay_buffer"
    time = datetime.time()
    replay_buffer.save(f"./buffers/{buffer_name}_{time}")

    return replay_buffer


@app.route('/training', methods=['POST'])
def training():
    if request.method == 'POST':

        global trainer_info
        logger.info('Main Service: Receive training request. Model updating...')
        # args.batch_size
        eval_freq = 5e3
        batch_size = 100

        policy = trainer_info['policy']
        replay_buffer = trainer_info['replay_buffer']

        if red_obj.llen("action") > 900 and red_obj.llen("state") > 900:
            replay_buffer = build_replay_buffer()

        pol_trains = policy.train(replay_buffer, iterations=int(eval_freq), batch_size=batch_size)
        torch.save(policy, os.path.join('./', 'best.pth'))  # TODO:路径需要修改，且需要添加模型备份功能
        logger.info('Main Service: Model training is over, model updated')


def service_start(config=None):
    # print(args)
    policy_path = "ckpt/BCQ/control.pkl"
    policy = torch.load(policy_path)
    trainer_info['policy'] = policy
    # policy = policy.to(device=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    trainer_info['device'] = device

    # TODO:测试用，需删除
    state_dim = 9
    action_dim = 1
    buffer_name = f"replay_buffer"
    replay_buffer = utils.ReplayBuffer(state_dim, action_dim, device)
    replay_buffer.load(f"./buffers/{buffer_name}_train")
    trainer_info['replay_buffer'] = replay_buffer

    app.run(
        host='0.0.0.0',
        port=config['flask_port'],
        debug=False
    )


class Train_Threading(threading.Thread):

    def __init__(self, Service, config=None):
        threading.Thread.__init__(self)
        self.trainer_id = config['trainer_id']
        self.trainer_name = config['name']
        self.Father_Service = Service
        self.RUNNING = True
        self.config = config
        self.th_id = int(config['th_id'])
        # self.time_range = None
        policy_path = "ckpt/BCQ/best.pth"
        self.policy = torch.load(policy_path)
        self.eval_freq = 5e3
        self.batch_size = 100
        # policy = policy.to(device=0)
        self.training_request = False

    def run(self):

        try:
            service_start(config=self.config)
            logger.debug('Main Service:' + 'Thickener-%s' % self.th_id + 'Train Service start')
        except Exception as e:
            traceback.print_exc()
            logger.warning('Main Service:' + 'Thickener-%s ' % self.th_id + 'Train Service break: ' + str(e))



