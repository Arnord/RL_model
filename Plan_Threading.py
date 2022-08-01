import threading
import numpy as np
import torch
import traceback
# import redis

import logging
logger = logging.getLogger('main')

from flask import Flask
import BCQ

# app = Flask(__name__)
# rd = redis.Redis(host="", port=)


# @app.route('/heartbeat')
# def heartbeat():
#     #
#     return
#
#
# @app.route('/state')
# def get_state():
#     return
#
#
# @app.route('/plan')
# def plan_action():
#     return


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
        policy_path = "ckpt/BCQ/control.pkl"
        self.policy = torch.load(policy_path)
        # policy = policy.to(device=0)
        self.plan_request = False

    def run(self):
        # app.run(host="0.0.0.0", port=5000)
        # 当捕获到thickener 的flask后运行
        while True:
            try:
                if self.plan_request:
                    logger.debug('Main Service: Receive planning request. Planning action...')
                    # state = flask_post['state'] # TODO:需要归一化
                    state = 0
                    action = self.policy.select_action(np.array(state))
                    print(action)

                    # TODO：发送生成的action to thickener control
                    # Send acion

                    # TODO: 将state-action对保存在数据库表中，方便后续BufferGenerate
                    # TODO：暂时储存两个表，一个作为历史数据，一个作为经验回访池（）
                    # replay_buffer = [state, action]
                    # replay_buffer.save(redis)

                    logger.debug('Main Service: Action planning over, send the new action.')
                logger.debug('Main Service: Plan Service loop')
            except Exception as e:
                traceback.print_exc()
                logger.warning('Main Service:' + 'Thickener-%s ' % self.th_id + 'Plan Service break: '+ str(e))

