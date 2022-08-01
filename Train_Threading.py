import threading
import torch
import os
import traceback
# import redis

import logging

logger = logging.getLogger('main')

from flask import Flask

# app = Flask(__name__)


# rd = redis.Redis(host="", port=)

# @app.route('/')
# def heartbeat():
#     #
#     return


# @app.route('/state')
# def


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

    def build_replay_buffer(self):  # TODO: 后续有时间的话可以指定构建变量的replay_buffer
        # TODO:从数据库中取（每隔一段时间用前10e3的数据作为replay_buffer）
        #
        #

        a = self.training_request
        replay_buffer = 0
        return replay_buffer

    def run(self):
        # app.run(host="0.0.0.0", port=5000)
        # 当捕获到thickener 的flask后运行
        while True:
            try:
                if self.training_request:
                    logger.debug('Main Service: Receive training request. Model Training...')
                    replay_buffer = self.build_replay_buffer()
                    pol_trains = self.policy.train(replay_buffer, iterations=int(self.eval_freq), batch_size=self.batch_size)
                    torch.save(self.policy, os.path.join('./', 'best.pth'))         # TODO:路径需要修改
                    logger.debug('Main Service: Model training is over')

                # TODO: 判断如果经验回访池增加了1000条新数据，则自动开始更新
                # elif len(new_data) > 1000:
                #     logger.debug('Main Service: Replay buffer pool is full, model updating...')
                #     replay_buffer = self.build_replay_buffer()
                #     pol_trains = self.policy.train(replay_buffer, iterations=int(self.eval_freq), batch_size=self.batch_size)
                #     torch.save(self.policy, os.path.join('./', 'best.pth'))  # TODO:路径需要修改
                #     logger.debug('Main Service: Model updating is over')

                logger.debug('Main Service: Train Service loop')
            except Exception as e:
                traceback.print_exc()
                logger.warning('Main Service:' + 'Thickener-%s ' % self.th_id + 'Train Service break: ' + str(e))

