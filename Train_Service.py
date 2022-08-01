from Train_Threading import *
import logging

logger = logging.getLogger('main')


class Train_Service(threading.Thread):

    def add_Trainer(self, trainer: Train_Threading):
        self.threading_pooling[trainer.trainer_id] = trainer
        trainer.setDaemon(True)

    def del_Trainer(self, trainer_id: int):
        self.threading_pooling[trainer_id].RUNNING = False
        del self.threading_pooling[trainer_id]

    def __init__(self, threadID=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.RUNNING = True
        self.trainer_msg = {}
        self.threading_pooling = {}
        self.Locking = threading.Lock()

    def start_all_Trainers(self):
        for trainer_id, trainer_thread in self.threading_pooling.items():
            trainer_thread.setDaemon(True)
            trainer_thread.start()

    def join_all_Trainers(self):
        for planner_id, planner_thread in self.threading_pooling.items():
            planner_thread.join()

    def run(self):
        self.start_all_Trainers()
        self.join_all_Trainers()
