from Plan_Threading import *
import logging
logger = logging.getLogger('main')


class Plan_Service(threading.Thread):

    def add_Planner(self, planner: Plan_Threading):
        self.threading_pooling[planner.planner_id] = planner
        planner.setDaemon(True)

    def del_Planner(self, planner_id: int):
        self.threading_pooling[planner_id].RUNNING = False
        del self.threading_pooling[planner_id]

    def __init__(self, threadID=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.RUNNING = True
        self.planner_msg = {}
        self.threading_pooling = {}
        self.Locking = threading.Lock()

    def start_all_Planners(self):
        for planner_id, planner_thread in self.threading_pooling.items():
            planner_thread.setDaemon(True)
            planner_thread.start()

    def join_all_Planners(self):
        for planner_id, planner_thread in self.threading_pooling.items():
            planner_thread.join()

    def run(self):
        self.start_all_Planners()
        self.join_all_Planners()

