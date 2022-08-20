import threading
import numpy as np
import torch
import traceback
# import redis

import logging
logger = logging.getLogger('main')
import utils

from flask import Flask, jsonify, request
import json
import BCQ
import redis

app = Flask(__name__)

# 创建redis实例
red_obj = redis.Redis(host='dgx.server.ustb-ai3d.cn', port=6380, db=0)


planner_info = {
    'policy': None,
    'device': None,
    'args': None,
    'replay_buffer': utils.ReplayBuffer(),
    'scale': None
}
# global planner_info


@app.route('/planning', methods=['POST'])
def planning():
    if request.method == 'POST':

        global planner_info
        logger.info('Main Service: Receive planning request. Planning action...')

        re_state = json.loads(request.form['state'])
        re_state = torch.Tensor(re_state).to(device=planner_info['device'])
        # print(re_state)

        # state = flask_post['state'] # TODO:需要归一化和反归一化
        policy = planner_info['policy']
        replay_buffer = planner_info['replay_buffer']

        state, _, _, _, _ = replay_buffer.sample(batch_size=1)
        state = re_state.cpu().numpy()
        action = policy.select_action(state)
        print(action)

        # TODO：暂时储存两个表，一个作为历史数据，一个作为经验回访池（）
        red_obj.lpush("action", json.dumps(action.tolist()))
        red_obj.lpush("state", json.dumps(state.tolist()))

        # 回放池超过存储容量，解放尾部数据
        if red_obj.llen("action") > 1000 and red_obj.llen("state") > 1000:        # buffer_size
            red_obj.rpop("action")
            red_obj.rpop("state")

        logger.info('Main Service: Action planning over, send the new action.')

        response_dict = {
            'planning_action': action.tolist()
        }

        return jsonify(response_dict)


def service_start(config=None):
    # print(args)
    policy_path = "ckpt/BCQ/control.pkl"
    policy = torch.load(policy_path)
    planner_info['policy'] = policy
    # policy = policy.to(device=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    planner_info['device'] = device

    # TODO:测试用，需删除
    state_dim = 9
    action_dim = 1
    buffer_name = f"replay_buffer"
    replay_buffer = utils.ReplayBuffer(state_dim, action_dim, device)
    replay_buffer.load(f"./buffers/{buffer_name}_train")
    planner_info['replay_buffer'] = replay_buffer

    # TODO:service_start时应该需要清空经验回放池，调试时暂时不清空
    # red_list = ["action", "state", "reward", "done"]
    # for i in red_list:
    #     red_obj.delete(i)

    app.run(
        host='0.0.0.0',
        port=config['flask_port'],
        debug=False
    )


class Plan_Threading(threading.Thread):

    def __init__(self, Service, config=None):
        threading.Thread.__init__(self)
        self.planner_id = config['planner_id']
        self.planner_name = config['name']
        self.Father_Service = Service
        self.RUNNING = True
        self.config = config
        self.th_id = int(config['th_id'])
        # self.time_range = None

    def run(self):

        try:
            service_start(config=self.config)
            logger.debug('Main Service:' + 'Thickener-%s' % self.th_id + 'Plan Service start')
        except Exception as e:
            traceback.print_exc()
            logger.warning('Main Service:' + 'Thickener-%s ' % self.th_id + 'Plan Service break: ' + str(e))

