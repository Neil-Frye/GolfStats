import logging
print("Checking log configuration")
logger = logging.getLogger()
print(f"Log level: {logger.level}")
handlers = logger.handlers
print(f"Number of handlers: {len(handlers)}")
for h in handlers:
    print(f"Handler: {type(h)}, level: {h.level}")

