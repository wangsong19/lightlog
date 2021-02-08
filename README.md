# lightlog

	Lite log module for multi-process or remote log server.

### Feature

	+ Log server has 3 ways to hanldle log record:
		a. local save by single process
		b. local save by multi-process
		c. remote save by single/multi-process
	+ Easy to use!

### Description
	
	Lock at module initial file `__init__.py`.

### Use

	Command it:
	``` bash
		setup setup.py install
	```

	``` python
		import lightlog

		## single process
		task_log = lightlog.get_logger(fname="task_log")
		# set level if need (default is INFO)
		# from logging import DEBUG
		# task_log.set_level(DEBUG)
		task_log.debug("------ task has done! -------")

		## multi-process
		from multiprocessing import Queue, Process
		# in main-process
		log_worker = lightlog.get_ready_log_worker()
		log_worker.start()
		log_worker.join()
		# in sub-process
		task_log = lightlog.get_logger(fname="task_log")
		task_log.info("------ new task has done! -------")

		## remote server to save log
		# set remote address and use multi-porcess then start it
		config_dict = {"address": ("192.168.9.99", 9939), "is_mp": True}
		lightlog.lightconfig.load(config_dict)
		lightlog.LogServer.run()
		# use it this server as usual
		task_log = lightlog.get_logger(fname="task_log")
		task_log.warn("------ remote new task has done! -------")
	```
