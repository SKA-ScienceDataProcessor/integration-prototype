# -*- coding: utf-8 -*-
"""Processing Controller Scheduler main function"""

from .scheduler import ProcessingBlockScheduler


if __name__ == '__main__':
    print("Starting Processing Controller!")
    ProcessingBlockScheduler().run()

