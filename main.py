#!/usr/bin/python
# -*- coding:utf8 -*-

from time import sleep
import sys
import logging
import os
from utils import get_config_dict

from Plan_Service import Plan_Service
from Plan_Threading import Plan_Threading
from Train_Service import Train_Service
from Train_Threading import Train_Threading
from collections import defaultdict


def restart_plan_service():
    plan_service = Plan_Service()
    plan_service.add_Planner(
        planner=Plan_Threading(
            Service=plan_service,
            config=get_config_dict(f'Planner_Thickener1'))
    )

    plan_service.add_Planner(
        planner=Plan_Threading(
            Service=plan_service,
            config=get_config_dict(f'Planner_Thickener2'))
    )

    plan_service.setDaemon(True)
    return plan_service


def restart_train_service():
    train_service = Train_Service()
    train_service.add_Trainer(
        trainer=Train_Threading(
            Service=train_service,
            config=get_config_dict(f'Trainer_Thickener1'))
    )

    train_service.add_Trainer(
        trainer=Train_Threading(
            Service=train_service,
            config=get_config_dict(f'Trainer_Thickener2'))
    )

    train_service.setDaemon(True)
    return train_service


if __name__ == "__main__":

    logger = logging.getLogger("main")

    level = logging.DEBUG if sys.argv[-1].endswith('debug') else logging.INFO
    fh = logging.FileHandler("RL_model.log", encoding="utf-8", mode="a")
    formatter = logging.Formatter("%(asctime)s - %(name)s-%(levelname)s %(message)s")
    fh.setFormatter(formatter)
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fh)
    logger.setLevel(level=level)

    plan_service, train_service = restart_plan_service(), restart_train_service()
    plan_service.start()
    train_service.start()

    count_serv = defaultdict(int)
    while True:

        if not plan_service.is_alive():
            plan_service = restart_plan_service()
            plan_service.start()
            count_serv['plan'] += 1
            logger.error("{name} is not running. Restart for the {count} time ".format(
                name=plan_service.__class__.__name__, count=count_serv['plan']))

        if not train_service.is_alive():
            train_service = restart_train_service()
            train_service.start()
            count_serv['train'] += 1
            logger.error("{name} is not running. Restart for the {count} time ".format(
                name=train_service.__class__.__name__, count=count_serv['train']))

        sleep(60)



